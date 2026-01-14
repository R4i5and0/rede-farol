# 💡 Rede Farol – Segurança Digital para Todos

> ✨ **“Sua luz na segurança digital. Protegendo quem mais precisa com informação, tecnologia e acolhimento.”** 

<div align="center">
  <img src="https://img.shields.io/badge/Status-Concluído_(4º_Semestre)-blue?style=flat&logo=github" alt="Status"/>
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-Framework-black?style=flat&logo=flask" alt="Flask"/>
  <img src="https://img.shields.io/badge/MySQL-Banco_de_Dados-orange?style=flat&logo=mysql" alt="MySQL"/>
  <img src="https://img.shields.io/badge/Google_Gemini-API-8E75B2?style=flat&logo=google" alt="Gemini AI"/>
</div>

---

## 📄 Sobre o Projeto

O **Rede Farol** é uma plataforma web desenvolvida durante o **3º Semestre** do curso de Análise e Desenvolvimento de Sistemas. O objetivo foi criar uma solução com **impacto social real**: proteger públicos vulneráveis (idosos, crianças e leigos) contra golpes digitais.

A aplicação combina IA Generativa (Google Gemini) para oferecer acolhimento ao usuário, criptografia avançada para garantir a segurança dos dados e ferramentas práticas para identificar riscos. O chat funciona como um guia, trazendo clareza e orientação ao usuário.

---

## 💡 Aprendizados e Evolução Técnica (Post-Mortem)

> *Este projeto representa um marco importante na minha jornada de aprendizado.*  

Ao revisitar este código hoje, com a experiência adquirida em arquitetura de software, identifico pontos cruciais de melhoria que aplicaria em uma versão 2.0:  

- **Arquitetura Monolítica:** O projeto concentra a lógica em um arquivo principal. Hoje, eu utilizaria o padrão **MVC** ou **Blueprints** do Flask para separar responsabilidades.  
- **Separação de Estilos (CSS):** Na versão inicial, o CSS estava centralizado. Agora, eu criaria arquivos de estilo separados para cada página, garantindo maior organização e manutenção.  
- **ORM vs SQL Puro:** Utilizei queries SQL diretas. Atualmente, optaria por um ORM como **SQLAlchemy** para maior segurança e abstração.  
- **Segurança:** A implementação do **Flask-Bcrypt** foi um passo fundamental para entender a importância de não salvar senhas em texto puro, elevando o nível de segurança da aplicação.  

### 📈 Evolução Técnica

- 😢**Código Antigo:** Ao revisar, percebo limitações e escolhas que hoje não faria.  
- 😊**Orgulho:** Manter o projeto original serve como registro da minha **evolução técnica**.  
---

## 📸 Tour pela Aplicação

### 1. 🏠 Página Principal (Deslogado)

A home acolhe o usuário com uma mensagem de boas-vindas e segmenta o conteúdo por público-alvo:

- **Idosos e Leigos**: Prevenção contra phishing, golpes de falso suporte e WhatsApp.  
- **Crianças e Adolescentes**: Alertas sobre perigos em plataformas digitais e cyberbullying.  
- **Pais e Responsáveis**: Ferramentas de controle parental e dicas de diálogo.  

> ✅ **Modal de Informação**: Ao clicar em qualquer card, abre um modal com dicas práticas e linguagem simples.

![Home](./assets/home.gif)

---

### 2. 🔐 Login e Cadastro

Tela de login com validação de e-mail e senha. Para novos usuários, há link para cadastro.

> ✅ **Cadastro**: Solicita nome completo, e-mail, senha e confirmação de senha. Senhas são criptografadas com bcrypt.

![Login e Cadastro](./assets/login-cadastro.gif)

---

### 3. 📌 Footer e ⚠️ Confirmação de Saída

O “footer“ da aplicação contém ícones que, ao serem clicados, **redirecionam para suas respectivas páginas**. 
Ao clicar em “Sair”, aparece um modal de confirmação para evitar saídas acidentais.

![Fim](./assets/fim.gif)

---

### 4. 🧩 Teste de Risco Digital

Questionário que avalia o perfil de segurança do usuário com base em hábitos digitais (senhas, phishing, redes sociais).

> ✅ **Resultado**: Classifica o usuário em 3 perfis: **Cauteloso**, **Cuidado** ou **Alvo Fácil**.

![Teste 1](./assets/Teste-1.gif)  
![Teste 2](./assets/Teste-2.gif)

---

### 5. 📊 Dashboard Logado (Com Gráficos Interativos)

Após o login, o usuário vê seu painel personalizado:

- **Gráfico de Pontos Fortes e Fracos**: Mostra desempenho em 4 categorias (Senhas, Detecção de Golpes, Redes Sociais, Dispositivos).
- **Ferramentas Exclusivas**: Chatbot Tira-Dúvidas e Curadoria de Conteúdo.
- **Avaliações Recentes**: Lista das últimas avaliações feitas pelo usuário, com opções de editar/excluir.

![Dashboard Logado](./assets/dash-login.gif)

---

### 6. 📊 Dashboard Sem Login

Versão pública do dashboard, com carrossel informativo, ranking dos golpes mais comuns e acesso às ferramentas principais.

![Dashboard Sem Login](./assets/dash-sem-login.gif)

---

### 7. 🎥 Curadoria de Conteúdo (Logado)

Catálogo de vídeos, PDFs e guias organizados por categoria (Controle Parental, Phishing, etc.). Os conteúdos podem ser:

A plataforma oferece diferentes formatos de acesso:
- **Vídeos locais (upload do PC)**: Reproduzidos em modal, permitindo assistir diretamente na aplicação.  
- **Vídeos do YouTube**: Redirecionam para o YouTube, respeitando os direitos autorais.  
- **Cartilhas em PDF**: Disponíveis para download através do botão **“Baixar Cartilha”**.  
- **Ranking dos Mais Populares**: Exibe os conteúdos mais bem avaliados pelos usuários.

> ℹ️ **Direitos autorais**: Todo conteúdo exibido inclui fonte de origem visível. Vídeos do YouTube redirecionam diretamente ao canal original. Materiais próprios foram produzidos com base em referências públicas e educacionais.

![Conteúdo](./assets/Conteúdo.gif)  
![Conteúdo com PDF/Vídeo](./assets/Conteúdo-pdf-video.gif)

---

### 8. 🤖 Chatbot Híbrido com Google Gemini

Assistente de segurança com interface amigável:

- Campo de texto para perguntas livres.
- Dicas prontas clicáveis ao lado (ex: “Como ativar verificação em 2 etapas?”).
- Respostas contextualizadas com foco em segurança digital.

> ✅ A IA não deixa de responder por falta de conhecimento, mas porque foi **programada para atuar exclusivamente em temas de segurança**.  

Quando recebe uma pergunta fora desse escopo, ela redireciona para tópicos relacionados.  
Exemplo: *Olá! Agradeço a sua pergunta, mas eu sou um assistente focado 100% em segurança digital. Minha especialidade é proteger você e sua família online.
Não consigo ajudar com perguntas sobre vida pessoal, mas posso te ajudar a criar uma senha forte e segura agora mesmo! Que tal?”*  

![Chatbot](./assets/chat.gif)

---

### 9. 🔍 Analisador de Links

Ferramenta integrada ao chatbot que analisa URLs suspeitas e retorna um diagnóstico imediato de confiabilidade.

![Analisar Link](./assets/Analisar-link.gif)

---

### 10. 📝 Avaliações (CRUD)

Usuários logados podem avaliar conteúdos com estrelas e comentários. As avaliações aparecem no mural e podem ser editadas ou excluídas pelo próprio usuário.

> ✅ **Admin**: Pode ver e excluir todas as avaliações.

![Avaliação 1](./assets/Avaliacao-1.gif)  
![Avaliação 2](./assets/Avaliacao-2.gif)

---

### 11. 👑 Painel Administrativo

Acesso exclusivo para administradores. Permite:

- Gerenciar todos os conteúdos (visualizar, editar, excluir).
- Adicionar novo conteúdo via formulário completo (título, descrição, tipo, fonte, categorias, uploads).

> ✅ **Upload de Conteúdo**: Suporta vídeos locais, PDFs, thumbnails e links externos (YouTube).

![Painel Admin](./assets/painel-admin.gif)  
![Modal Admin](./assets/modal-admin.gif)

---

### 12. 🗃️ Banco de Dados Criptografado

Todas as senhas são armazenadas com hash via **bcrypt**. O banco segue estrutura relacional segura com chaves estrangeiras.

![Banco Criptografado](./assets/Banco-cript.gif)

---

## 🛠️ Tecnologias Utilizadas

* **Back-End:** Python, Flask  
* **Front-End:** HTML5, CSS3, Bootstrap 5, JavaScript (interações dinâmicas)  
* **Segurança:** Flask-Bcrypt (hash de senhas), chaves secretas via `.env`  
* **Banco de Dados:** MySQL (via conector `flask_mysqldb`)  
* **Inteligência Artificial:** Google Generative AI (Gemini) SDK  
* **Upload de Arquivos:** Suporte a imagens, vídeos, áudios e PDFs  

---

# 💡 Rede Farol - Segurança Digital

---

## 🎥 Demonstração
![Home](./assets/home.gif)
![Chat](./assets/chat.gif)

---

## ⚙️ Como Rodar o Projeto Localmente

### 1. Pré-requisitos
* **Python** instalado em sua máquina.
* **Servidor MySQL** ativo (XAMPP, WAMP ou similar).

### 2. Configure o Banco de Dados
* Abra o **phpMyAdmin** em: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
* Crie um banco de dados chamado `rede_farol`.
* Importe o script SQL: [`banco.sql`](./banco.sql)

### 3. Obtenha sua chave de API (Google Gemini)
Para que o chatbot funcione, você precisa de uma chave própria:
1. Acesse o [Google AI Studio](https://aistudio.google.com/).
2. Faça login e clique em **"Get API key"**.
3. Clique em **"Create API key in new project"** e copie o código.

### 4. Configure as Variáveis de Ambiente
Crie um arquivo chamado `.env` na raiz da pasta `rede_farol` e adicione:

```env
GOOGLE_API_KEY=SUA_CHAVE_AQUI
SECRET_KEY=uma_chave_qualquer
```

### 5. Crie e ative o ambiente virtual
```env
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 6. Instale as dependências
```env
pip install flask flask-mysqldb bcrypt python-dotenv pymysql requests google-generativeai
```

### 7. Execute a aplicação
```env
python app.py
```

#### ✅ Acesse em: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

⚠️ **Importante:** Evite espaços no caminho da pasta!
* ✅ **Use:** `C:\Rede_Farol\rede_farol`
* ❌ **Não use:** `C:\Meus Projetos\Rede Farol`

---

### 📅 Status do Projeto
**Finalizado em agosto de 2025**

Desenvolvido com 💜 por **Raissa da Anunciação**
