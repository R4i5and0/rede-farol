/* === ARQUIVO: static/js/main.js (VERSÃO FINAL COM MELHORIAS) === */

/**
 * (NOVO) Parser de YouTube Robusto
 */
function getYoutubeVideoId(url) {
    let videoId = null;
    try {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        if (match && match[2].length === 11) {
            videoId = match[2];
        }
    } catch (e) {
        console.warn("Não é um link de YouTube válido:", url);
    }
    return videoId;
}

/**
 * (CORRIGIDO) Função que cria o HTML do player de vídeo.
 * AGORA, ela toca o vídeo DENTRO da modal (com a capa)
 */
function renderVideo(data, basePath) {
    if (data.arquivo) {
        // É um vídeo local (upload)
        return `<video controls class="img-fluid"><source src="${basePath}${data.arquivo}" type="video/mp4">Seu navegador não suporta a tag de vídeo.</video>`;
    }

    if (data.url_arquivo) {
        // É um link (provavelmente YouTube)
        const videoId = getYoutubeVideoId(data.url_arquivo);

        if (videoId) {
            // (NOVO) É um vídeo do YouTube! Vamos mostrar a thumbnail bonita.
            const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
            const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;

            // (CORREÇÃO) O onclick é colocado no wrapper, garantindo que o clique na seta (play button) funcione.
            return `
                <div class="video-thumbnail-wrapper" onclick="this.innerHTML = '<div class=\'ratio ratio-16x9\'><iframe src=\'${embedUrl}\' title=\'YouTube video player\' frameborder=\'0\' allow=\'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\' allowfullscreen></iframe></div>';">
                    <img src="${thumbnailUrl}" class="img-fluid" alt="Capa do vídeo: ${data.titulo}">
                </div>
            `;
        }
    }
    // Se não for nem local nem YouTube, mostra o erro
    return '<p class="text-danger">Não foi possível carregar este vídeo.</p>';
}

/**
 * (CORRIGIDO) Função que cria o HTML do PDF (Preview Bonito)
 * AGORA, retorna APENAS a capa, sem links. O botão fica no renderConteudo.
 */
function renderPdfPreview(data, basePath) {
    const thumbnail = data.thumbnail
        ? `${basePath}${data.thumbnail}`
        : "https://placehold.co/1280x720/4a00e0/f0f0f0?text=PDF"; // Imagem padrão

    // CORREÇÃO: Removemos a sobreposição e o botão daqui.
    return `
        <div class="pdf-preview-card">
            <img src="${thumbnail}" class="img-fluid" alt="Prévia do PDF: ${data.titulo}">
        </div>
    `;
}

/**
 * (CORRIGIDO) Função que cria o HTML do player de ÁUDIO
 * Agora toca DENTRO do modal
 */
function renderAudio(data, basePath) {
    // Define o caminho (prioriza arquivo local, depois URL)
    const audioPath = data.arquivo ? `${basePath}${data.arquivo}` : data.url_arquivo;

    // Se não tiver caminho, mostra erro
    if (!audioPath) {
        return '<p class="text-danger">Não foi possível carregar este áudio.</p>';
    }

    // Retorna o player de áudio padrão do HTML5
    return `<audio controls class="w-100">
                <source src="${audioPath}" type="audio/mpeg">
                Seu navegador não suporta a tag de áudio.
            </audio>`;
}

function renderImagem(data, basePath) {
    // (CORRIGIDO) Se o 'Tipo' for Imagem, usa o 'arquivo' (principal)
    if (data.arquivo) {
        return `<img src="${basePath}${data.arquivo}" class="img-fluid" alt="${data.titulo}">`;
    }
    if (data.url_arquivo) {
        return `<img src="${data.url_arquivo}" class="img-fluid" alt="${data.titulo}">`;
    }
    return '<p class="text-danger">Não foi possível carregar esta imagem.</p>';
}

// ==================================================================
// == O "Cérebro" do Modal
// ==================================================================
const renderMap = {
    'video': renderVideo,
    'pdf': renderPdfPreview,
    'audio': renderAudio,
    'imagem': renderImagem,
    // (NOVO) Adiciona os 'tipos' principais dos combos
    'video_pdf': renderVideo,
    'video_audio': renderVideo,
    'pdf_audio': renderAudio, // <--- CORRIGIDO
};

/**
 * (CORREÇÃO FINAL) Função principal que decide o que mostrar na modal
 */
