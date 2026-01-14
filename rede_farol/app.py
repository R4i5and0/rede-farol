# =============================================================================
# IMPORTAÇÕES PRINCIPAIS E CONFIGURAÇÃO
# =============================================================================
import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import bcrypt
import os
from werkzeug.utils import secure_filename
from functools import wraps
import re # Necessário para a API de Analisador de Links
import uuid 
from datetime import datetime 

# NOVAS IMPORTAÇÕES PARA O CHATBOT HÍBRIDO (IA)
from dotenv import load_dotenv 
import google.generativeai as genai 

# CONFIGURAÇÃO DA APLICAÇÃO
app = Flask(__name__)

# Chave secreta
app.secret_key = os.getenv('SECRET_KEY', 'chave-secreta-muito-segura-123')

# Configuração de upload de arquivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'mp3', 'webm', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'rede_farol'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

# Inicializa extensões
mysql = MySQL(app)

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =============================================================================
# CONFIGURAÇÃO DA IA GENERATIVA (CHATBOT NÍVEL 2)
# =============================================================================
load_dotenv() 

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }
    safety_settings = [
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    MODELO_IA_NOME = "models/gemini-flash-latest" 
    
    gemini_model = genai.GenerativeModel(model_name=MODELO_IA_NOME,
                                     generation_config=generation_config,
                                     safety_settings=safety_settings)
    
    print("✅ Modelo de IA Gemini carregado com sucesso.")
except Exception as e:
    print(f"❌ ERRO ao carregar a API do Google Gemini: {e}")
    print("   Verifique se a sua GOOGLE_API_KEY está correta no arquivo .env")
    gemini_model = None 

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_file_if_exists(filename):
    """Função segura para deletar um arquivo do UPLOAD_FOLDER."""
    if not filename:
        return 
        
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f"Erro ao deletar arquivo {filename}: {e}") 

def save_secure_file(file):
    """Gera um nome de arquivo unico e o salva."""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        novo_nome = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], novo_nome)
        file.save(file_path)
        return novo_nome
    return None

# =============================================================================
# DECORADORES DE AUTENTICAÇÃO
# =============================================================================
def requer_login(f):
    """Exige que o usuário esteja logado para acessar a rota."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Você precisa fazer login para acessar esta página.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def requer_admin(f):
    """Exige que o usuário seja admin para acessar a rota."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'): 
            flash('Você precisa fazer login primeiro.', 'danger')
            return redirect(url_for('login'))
        if session.get('tipo_usuario') != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# ROTAS DE API (Ranqueamento e Análise de Link)
# =============================================================================

