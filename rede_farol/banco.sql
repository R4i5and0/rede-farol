DROP DATABASE IF EXISTS rede_farol;
CREATE DATABASE rede_farol;
USE rede_farol;


CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL, 
    tipo_usuario ENUM('idoso', 'pai_mae', 'adolescente', 'outro', 'admin', 'usuario') NOT NULL
);

select * from Usuario;


CREATE TABLE Conteudo (
    id_conteudo INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL,  
    url_arquivo VARCHAR(255),             
    arquivo VARCHAR(255) NULL,            
    thumbnail VARCHAR(255) NULL,         
    url_recurso_adicional VARCHAR(255) NULL, 
    fonte VARCHAR(255),
    data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_admin INT NOT NULL,
    contagem_likes INT DEFAULT 0,
    FOREIGN KEY (id_admin) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);


select * from Conteudo;



CREATE TABLE Categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome_categoria VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO Categoria (nome_categoria) VALUES
('Segurança para Idosos'),
('Controle Parental'),
('Redes Sociais'),
('Phishing e Golpes'),
('Senhas Seguras'),
('Crianças Online');

CREATE TABLE Conteudo_Categoria (
    id_conteudo INT NOT NULL,
    id_categoria INT NOT NULL,
    PRIMARY KEY (id_conteudo, id_categoria),
    FOREIGN KEY (id_conteudo) REFERENCES Conteudo(id_conteudo) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria) ON DELETE CASCADE
);


CREATE TABLE Registro_Votos (
    id_usuario INT NOT NULL,
    id_conteudo INT NOT NULL,
    data_voto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_conteudo),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_conteudo) REFERENCES Conteudo(id_conteudo) ON DELETE CASCADE
);




CREATE TABLE Mural (
    id_mural INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_conteudo INT NULL,
    titulo VARCHAR(200) NOT NULL,
    comentario TEXT NOT NULL,
    avaliacao DECIMAL(3,2) NOT NULL, 
    data_postagem DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_funcionario INT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_conteudo) REFERENCES Conteudo(id_conteudo) ON DELETE SET NULL,
    FOREIGN KEY (id_funcionario) REFERENCES Usuario(id_usuario) ON DELETE SET NULL
);

CREATE TABLE Chatbot_Consulta (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE SET NULL
);


CREATE TABLE Diagnostico (
    id_diagnostico INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    data_realizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    
 
    score_senhas INT DEFAULT 0,
    score_phishing INT DEFAULT 0,
    score_social INT DEFAULT 0,
    score_dispositivos INT DEFAULT 0,
    
  
    score_geral INT DEFAULT 0,
    perfil_resultado VARCHAR(50), 

    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