async function renderConteudo(data, modal) {
    // Pega TODOS os elementos da modal
    const titleEl = modal.querySelector('#conteudoModalLabel');
    const contentArea = modal.querySelector('#modal-content-area');
    const descEl = modal.querySelector('#modalDescricao');
    const fonteEl = modal.querySelector('#modalFonte');
    const expandLinkArea = modal.querySelector('#modal-expand-link');
    const mainLinkArea = modal.querySelector('#modal-main-link');
    const recursoAdicionalArea = modal.querySelector('#modal-recurso-adicional');

    // 1. Limpa tudo
    titleEl.textContent = data.titulo;
    descEl.textContent = data.descricao;
    fonteEl.textContent = data.fonte || 'Não informada';
    contentArea.innerHTML = '';
    expandLinkArea.innerHTML = '';
    mainLinkArea.innerHTML = '';
    recursoAdicionalArea.innerHTML = '';

    // 2. Define os caminhos
    const tipo = data.tipo.toLowerCase(); // Ex: "video_pdf"
    const urlExterna = data.url_arquivo;
    const arquivoLocal = data.arquivo;
    const arquivoAdicional = data.url_recurso_adicional;
    const basePath = '/static/uploads/';

    let contentHtml = '';

    // 3. (LÓGICA PRINCIPAL) Renderiza o conteúdo principal (Player/Capa)
    if (tipo in renderMap) {
        contentHtml = renderMap[tipo](data, basePath);
    } else if (tipo === 'link' || tipo === 'dica') {
        // Tipos que não têm player
    } else {
        contentHtml = '<p class="text-danger">Não foi possível carregar este conteúdo.</p>';
    }
    contentArea.innerHTML = contentHtml;

    // 4. Lógica do "Expandir" (YouTube)
    if (tipo.includes('video') && urlExterna && getYoutubeVideoId(urlExterna)) {
        // CORREÇÃO: Adicionada a classe expandir-link-visivel para estilo
        expandLinkArea.innerHTML = `
            <a href="${urlExterna}" target="_blank" title="Abrir em nova aba" class="expandir-link-visivel">
                <i class="fas fa-expand me-1"></i> Abrir no YouTube
            </a>
        `;
    }

    // 5. Lógica do BOTÃO PRINCIPAL (PDF, LINK ou DICA)
    if (tipo === 'pdf' || tipo === 'link' || tipo === 'dica' || tipo === 'imagem') {

        let path;
        let iconClass;
        let buttonText;

        // Determina o caminho e texto
        if (tipo === 'pdf') {
            path = arquivoLocal ? `${basePath}${arquivoLocal}` : urlExterna;
            iconClass = 'fas fa-file-pdf';
            buttonText = 'Baixar Cartilha';
        } else if (tipo === 'imagem') {
            path = arquivoLocal ? `${basePath}${arquivoLocal}` : urlExterna;
            iconClass = 'fas fa-eye';
            buttonText = 'Ver Imagem Completa';
        } else { // link ou dica
            path = urlExterna;
            iconClass = 'fas fa-external-link-alt';
            buttonText = 'Acessar Conteúdo';
        }

        if (path) {
            mainLinkArea.innerHTML = `
                <a href="${path}" target="_blank" class="btn btn-farol btn-lg">
                    <i class="${iconClass} me-2"></i> ${buttonText}
                </a>
            `;
        }

        // Se não houver caminho, a área de link principal fica vazia (sem erro)
    }

    // 6. (LÓGICA CORRIGIDA) Botão "Adicional"
    if (arquivoAdicional) {

        // Define o texto e o ícone com base no 'tipo'
        let iconClass = 'fas fa-book-open'; // Padrão (PDF/Cartilha)
        let buttonText = 'Baixar Cartilha';

        // 'video_audio' ou 'pdf_audio' usam o adicional para áudio
        if (tipo === 'video_audio' || tipo === 'pdf_audio') {
            iconClass = 'fas fa-file-audio';
            buttonText = 'Baixar Áudio';
        }

        recursoAdicionalArea.innerHTML = `
            <a href="${basePath}${arquivoAdicional}" target="_blank" class="btn btn-farol-secondary">
                <i class="${iconClass} me-2"></i> ${buttonText}
            </a>
        `;
    }
}