@app.route('/conteudo/<int:id_conteudo>')
@requer_login
def detalhes_conteudo(id_conteudo):
    """Exibe os detalhes de um conteúdo específico."""
    cur = mysql.connection.cursor()
    
    # Busca o conteúdo
    cur.execute("SELECT * FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    conteudo = cur.fetchone()
    
    if not conteudo:
        flash('Conteúdo não encontrado.', 'danger')
        return redirect(url_for('listar_conteudos'))
    
    # Busca as categorias do conteúdo
    cur.execute("""
        SELECT c.nome_categoria 
        FROM Categoria c 
        JOIN Conteudo_Categoria cc ON c.id_categoria = cc.id_categoria 
        WHERE cc.id_conteudo = %s
    """, (id_conteudo,))
    categorias = cur.fetchall()
    
    cur.close()
    
    return render_template('detalhes_conteudo.html', conteudo=conteudo, categorias=categorias)
# =============================================================================


@app.route('/api/conteudo/<int:id_conteudo>/votar', methods=['POST'])
@requer_login
def votar_conteudo(id_conteudo):
    id_usuario = session.get('id_usuario')
    
    try:
        cur = mysql.connection.cursor()
        
        # 1. VERIFICA se o usuário já votou (SEM selecionar id_voto)
        cur.execute("SELECT 1 FROM Registro_Votos WHERE id_usuario = %s AND id_conteudo = %s", (id_usuario, id_conteudo))
        voto_existente = cur.fetchone()
        
        if voto_existente:
            # --- DESFAZER VOTO ---
            cur.execute("DELETE FROM Registro_Votos WHERE id_usuario = %s AND id_conteudo = %s", (id_usuario, id_conteudo))
            
            # Diminui a contagem
            cur.execute("UPDATE Conteudo SET contagem_likes = contagem_likes - 1 WHERE id_conteudo = %s", (id_conteudo,))
            
            # Pega nova contagem
            cur.execute("SELECT contagem_likes FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
            nova_contagem = cur.fetchone()['contagem_likes']
            
            mysql.connection.commit()
            cur.close()
            
            return jsonify({
                'success': True,
                'new_count': nova_contagem,
                'message': 'Voto removido com sucesso.'
            }), 200
            
        else:
            # --- ADICIONAR VOTO ---
            cur.execute("INSERT INTO Registro_Votos (id_usuario, id_conteudo) VALUES (%s, %s)", (id_usuario, id_conteudo))
            
            # Incrementa a contagem
            cur.execute("UPDATE Conteudo SET contagem_likes = contagem_likes + 1 WHERE id_conteudo = %s", (id_conteudo,))
            
            # Pega nova contagem
            cur.execute("SELECT contagem_likes FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
            nova_contagem = cur.fetchone()['contagem_likes']
            
            mysql.connection.commit()
            cur.close()
            
            return jsonify({
                'success': True,
                'new_count': nova_contagem,
                'message': 'Voto registrado com sucesso.'
            }), 200
            
    except Exception as e:
        mysql.connection.rollback()
        print(f"Erro ao votar/desfazer: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao processar voto.'}), 500
    
    
from urllib.parse import urlparse
import re

@app.route('/api/analisar-link', methods=['POST'])
def analisar_link():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'risco': 'URL não fornecida', 'mensagem': 'Por favor, cole um link para análise.'}), 200

    if not url.lower().startswith('http://') and not url.lower().startswith('https://'):
        url = 'https://' + url

    try:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc.lower().replace('www.', '') # Remove 'www.' para facilitar
    except Exception as e:
        return jsonify({'success': False, 'risco': 'URL Inválida', 'mensagem': 'O formato do link parece ser inválido.'}), 200

    # REGRA 1: Risco Médio (Conexão não segura)
    if parsed_url.scheme != 'https':
        return jsonify({
            'success': True, 'url': url,
            'risco': "Médio (Conexão Não Criptografada)",
            'mensagem': "CUIDADO! O link não usa HTTPS (cadeado seguro). Sua conexão pode ser interceptada."
        }), 200

    # ✅ --- NOVA REGRA 2: LISTA DE CONFIANÇA (SAFELIST) --- ✅
    # Verifica se o domínio é CONHECIDO e SEGURO.
    dominios_confiaveis = [
        # Gigantes de Tech
        'google.com', 'youtube.com', 'microsoft.com', 'apple.com',
        'instagram.com', 'facebook.com', 'whatsapp.com', 'linkedin.com',
        'github.com', 'gemini.google.com',
        
        # Governo e Notícia
        'gov.br', 'jus.br', 'leg.br', 'g1.globo.com', 'uol.com.br',
        
        # Bancos (Domínios Reais)
        'itau.com.br', 'bradesco.com.br', 'santander.com.br', 'caixa.gov.br', 'bb.com.br', 'nubank.com.br'
    ]

    for dominio in dominios_confiaveis:
        # Verifica se o netloc é EXATAMENTE o domínio ou se TERMINA com ".dominio"
        # Ex: 'gemini.google.com' termina com '.google.com'
        if netloc == dominio or netloc.endswith('.' + dominio):
            return jsonify({
                'success': True, 'url': url,
                'risco': "Baixo (Link Confiável)",
                'mensagem': f"Este link pertence ao domínio '{dominio}', que é um site conhecido e seguro."
            }), 200
    # --- FIM DA NOVA REGRA ---

    # REGRA 3: Risco Alto (TLDs suspeitas - as extensões do domínio)
    tlds_suspeitos = ['xyz', 'online', 'link', 'club', 'top', 'info', 'ru', 'biz', 'icu']
    
    domain_parts = netloc.split('.')
    if len(domain_parts) > 1:
        tld = domain_parts[-1].lower()
        if tld in tlds_suspeitos:
            return jsonify({
                'success': True, 'url': url,
                'risco': "Alto (Domínio Suspeito)",
                'mensagem': f"AVISO VERMELHO! O domínio usa a extensão '.{tld}', que é muito comum em golpes de phishing e spam."
            }), 200


    # REGRA 3: Risco Alto (Falsificação de Subdomínio - O SEU TESTE!)
    if len(domain_parts) > 2: # Ex: 'subdominio.dominio.com' (3 partes)
        # Domínio principal: 'novasenha.xyz'
        main_domain = f"{domain_parts[-2]}.{domain_parts[-1]}"
        # Subdomínio: 'www.banco-itau.com-seguranca'
        sub_domain = netloc.replace(main_domain, '').rstrip('.').lower()
        
        # Palavras-chave que indicam imitação
        marcas_imitadas = [
            'banco', 'itau', 'bradesco', 'santander', 'caixa', 'bb.com', 'nubank',
            'microsoft', 'google', 'apple', 'facebook', 'instagram', 'netflix', 'amazon',
            'receita.fazenda', 'gov.br', 'login', 'seguranca', 'account', 'security',
            'atualizar', 'premio', 'pix'
        ]
        
        for marca in marcas_imitadas:
            if marca in sub_domain:
                return jsonify({
                    'success': True, 'url': url,
                    'risco': "Alto (Risco de Falsificação)",
                    'mensagem': f"AVISO VERMELHO! O link parece ser '{main_domain}' (um site desconhecido), mas está tentando se passar por '{marca}' no subdomínio. Isso é uma tática de phishing!"
                }), 200

    # Se passou por todas as regras, é neutro
    return jsonify({
        'success': True,
        'url': url,
        'risco': "Análise Neutra", # Corrigido para bater com a sua imagem
        'mensagem': "Não conseguimos identificar riscos óbvios, mas sempre tenha cuidado com links desconhecidos."
    }), 200
    
    
    
# =============================================================================
# ROTAS DO DIAGNÓSTICO (O PROCESSO)
# =============================================================================

@app.route('/diagnostico', methods=['GET', 'POST'])
@requer_login
def diagnostico():
    if request.method == 'POST':
        # --- 1. LÓGICA DE CÁLCULO (AJUSTADA PARA O FORMULÁRIO REAL) ---
        score_senhas = 0
        score_phishing = 0
        score_social = 0
        score_dispositivos = 0
        
        p_senha_tam = request.form.get('senha_tamanho')
        if p_senha_tam == 'forte':
            score_senhas += 50
        elif p_senha_tam == 'medio':
            score_senhas += 25
        # valor 'fraco' → 0 pontos (implícito)
        
        p_senha_reuso = request.form.get('senha_reuso')
        if p_senha_reuso == 'nao':
            score_senhas += 50
        # 'sim' → 0 pontos
        
        p_phishing_link = request.form.get('phishing_link')
        if p_phishing_link == 'verifico':
            score_phishing += 50
        # 'clico' → 0 pontos
        
        p_phishing_promo = request.form.get('phishing_promo')
        if p_phishing_promo == 'desconfio':
            score_phishing += 50
        # 'confio' → 0 pontos
        
        p_social_priv = request.form.get('social_privacidade')
        if p_social_priv == 'fechado':
            score_social += 50
        # 'todos' → 0 pontos (não há opção 'amigos')
        
        p_social_expo = request.form.get('social_exposicao')
        if p_social_expo == 'pouco':
            score_social += 50
        # 'muito' → 0 pontos
        
        p_wifi = request.form.get('wifi_publico')
        if p_wifi == 'nunca':
            score_dispositivos += 50
        # 'sempre' → 0 pontos (não há opção 'vpn')
        
        p_antivirus = request.form.get('antivirus')
        if p_antivirus == 'sim':
            score_dispositivos += 50
        # 'nao' → 0 pontos

        score_geral = int((score_senhas + score_phishing + score_social + score_dispositivos) / 4)
        
        perfil_resultado = "Alvo Fácil"
        if score_geral >= 80:
            perfil_resultado = "Guardião Digital" 
        elif score_geral >= 50:
            perfil_resultado = "Cauteloso" 
        
        # --- 2. SALVAR NO BANCO ---
        id_usuario = session['id_usuario']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Diagnostico 
            (id_usuario, score_senhas, score_phishing, score_social, score_dispositivos, score_geral, perfil_resultado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_usuario, score_senhas, score_phishing, score_social, score_dispositivos, score_geral, perfil_resultado))
        
        mysql.connection.commit()
        cur.close()

        # --- 3. MOSTRAR RESULTADO ---
        return render_template('diagnostico_resultado.html', 
                               perfil=perfil_resultado, 
                               score=score_geral)

    # --- AO CARREGAR O FORMULÁRIO (GET) ---
    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM Diagnostico 
        WHERE id_usuario = %s 
        ORDER BY data_realizacao DESC LIMIT 1
    """, (id_usuario,))
    ultimo_diagnostico = cur.fetchone()
    cur.close()

    return render_template('diagnostico_form.html', ultimo_diagnostico=ultimo_diagnostico)


@app.route('/diagnostico/resultado')
@requer_login
def ver_ultimo_diagnostico():
    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM Diagnostico 
        WHERE id_usuario = %s 
        ORDER BY data_realizacao DESC LIMIT 1
    """, (id_usuario,))
    resultado = cur.fetchone()
    cur.close()
    if resultado:
        return render_template('diagnostico_resultado.html',
                               perfil=resultado['perfil_resultado'],
                               score=resultado['score_geral'])
    else:
        flash('Você ainda não fez nenhum diagnóstico.', 'info')
        return redirect(url_for('diagnostico'))
