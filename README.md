# 💡 Rede Farol - Segurança Digital para Todos

> "Sua luz na segurança digital. Protegendo quem mais precisa com informação, tecnologia e acolhimento."

![Status](https://img.shields.io/badge/Status-Concluído_(3º_Semestre)-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-black)
![MySQL](https://img.shields.io/badge/MySQL-Banco_de_Dados-orange)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-API-8E75B2)

---

## 📄 Sobre o Projeto

O **Rede Farol** é uma plataforma web desenvolvida durante o **3º Semestre** do curso de Análise e Desenvolvimento de Sistemas. O objetivo foi criar uma solução com **impacto social real**: proteger públicos vulneráveis (idosos, crianças e leigos) contra golpes digitais.

A aplicação utiliza IA Generativa (Google Gemini) para acolher o usuário, criptografia forte para proteção de dados e ferramentas práticas para identificar riscos.

---

## 💡 Aprendizados e Evolução Técnica (Post-Mortem)

> *Este projeto representa um marco importante na minha jornada de aprendizado.*

Ao revisitar este código hoje, com a experiência adquirida em arquitetura de software, identifico pontos cruciais de melhoria que aplicaria em uma versão 2.0:

* **Arquitetura Monolítica:** O projeto concentra a lógica em um arquivo principal. Hoje, eu utilizaria o padrão **MVC** ou **Blueprints** do Flask para separar responsabilidades.
* **ORM vs SQL Puro:** Utilizei queries SQL diretas. Atualmente, optaria por um ORM como **SQLAlchemy** para maior segurança e abstração.
* **Segurança:** A implementação do **Flask-Bcrypt** foi um passo fundamental para entender a importância de não salvar senhas em texto puro, elevando o nível de segurança da aplicação.

Manter o projeto original aqui serve para documentar minha **evolução técnica** de estudante para desenvolvedora profissional.

---

## 📸 Tour pela Aplicação

### 1. 🏠 Página Principal (Deslogado)

A home acolhe o usuário com uma mensagem de boas-vindas e segmenta o conteúdo por público-alvo:

- **Idosos e Leigos**: Prevenção contra phishing, golpes de falso suporte e WhatsApp.
- **Crianças e Adolescentes**: Alertas sobre perigos em Discord/Telegram e cyberbullying.
- **Pais e Responsáveis**: Ferramentas de controle parental e dicas de diálogo.

> ✅ **Modal de Informação**: Ao clicar em qualquer card, abre um modal com dicas práticas e linguagem simples.

![Home](./assets/home.gif)

---

### 2. 🔐 Login e Cadastro

Tela de login com validação de e-mail e senha. Para novos usuários, há link para cadastro.

> ✅ **Cadastro**: Solicita nome completo, e-mail, senha e confirmação de senha. Senhas são criptografadas com bcrypt.

![Login e Cadastro](./assets/login-cadastro.gif)

---

### 3. ⚠️ Confirmação de Saída

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

- **Vídeos locais**: Reproduzidos em modal com botão “Baixar Cartilha” (PDF).
- **Vídeos do YouTube**: Redireciona diretamente para o YouTube (respeitando direitos autorais).
- **Ranking dos Mais Populares**: Mostra os conteúdos mais avaliados.

![Conteúdo](./assets/Conteúdo.gif)  
![Conteúdo com PDF/Vídeo](./assets/Conteúdo-pdf-video.gif)

---

### 8. 🤖 Chatbot Híbrido com Google Gemini

Assistente de segurança com interface amigável:

- Campo de texto para perguntas livres.
- Dicas prontas clicáveis ao lado (ex: “Como ativar verificação em 2 etapas?”).
- Analisador de links: Cole uma URL suspeita e receba um diagnóstico imediato.

> ✅ **Resposta contextualizada**: Se a IA não souber responder, ela redireciona para temas relacionados.

![Chatbot](./assets/chat.gif)

---

### 9. 📝 Avaliações (CRUD)

Usuários logados podem avaliar conteúdos com estrelas e comentários. As avaliações aparecem no mural e podem ser editadas ou excluídas pelo próprio usuário.

> ✅ **Admin**: Pode ver e excluir todas as avaliações.

![Avaliação 1](./assets/Avaliacao-1.gif)  
![Avaliação 2](./assets/Avaliacao-2.gif)

---

### 10. 👑 Painel Administrativo

Acesso exclusivo para administradores. Permite:

- Gerenciar todos os conteúdos (visualizar, editar, excluir).
- Adicionar novo conteúdo via formulário completo (título, descrição, tipo, fonte, categorias, uploads).

> ✅ **Upload de Conteúdo**: Suporta vídeos locais, PDFs, thumbnails e links externos (YouTube).

![Painel Admin](./assets/painel-admin.gif)  
![Modal Admin](./assets/modal-admin.gif)

---

### 11. 🔍 Analisador de Links

Ferramenta integrada ao chatbot que analisa URLs suspeitas e retorna um diagnóstico de confiabilidade.

![Analisar Link](./assets/Analisar-link.gif)

---

### 12. 🗃️ Banco de Dados Criptografado

Todas as senhas são armazenadas com hash via **bcrypt**. O banco segue estrutura relacional segura com chaves estrangeiras.

![Banco Criptografado](./assets/Banco-cript.gif)

---

## 🛠️ Tecnologias Utilizadas

* **Back-End:** Python, Flask.
* **Front-End:** HTML5, CSS3, Bootstrap 5, JavaScript (interações dinâmicas).
* **Segurança:** Flask-Bcrypt (hash de senhas), chaves secretas via `.env`.
* **Banco de Dados:** MySQL (via conector `flask_mysqldb`).
* **Inteligência Artificial:** Google Generative AI (Gemini) SDK.
* **Upload de Arquivos:** Suporte a imagens, vídeos, áudios e PDFs.

---

## ⚙️ Como Rodar o Projeto Localmente

### Pré-requisitos
- Python instalado.
- Servidor MySQL rodando (ex: XAMPP, WAMP, MariaDB, etc.).

### Passo a Passo

1. **Clone o repositório**
   ```powershell
   git clone https://github.com/R4i5and0/rede-farol.git
   cd rede-farol