// ==================================================================
// == SEU CÓDIGO ORIGINAL (COM AS CORREÇÕES E ADIÇÕES)
// ==================================================================
document.addEventListener('DOMContentLoaded', function () {

    // --- LÓGICA DO CÉU ESTRELADO (MANTIDA) ---
    const canvas = document.getElementById('stars');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let stars = [];
        const colors = [
            '#FFFFFF', '#FFD700', '#ADD8E6', '#FF6347',
            '#DA70D6', '#2ebfe4', 'rgba(255, 218, 7, 0.8)'
        ];

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        for (let i = 0; i < 700; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1.5,
                alpha: Math.random() * 0.6 + 0.4,
                color: colors[Math.floor(Math.random() * colors.length)],
                dx: (Math.random() - 0.5) * 0.2,
                dy: (Math.random() - 0.5) * 0.2
            });
        }

        function drawStars() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let star of stars) {
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                ctx.fillStyle = star.color;
                ctx.globalAlpha = star.alpha;
                ctx.fill();
                ctx.globalAlpha = 1.0;

                star.x += star.dx;
                star.y += star.dy;

                if (star.x < 0 || star.x > canvas.width) star.dx *= -1;
                if (star.y < 0 || star.y > canvas.height) star.dy *= -1;
            }
            requestAnimationFrame(drawStars);
        }
        drawStars();
    } // Fim da lógica if (canvas)


    // ================================================================
    // ⭐ NOVO: LÓGICA DE ESTADO ATIVO PARA OS FILTROS DE CATEGORIA ⭐
    // ================================================================
    const filterButtons = document.querySelectorAll('.filter-bar a.btn');
    if (filterButtons.length > 0) {
        const urlParams = new URLSearchParams(window.location.search);
        // O ID da categoria ativa na URL (e.g., '1' em ?categoria=1)
        const activeCategory = urlParams.get('categoria');

        filterButtons.forEach(button => {
            const buttonUrl = new URL(button.href);
            const buttonParams = new URLSearchParams(buttonUrl.search);
            const buttonCategory = buttonParams.get('categoria');

            // 1. Caso do botão "Ver Todos" (não tem parâmetro 'categoria' no href)
            if (!buttonCategory) {
                // 'Ver Todos' está ativo se NÃO houver parâmetro 'categoria' na URL
                if (!activeCategory) {
                    button.classList.add('btn-farol-active');
                    button.classList.remove('btn-outline-light');
                }
            }
            // 2. Caso de um botão de categoria específica
            else if (activeCategory && buttonCategory === activeCategory) {
                // Categoria está ativa se o ID corresponder
                button.classList.add('btn-farol-active');
                button.classList.remove('btn-outline-light');
            }
        });
    }

    // --- LÓGICA DA MODAL DE CONTEÚDO (MANTIDA) ---
    const conteudoModal = document.getElementById('conteudoModal');
    if (conteudoModal) {

        // Evento que RODA o conteúdo (quando o modal ABRE)
        conteudoModal.addEventListener('show.bs.modal', async function (event) {
            const button = event.relatedTarget;
            const conteudoId = button.getAttribute('data-id');
            const modal = this;

            const titleEl = modal.querySelector('#conteudoModalLabel');
            const contentArea = modal.querySelector('#modal-content-area');
            const descEl = modal.querySelector('#modalDescricao');
            const fonteEl = modal.querySelector('#modalFonte');

            titleEl.textContent = 'Carregando...';
            descEl.textContent = '';
            fonteEl.textContent = '';
            // (NOVO) Loader "bonito"
            contentArea.innerHTML = `
                <div class="modal-loader">
                    <i class="fas fa-satellite-dish fa-spin"></i>
                    <p>Buscando sinal...</p>
                </div>
            `;

            try {
                const response = await fetch(`/api/conteudo/${conteudoId}`);
                if (!response.ok) throw new Error('Falha ao buscar dados.');
                const data = await response.json();

                // (NOVO) Chama a função refatorada
                await renderConteudo(data, modal);

            } catch (error) {
                console.error('Erro:', error);
                titleEl.textContent = 'Erro';
                contentArea.innerHTML = '<p class="text-danger text-center">Não foi possível carregar o conteúdo.</p>';
            }
        });

        // (CORRIGIDO) O Bug do Vídeo Tocando (Evento de Fechamento)
        conteudoModal.addEventListener('hidden.bs.modal', function (event) {
            const contentArea = document.getElementById('modal-content-area');

            // Limpa as áreas dinâmicas para parar players de vídeo/áudio
            if (contentArea) contentArea.innerHTML = ''; // Destrói o player e para o som

            // Limpa os outros campos
            document.getElementById('conteudoModalLabel').innerText = 'Carregando...';
            document.getElementById('modalDescricao').innerText = '';
            document.getElementById('modalFonte').innerText = '';

            // Limpa as áreas de botões
            document.getElementById('modal-recurso-adicional').innerHTML = '';
            document.getElementById('modal-external-link').innerHTML = '';
            document.getElementById('modal-expand-link').innerHTML = ''; // Corrigida a variável
            document.getElementById('modal-main-link').innerHTML = '';
        });

    } // Fim da lógica if (conteudoModal)

}); // Fim do DOMContentLoaded