# =============================================================================
# ROTAS PRINCIPAIS (PÚBLICAS)
# =============================================================================
@app.route('/dashboard_usuario')
def dashboard_usuario():
    """Dashboard de ameaças e RESULTADOS do usuário."""
    
    # Dados padrão (para quem não logou ou não fez teste)
    dados_diagnostico = None 
    avaliacoes_recentes = None

    if session.get('logged_in'):
        id_usuario = session['id_usuario']
        cur = mysql.connection.cursor()
        
        # 1. Busca as avaliações (Isso você já tinha)
        cur.execute("""
            SELECT m.*, c.titulo AS titulo_conteudo 
            FROM Mural m 
            LEFT JOIN Conteudo c ON m.id_conteudo = c.id_conteudo 
            WHERE m.id_usuario = %s
            ORDER BY m.data_postagem DESC LIMIT 3
        """, (id_usuario,))
        avaliacoes_recentes = cur.fetchall()
        
        # 2. NOVO: Busca o ÚLTIMO diagnóstico feito pelo usuário
        cur.execute("""
            SELECT * FROM Diagnostico 
            WHERE id_usuario = %s 
            ORDER BY data_realizacao DESC LIMIT 1
        """, (id_usuario,))
        dados_diagnostico = cur.fetchone()
        
        cur.close()
    
    return render_template('dashboard_usuario.html', 
                           avaliacoes_recentes=avaliacoes_recentes,
                           dados_diagnostico=dados_diagnostico) # <--- Passando os dados novos!

# =============================================================================
# ROTAS DE CONTEÚDO (PROTEGIDAS)
# =============================================================================

@app.route('/conteudos')
@requer_login
def listar_conteudos():
    """
    Lista todos os conteúdos (ou filtra por categoria),
    ordenado pelo Ranqueamento (Likes) PRIMEIRO.
    """
    cur = mysql.connection.cursor()
    
    # 1. Busca as categorias PRIMEIRO (para os botões)
    cur.execute("SELECT * FROM Categoria ORDER BY nome_categoria")
    todas_as_categorias = cur.fetchall()
    
    # 2. Verifica se o usuário clicou em um filtro de categoria
    categoria_filtrada_id = request.args.get('categoria')

    if categoria_filtrada_id:
        # 3a. Se filtrou, faz um SQL com JOIN, ORDENADO POR LIKES
        cur.execute(
            """
            SELECT c.* FROM Conteudo c
            JOIN Conteudo_Categoria cc ON c.id_conteudo = cc.id_conteudo
            WHERE cc.id_categoria = %s
            ORDER BY c.contagem_likes DESC, c.data_publicacao DESC
            """, (categoria_filtrada_id,)
        )
    else:
        # 3b. Se não filtrou, busca tudo, ORDENADO PELO RANQUEAMENTO (LIKES)
        cur.execute("SELECT * FROM Conteudo ORDER BY contagem_likes DESC, data_publicacao DESC")
    
    conteudos = cur.fetchall()

    # 4. Busca os 5 conteúdos mais votados (para o gráfico)
    cur.execute("SELECT * FROM Conteudo ORDER BY contagem_likes DESC LIMIT 5")
    conteudos_populares = cur.fetchall()
    
    cur.close()
    
    # 5. Envia AMBAS as listas para o template
    return render_template('conteudos.html', 
                            conteudos=conteudos, 
                            todas_as_categorias=todas_as_categorias,
                            conteudos_populares=conteudos_populares)  # <-- Nova variável