function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const icon = passwordField.nextElementSibling;

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordField.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// ===================================================================
// ⭐ FUNCIONALIDADE #4: RANQUEAMENTO DE CONTEÚDOS (VOTAÇÃO/LIKES) ⭐
// ===================================================================

document.addEventListener('DOMContentLoaded', function () {
    const conteudoModal = document.getElementById('conteudoModal');
    const contentArea = document.getElementById('modal-content-area');

    conteudoModal.addEventListener('hidden.bs.modal', function () {
        contentArea.innerHTML = '';
        document.getElementById('conteudoModalLabel').innerText = 'Carregando...';
        document.getElementById('modalDescricao').innerText = '';
        document.getElementById('modalFonte').innerText = '';
        document.getElementById('modal-recurso-adicional').innerHTML = '';
        document.getElementById('modal-external-link').innerHTML = '';
    });

    // VOTAÇÃO COM DESFAZER + FEEDBACK VISUAL
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        const conteudoId = button.getAttribute('data-id');
        const countElement = document.getElementById(`count-${conteudoId}`);

        // Marca como votado se já foi (opcional, para estado inicial)
        // Você pode remover isso se quiser que o botão comece sem marcação
        // Mas é útil se o usuário já votou antes de carregar a página

        button.addEventListener('click', async function () {
            if (button.disabled) return;

            button.disabled = true;
            button.style.transform = 'scale(1.1)';
            button.style.boxShadow = '0 0 15px rgba(255, 107, 107, 0.7)';

            try {
                const response = await fetch(`/api/conteudo/${conteudoId}/votar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (response.ok) {
                    // Atualiza a contagem
                    countElement.textContent = data.new_count;

                    // Toggle: se estava votado, remove; senão, adiciona
                    if (button.classList.contains('voted')) {
                        button.classList.remove('voted');
                        button.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
                        button.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                        button.querySelector('i').style.color = 'white';

                        // Efeito de brilho amarelo ao desfazer
                        button.style.boxShadow = '0 0 15px rgba(255, 215, 0, 0.7)';
                        setTimeout(() => {
                            button.style.boxShadow = 'none';
                        }, 1000);

                    } else {
                        button.classList.add('voted');
                        button.style.backgroundColor = 'rgba(255, 107, 107, 0.2)';
                        button.style.borderColor = 'rgba(255, 107, 107, 0.4)';
                        button.querySelector('i').style.color = '#ff6b6b';

                        // Efeito de brilho amarelo ao votar
                        button.style.boxShadow = '0 0 15px rgba(255, 215, 0, 0.7)';
                        setTimeout(() => {
                            button.style.boxShadow = 'none';
                        }, 1000);
                    }

                    // Feedback visual suave
                    setTimeout(() => {
                        button.style.transform = 'scale(1)';
                    }, 300);

                } else {
                    alert('Erro ao processar o voto. Tente novamente.');
                }

            } catch (error) {
                console.error('Erro de conexão ao votar:', error);
                alert('Erro de conexão. Tente novamente mais tarde.');
            } finally {
                button.disabled = false;
            }
        });
    });
});

// ===================================================================
// ⭐ FUNCIONALIDADE #5: ANALISADOR DE LINKS (USADO EM chatbot.html) ⭐
// ===================================================================
const analiseForm = document.getElementById('analiseLinkForm');
const linkInput = document.getElementById('linkInput');
const resultadoDiv = document.getElementById('resultadoAnalise');

if (analiseForm) {
    analiseForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const url = linkInput.value.trim();

        // Feedback visual
        resultadoDiv.innerHTML = '<p class="text-info">Analisando...</p>';

        try {
            const response = await fetch('/api/analisar-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();
            let classeCor = 'text-success';

            if (data.risco.includes('Alto')) {
                classeCor = 'text-danger';
            } else if (data.risco.includes('Médio')) {
                classeCor = 'text-warning';
            }

            resultadoDiv.innerHTML = `
                    <p class="${classeCor} fw-bold mb-0">${data.risco}</p>
                    <p class="text-white-50 mt-0 small">${data.mensagem}</p>
                `;

        } catch (error) {
            console.error('Erro na análise de link:', error);
            resultadoDiv.innerHTML = '<p class="text-danger">Erro de conexão com o servidor.</p>';
        }
    });
}






// ===================================================================
// ⭐ NOVO: LÓGICA DE DETECÇÃO DE PÁGINA PARA ESTILO (NO-GLASS) ⭐
// ===================================================================

(function () {
    const body = document.body;
    const path = window.location.pathname;

    // Páginas que NÃO devem ter o efeito de caixa opaca (Glassmorphism) no Hero
    if (path === '/' || path.includes('/dashboard_usuario')) {
        body.classList.add('no-glass');
    }
})();