@app.route('/api/conteudo/<int:id_conteudo>')
@requer_login
def get_conteudo_details(id_conteudo):
    """Retorna detalhes de um conteúdo específico (para modal)."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    conteudo = cur.fetchone()
    cur.close()
    if conteudo:
        return jsonify(conteudo)
    return jsonify({'error': 'Conteúdo não encontrado'}), 404

# ... (Sua outra API 'latest-threats' está aqui, tudo certo) ...
@app.route('/api/latest-threats')
def latest_threats():
    return jsonify([
        {'title': 'Golpe do Falso Suporte Técnico', 'url': '#', 'date': '14/10/2025', 'description': '...'},
        {'title': 'Falso Prêmio no WhatsApp', 'url': '#', 'date': '13/10/2025', 'description': '...'},
        {'title': 'Login Falso de Banco', 'url': '#', 'date': '12/10/2025', 'description': '...'}
    ])

# =============================================================================
# ROTAS DO CHATBOT HÍBRIDO (NÍVEL 2)
# =============================================================================

def get_bot_response(user_message):
    """O "Cérebro" HÍBRIDO do Chatbot."""
    msg = user_message.lower().strip() 

    # --- NÍVEL 1: CÉREBRO RÁPIDO (Regras) ---
    if msg in ['oi', 'ola', 'olá', 'bom dia', 'boa tarde', 'boa noite']:
        nome_usuario = session.get('nome', '').split(' ')[0] 
        return f"Olá, {nome_usuario}! Como posso te ajudar a ficar mais seguro(a) hoje?"
    if msg == 'ajuda':
        return "Eu posso te ajudar com dúvidas sobre golpes, phishing, senhas, e como ativar proteções. Tente me perguntar: 'como ativar duas etapas' ou 'o que é malware?'"
    if ('duas etapas' in msg or '2fa' in msg) and 'whatsapp' in msg:
        return "Ótima pergunta! Para ativar no WhatsApp:\n1. Vá em Configurações (ou Ajustes).\n2. Clique em 'Conta'.\n3. Clique em 'Confirmação em duas etapas'.\n4. Ative e crie um PIN de 6 dígitos (e não esqueça de adicionar um e-mail de recuperação!)."
    if 'o que é phishing' in msg:
        return "Phishing (ou 'pescaria digital') é quando golpistas enviam links falsos fingindo ser um banco, loja ou o governo. Eles tentam te enganar para você digitar sua senha ou dados do cartão em um site falso. Desconfie sempre de e-mails com senso de 'urgência'."
    if 'o que é malware' in msg or 'o que é virus' in msg:
        return "Malware é um programa malicioso que infecta seu PC ou celular. Pode ser um 'Vírus' (que se espalha) ou um 'Ransomware' (que sequestra seus arquivos). A melhor proteção é ter um bom antivírus (como o próprio Microsoft Defender) e NUNCA baixar arquivos de sites piratas ou e-mails desconhecidos."
    
    # (NOVO) Bônus: Resposta do MRT atualizada conforme sua solicitação
    if 'mrt' in msg or ('ferramenta' in msg and 'windows' in msg and 'cmd' in msg):
        return (
            "Ótima pergunta! Você está falando do 'MRT', a Ferramenta de Remoção de Software Mal-intencionado do Windows.\n\n"
            "**O que é?**\n"
            "Pense nela como um 'detetive' que o próprio Windows usa para procurar e remover os tipos mais comuns de vírus graves.\n\n"
            "**Como usar (o jeito fácil):**\n"
            "1. Pressione as teclas **Windows + R** juntas (para abrir a janelinha 'Executar').\n"
            "2. Digite **mrt** e aperte Enter.\n"
            "3. Uma tela azul vai abrir. Siga as instruções e escolha 'Exame Rápido' para começar."
        )

    if 'obrigado' in msg or 'obrigada' in msg or 'tchau' in msg or 'até mais' in msg:
        return "De nada! Fico feliz em ajudar. Se cuide e fique seguro(a)!"
    
    # --- NÍVEL 2: CÉREBRO INTELIGENTE (IA Generativa) ---
    
    if not gemini_model:
        return "Desculpe, minha conexão com a IA está offline. Não consigo responder perguntas complexas agora. Tente perguntar sobre temas básicos como 'phishing' ou 'malware'."

    try:
        system_prompt = (
            "Você é um assistente de segurança do site Rede Farol. "
            "Sua missão é ajudar pessoas leigas (idosos, pais, adolescentes) a se protegerem online. "
            "Seu tom de voz deve ser **extremamente simples, didático, paciente e acolhedor**. "
            "Sempre que possível, dê respostas em formato de **passo-a-passo** ou lista.\n\n"
            
            "REGRAS IMPORTANTES:\n"
            "1. RECOMENDAÇÕES DE SOFTWARE: Ao recomendar antivírus, priorize o Microsoft Defender (nativo do Windows) e opções pagas de alta qualidade como Kaspersky ou Bitdefender. **NUNCA, JAMAIS, recomende antivírus gratuitos como Avast ou AVG**, pois eles têm problemas de privacidade. Apenas mencione os bons.\n"
            "2. NÍVEL TÉCNICO: Se o usuário pedir um método técnico (como 'via CMD', 'powershell' ou 'terminal'), **FORNEÇA esse método técnico**. Mas, logo depois, ofereça também o método mais fácil (via interface gráfica/cliques) como a 'opção mais simples'.\n"
            "3. FOCO: Responda APENAS perguntas sobre segurança digital, golpes, proteção de dados, privacidade, antivírus, controle parental e tópicos relacionados.\n"
            "4. RECUSA: Se a pergunta for sobre qualquer outro assunto (como política, esportes, saúde, matemática, fofoca, etc.), recuse educadamente e diga: "
            "'Desculpe, mas eu sou um assistente focado 100% em segurança digital. Não consigo ajudar com esse assunto, mas posso te ajudar a criar uma senha forte!'."
        )
        
        convo = gemini_model.start_chat(history=[
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Entendido. Estou pronto para ajudar com segurança digital de forma simples e acolhedora, priorizando as recomendações corretas e fornecendo ajuda técnica (como CMD) quando solicitado."]}
        ])
        
        convo.send_message(user_message)
        
        return convo.last.text

    except Exception as e:
        print(f"❌ ERRO ao chamar a API do Gemini: {e}")
        return "Desculpe, tive um problema ao tentar processar sua pergunta com a IA. Tente perguntar de forma mais simples."


@app.route('/chatbot')
@requer_login 
def chatbot_page():
    """Renderiza a página do chatbot."""
    return render_template('chatbot.html')


@app.route('/api/chatbot-ask', methods=['POST'])
@requer_login 
def chatbot_ask():
    """
    A "Ponte" (API). Recebe a pergunta do usuário,
    busca a resposta no "Cérebro HÍBRIDO" e salva no Banco de Dados.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Mensagem inválida.'}), 400

    pergunta = data['message']
    
    # 1. Pega a resposta do "Cérebro Híbrido"
    resposta = get_bot_response(pergunta)
    
    # 2. Salva a consulta no Banco de Dados (Sua tabela!)
    try:
        id_usuario = session.get('id_usuario')
        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO Chatbot_Consulta (id_usuario, pergunta, resposta)
            VALUES (%s, %s, %s)
            """,
            (id_usuario, pergunta, resposta)
        )
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"❌ Erro ao salvar log do chat no banco de dados: {e}")
    
    # 3. Retorna a resposta para a Página
    return jsonify({'answer': resposta})


# =============================================================================
# ROTAS DE ADMIN (PROTEGIDAS E REFATORADAS)
# =============================================================================

@app.route('/admin/dashboard')
@requer_admin
def admin_dashboard():
    """Exibe o painel de administração com a lista de conteúdos."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Conteudo ORDER BY data_publicacao DESC")
    conteudos = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html', conteudos=conteudos)


# =============================================================================
# ROTAS DE CONTEÚDO (CRUD)
# =============================================================================

@app.route('/admin/adicionar', methods=['GET', 'POST'])
@requer_admin
def adicionar_conteudo():
    
    cur = mysql.connection.cursor() 
    
    if request.method == 'POST':
        # --- LÓGICA DE SALVAR (POST) ---
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo = request.form['tipo']
        fonte = request.form['fonte']
        id_admin = session['id_usuario']
        
        categorias_selecionadas = request.form.getlist('categorias')
        
        # Inicia variáveis de arquivo como Nulas
        thumbnail_nome = None
        arquivo_nome = None
        arquivo_adicional_nome = None
        
        # Pega a URL primeiro
        url_arquivo = request.form.get('url_arquivo', '') 
        
        # (LÓGICA INTELIGENTE 1) Processa Arquivo Principal
        if 'arquivo' in request.files and request.files['arquivo'].filename != '':
            file = request.files['arquivo']
            if allowed_file(file.filename):
                arquivo_nome = save_secure_file(file) 
                url_arquivo = '' 
        
        # (LÓGICA INTELIGENTE 2) Processa Arquivo Adicional
        if 'arquivo_adicional' in request.files and request.files['arquivo_adicional'].filename != '':
            file = request.files['arquivo_adicional']
            if allowed_file(file.filename):
                arquivo_adicional_nome = save_secure_file(file) 

        # Processa Thumbnail
        if 'thumbnail' in request.files and request.files['thumbnail'].filename != '':
            file = request.files['thumbnail']
            if allowed_file(file.filename):
                thumbnail_nome = save_secure_file(file) 

        # Insere o conteúdo principal
        cur.execute(
            """
            INSERT INTO Conteudo(titulo, descricao, tipo, url_arquivo, fonte, id_admin, thumbnail, arquivo, url_recurso_adicional) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (titulo, descricao, tipo, url_arquivo, fonte, id_admin, thumbnail_nome, arquivo_nome, arquivo_adicional_nome)
        )
        
        # Pega o ID do conteúdo que acabamos de criar
        id_novo_conteudo = cur.lastrowid
        
        # Insere as categorias na tabela de relacionamento
        for id_cat in categorias_selecionadas:
            cur.execute("INSERT INTO Conteudo_Categoria (id_conteudo, id_categoria) VALUES (%s, %s)", (id_novo_conteudo, id_cat))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Conteúdo adicionado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # --- LÓGICA DE MOSTRAR A PÁGINA (GET) ---
    cur.execute("SELECT * FROM Categoria ORDER BY nome_categoria")
    todas_as_categorias = cur.fetchall()
    cur.close()
    
    return render_template('admin/adicionar_conteudo.html', 
                            todas_as_categorias=todas_as_categorias)


@app.route('/admin/editar/<int:id_conteudo>', methods=['GET', 'POST'])
@requer_admin
def editar_conteudo(id_conteudo):
    
    cur = mysql.connection.cursor()
    
    # 1. Buscar o conteúdo principal (para saber os nomes dos arquivos antigos)
    cur.execute("SELECT * FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    conteudo = cur.fetchone()

    if not conteudo:
        cur.close() 
        flash('Conteúdo não encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # 2. Buscar TODAS as categorias para os checkboxes
    cur.execute("SELECT * FROM Categoria ORDER BY nome_categoria")
    todas_as_categorias = cur.fetchall()

    # 3. Buscar os IDs das categorias que este conteúdo JÁ POSSUI
    cur.execute("SELECT id_categoria FROM Conteudo_Categoria WHERE id_conteudo = %s", (id_conteudo,))
    categorias_marcadas_raw = cur.fetchall() 
    
    # 4. Transformar a lista para o template (ex: [1, 5, 8])
    categorias_do_conteudo = [item['id_categoria'] for item in categorias_marcadas_raw]
    

    # --- LÓGICA DE SALVAR (POST) ---
    if request.method == 'POST':
        # Pega dados do formulário
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo = request.form['tipo']
        fonte = request.form['fonte']
        categorias_selecionadas = request.form.getlist('categorias')
        
        # Pega nomes dos arquivos ANTIGOS (para poder deletá-los)
        thumb_antigo = conteudo['thumbnail']
        arquivo_antigo = conteudo['arquivo']
        adicional_antigo = conteudo['url_recurso_adicional']
        
        # Define nomes ATUAIS com base nos antigos (eles podem não mudar)
        thumb_atual = thumb_antigo
        arquivo_atual = arquivo_antigo
        adicional_atual = adicional_antigo
        
        # Pega a URL
        url_arquivo = request.form.get('url_arquivo', '')

        # (LÓGICA INTELIGENTE 1) Processa Thumbnail
        if 'thumbnail' in request.files and request.files['thumbnail'].filename != '':
            file = request.files['thumbnail']
            if allowed_file(file.filename):
                thumb_atual = save_secure_file(file) 
                delete_file_if_exists(thumb_antigo) 

        # (LÓGICA INTELIGENTE 2) Processa Arquivo Principal
        if 'arquivo' in request.files and request.files['arquivo'].filename != '':
            # Se um NOVO arquivo foi enviado, ele tem prioridade
            file = request.files['arquivo']
            if allowed_file(file.filename):
                arquivo_atual = save_secure_file(file) 
                delete_file_if_exists(arquivo_antigo) 
                url_arquivo = '' # Apaga a URL, pois o arquivo local manda
        elif url_arquivo != '' and arquivo_antigo:
            # Se uma URL foi digitada e existia um arquivo antigo, apaga o arquivo antigo
            delete_file_if_exists(arquivo_antigo) 
            arquivo_atual = None 
            
        # (LÓGICA INTELIGENTE 3) Processa Arquivo Adicional
        if 'arquivo_adicional' in request.files and request.files['arquivo_adicional'].filename != '':
            file = request.files['arquivo_adicional']
            if allowed_file(file.filename):
                adicional_atual = save_secure_file(file) 
                delete_file_if_exists(adicional_antigo) 

        # --- ATUALIZA O BANCO DE DADOS ---
        
        # 1. Atualiza a tabela principal 'Conteudo'
        cur.execute(
            """
            UPDATE Conteudo 
            SET titulo=%s, descricao=%s, tipo=%s, url_arquivo=%s, 
                fonte=%s, thumbnail=%s, arquivo=%s, url_recurso_adicional=%s
            WHERE id_conteudo=%s
            """,
            (titulo, descricao, tipo, url_arquivo, fonte, 
             thumb_atual, arquivo_atual, adicional_atual, id_conteudo)
        )

        # 2. Atualiza a tabela de relacionamento 'Conteudo_Categoria'
        cur.execute("DELETE FROM Conteudo_Categoria WHERE id_conteudo = %s", (id_conteudo,))
        for id_cat in categorias_selecionadas:
            cur.execute("INSERT INTO Conteudo_Categoria (id_conteudo, id_categoria) VALUES (%s, %s)", (id_conteudo, id_cat))
        
        # 3. Salva tudo (commit) e fecha
        mysql.connection.commit()
        cur.close()
        
        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    # --- LÓGICA DE MOSTRAR A PÁGINA (GET) ---
    cur.close() 
    
    return render_template('admin/editar_conteudo.html', 
                            conteudo=conteudo,
                            todas_as_categorias=todas_as_categorias,
                            categorias_do_conteudo=categorias_do_conteudo)

@app.route('/admin/excluir/<int:id_conteudo>', methods=['POST'])
@requer_admin
def excluir_conteudo(id_conteudo):
    """Exclui um conteúdo E remove TODOS os arquivos associados."""
    cur = mysql.connection.cursor()
    
    # 1. Pega o nome de TODOS os arquivos antes de deletar do DB
    cur.execute("SELECT thumbnail, arquivo, url_recurso_adicional FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    item = cur.fetchone()
    
    # 2. Deleta a linha do banco (o 'ON DELETE CASCADE' vai limpar as categorias)
    cur.execute("DELETE FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    mysql.connection.commit()
    cur.close()
    
    # 3. Agora, deleta os arquivos do servidor
    if item:
        delete_file_if_exists(item['thumbnail'])
        delete_file_if_exists(item['arquivo'])
        delete_file_if_exists(item['url_recurso_adicional'])
    
    flash('Conteúdo excluído com sucesso.', 'success')
    return redirect(url_for('admin_dashboard'))

# =============================================================================
# ROTAS DE AUTENTICAÇÃO
# =============================================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastro de novo usuário."""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register'))
            
        senha_bytes = senha.encode('utf-8')
        hash_senha = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        hash_senha_str = hash_senha.decode('utf-8')
        
        try:
            cur = mysql.connection.cursor()
            # NOVO: Tipo de usuário padronizado para 'usuario'
            cur.execute("INSERT INTO Usuario(nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)", (nome, email, hash_senha_str, 'usuario'))
            mysql.connection.commit()
            cur.close()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Erro: e-mail já cadastrado.', 'danger')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário (redireciona para admin ou home)."""
    if request.method == 'POST':
        email = request.form['email']
        senha_candidata = request.form['senha'].encode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Usuario WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        
        if usuario and bcrypt.checkpw(senha_candidata, usuario['senha'].encode('utf-8')):
            session['logged_in'] = True
            session['id_usuario'] = usuario['id_usuario']
            session['nome'] = usuario['nome']
            session['tipo_usuario'] = usuario['tipo_usuario']
            
            if usuario['tipo_usuario'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
                
        flash('E-mail ou senha incorretos.', 'danger')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Encerra a sessão do usuário."""
    session.clear()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('home'))

# =============================================================================
# ROTA HOME (ESSENCIAL PARA O BASE.HTML NÃO QUEBRAR)
# =============================================================================
@app.route('/')
def home():
    """Página inicial."""
    return render_template('home.html')

# =============================================================================
# ROTAS DO MURAL
# =============================================================================

@app.route('/mural')
@requer_login
def mural():
    """Exibe todas as avaliações para todos os usuários logados."""
    cur = mysql.connection.cursor()
    
    # Todos os usuários logados veem TODAS as avaliações
    cur.execute("""
        SELECT m.*, u.nome AS nome_usuario, c.titulo AS titulo_conteudo, c.thumbnail AS thumbnail_conteudo
        FROM Mural m 
        JOIN Usuario u ON m.id_usuario = u.id_usuario 
        LEFT JOIN Conteudo c ON m.id_conteudo = c.id_conteudo 
        ORDER BY m.data_postagem DESC
    """)
    
    posts = cur.fetchall()
    cur.close()
    
    return render_template('mural.html', posts=posts)



@app.route('/mural/novo/<int:id_conteudo>', methods=['GET', 'POST'])
@requer_login
def criar_post_mural(id_conteudo):
    if request.method == 'POST':
        titulo = request.form['titulo']
        comentario = request.form['comentario']
        avaliacao = float(request.form['avaliacao'])
        id_usuario = session['id_usuario']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO Mural (id_usuario, id_conteudo, titulo, comentario, avaliacao) VALUES (%s, %s, %s, %s, %s)",
            (id_usuario, id_conteudo, titulo, comentario, avaliacao)
        )
        mysql.connection.commit()
        cur.close()
        
        flash('Avaliação enviada com sucesso!', 'success')
        return redirect(url_for('mural'))
    
    # Busca o conteúdo completo para mostrar no formulário
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Conteudo WHERE id_conteudo = %s", (id_conteudo,))
    conteudo = cur.fetchone()
    cur.close()

    if not conteudo:
        flash('Conteúdo não encontrado.', 'danger')
        return redirect(url_for('listar_conteudos'))

    return render_template('mural_form.html', conteudo=conteudo, id_conteudo=id_conteudo)




@app.route('/mural/editar/<int:id_post>', methods=['GET', 'POST'])
@requer_login
def editar_post_mural(id_post):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM Mural WHERE id_mural = %s", (id_post,))
    post = cur.fetchone()
    
    if not post:
        flash('Post não encontrado.', 'danger')
        return redirect(url_for('mural'))

    # Verifica se o usuário é o dono ou se é admin
    if session['id_usuario'] != post['id_usuario'] and session['tipo_usuario'] != 'admin':
        flash('Você não tem permissão para editar este post.', 'danger')
        return redirect(url_for('mural'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        comentario = request.form['comentario']
        avaliacao = float(request.form['avaliacao'])  # ← MUDANÇA AQUI!
        id_funcionario = session['id_usuario'] # Quem editou (opcional)

        cur.execute(
            "UPDATE Mural SET titulo=%s, comentario=%s, avaliacao=%s, id_funcionario=%s WHERE id_mural = %s",
            (titulo, comentario, avaliacao, id_funcionario, id_post)
        )
        mysql.connection.commit()
        cur.close()
        
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('mural'))  # ← VOLTA PARA O MURAL

    cur.close()
    return render_template('mural_form.html', post=post)



@app.route('/mural/excluir/<int:id_post>', methods=['POST'])
@requer_login  # Qualquer usuário logado pode excluir (mas a lógica de permissão está no backend)
def excluir_post_mural(id_post):
    """Exclui um post do mural."""
    cur = mysql.connection.cursor()
    
    # Busca o post para verificar o dono
    cur.execute("SELECT id_usuario FROM Mural WHERE id_mural = %s", (id_post,))
    post = cur.fetchone()
    
    if not post:
        flash('Post não encontrado.', 'danger')
        cur.close()
        return redirect(url_for('mural'))

    # Verifica se o usuário é o dono ou se é admin
    if session['id_usuario'] != post['id_usuario'] and session['tipo_usuario'] != 'admin':
        flash('Você não tem permissão para excluir este post.', 'danger')
        cur.close()
        return redirect(url_for('mural'))

    cur.execute("DELETE FROM Mural WHERE id_mural = %s", (id_post,))
    mysql.connection.commit()
    cur.close()
    
    flash('Post excluído com sucesso.', 'success')
    return redirect(url_for('mural'))  # 👈 Volta para o mural

# =============================================================================
# EXECUÇÃO
# =============================================================================
if __name__ == '__main__':
    app.run(debug=True)