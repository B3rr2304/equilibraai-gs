import psycopg2
import os

DB_FILE = 'meu_banco.db'

def criar_e_popular_banco():
    """
    Cria a estrutura completa do banco de dados e popula as
    tabelas de lookup (mestras) com dados de exemplo.
    """
    
    # Apaga o banco antigo, se existir, para começar do zero
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"♻️ Banco de dados '{DB_FILE}' antigo removido.")

    print(f"🎉 Iniciando criação do banco de dados '{DB_FILE}'...")
    conn = psycopg2.connect(DB_FILE)
    cursor = conn.cursor()
    
    # --- 1. CRIAÇÃO DAS TABELAS ---
    
    # Tabela de níveis de experiência
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nivel_experiencia (
        nivel_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        peso REAL NOT NULL
    )
    ''')
    
    # Tabela de categorias de skills
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categoria_skill (
        categoria_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('hard_skill', 'soft_skill')), 
        descricao TEXT
    )
    ''')
    
    # Tabela de skills individuais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill (
        skill_id INTEGER PRIMARY KEY,
        categoria_id INTEGER NOT NULL,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        FOREIGN KEY (categoria_id) REFERENCES categoria_skill(categoria_id)
    )
    ''')
    
    # Tabela de colaboradores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS colaborador (
        colaborador_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        data_cadastro DATE DEFAULT CURRENT_DATE
    )
    ''')
    
    # Tabela de relação colaborador-skill (Tabela "Fato")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS colaborador_skill (
        colaborador_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        nivel_experiencia_id INTEGER NOT NULL,
        confianca REAL,
        data_avaliacao DATE,
        PRIMARY KEY (colaborador_id, skill_id),
        FOREIGN KEY (colaborador_id) REFERENCES colaborador(colaborador_id),
        FOREIGN KEY (skill_id) REFERENCES skill(skill_id),
        FOREIGN KEY (nivel_experiencia_id) REFERENCES nivel_experiencia(nivel_id)
    )
    ''')
    
    # Tabela de interesses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interesse (
        interesse_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT
    )
    ''')
    
    # Tabela de relação colaborador-interesse (A "PONTE" QUE FALTAVA)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS colaborador_interesse (
        colaborador_id INTEGER NOT NULL,
        interesse_id INTEGER NOT NULL,
        PRIMARY KEY (colaborador_id, interesse_id),
        FOREIGN KEY (colaborador_id) REFERENCES colaborador(colaborador_id),
        FOREIGN KEY (interesse_id) REFERENCES interesse(interesse_id)
    )
    ''')
    
    print("✅ Todas as 7 tabelas foram criadas com sucesso.")

    # --- 2. POPULAÇÃO DAS TABELAS DE LOOKUP ---
    
    print("📊 Populando tabelas de lookup (mestras)...")
    
    try:
        # Níveis de Experiência
        niveis = [
            (1, 'Iniciante', 'Conhecimento básico', 0.3),
            (2, 'Intermediário', 'Conhecimento prático', 0.6),
            (3, 'Avançado', 'Domínio do assunto', 0.8),
            (4, 'Especialista', 'Referência no assunto', 1.0)
        ]
        cursor.executemany("INSERT INTO nivel_experiencia (nivel_id, nome, descricao, peso) VALUES (?, ?, ?, ?)", niveis)
        
        # Categorias de Skill
        categorias = [
            (1, 'Desenvolvimento Backend', 'hard_skill', 'Tecnologias de servidor'),
            (2, 'Desenvolvimento Frontend', 'hard_skill', 'Tecnologias de cliente'),
            (3, 'Data Science', 'hard_skill', 'Análise e modelos de dados'),
            (4, 'DevOps', 'hard_skill', 'Infraestrutura e CI/CD'),
            (5, 'Habilidades Comportamentais', 'soft_skill', 'Competências interpessoais')
        ]
        cursor.executemany("INSERT INTO categoria_skill (categoria_id, nome, tipo, descricao) VALUES (?, ?, ?, ?)", categorias)
        
        # Skills (Hard Skills) - IDs de 1 a 20
        hard_skills = [
            (1, 1, 'Python', 'Linguagem de programação'),
            (2, 1, 'Flask', 'Micro-framework web Python'),
            (3, 1, 'SQL', 'Linguagem de consulta a banco de dados'),
            (4, 3, 'Pandas', 'Biblioteca para manipulação de dados'),
            (5, 3, 'Scikit-learn', 'Biblioteca de machine learning'),
            (6, 1, 'Java', 'Linguagem de programação'),
            (7, 1, 'Spring Boot', 'Framework para Java'),
            (8, 2, 'JavaScript', 'Linguagem de script para web'),
            (9, 2, 'React', 'Biblioteca frontend'),
            (10, 2, 'Angular', 'Framework frontend'),
            (11, 4, 'Docker', 'Plataforma de containers'),
            (12, 4, 'Kubernetes', 'Orquestrador de containers'),
            (13, 4, 'AWS', 'Amazon Web Services'),
            (14, 1, 'Node.js', 'Ambiente de execução JavaScript no backend'),
            (15, 3, 'TensorFlow', 'Biblioteca para deep learning'),
            (16, 3, 'PyTorch', 'Biblioteca para deep learning'),
            (17, 1, 'C#', 'Linguagem de programação Microsoft'),
            (18, 1, '.NET Core', 'Framework Microsoft'),
            (19, 4, 'Git', 'Sistema de controle de versão'),
            (20, 2, 'CSS', 'Linguagem de estilização')
        ]
        # Adiciona mais 30 skills genéricas para bater com os 50 IDs do CSV
        for i in range(21, 51):
            hard_skills.append((i, 1, f'Skill Genérica {i}', 'Skill técnica placeholder'))
            
        cursor.executemany("INSERT INTO skill (skill_id, categoria_id, nome, descricao) VALUES (?, ?, ?, ?)", hard_skills)
        
        # Skills (Soft Skills) - IDs de 51 a 60
        soft_skills = [
            (51, 5, 'Resolução de Problemas', 'Capacidade de encontrar soluções'),
            (52, 5, 'Foco', 'Capacidade de concentração'),
            (53, 5, 'Pensamento Analítico', 'Analisar informações e tirar conclusões'),
            (54, 5, 'Proatividade', 'Tomar iniciativa'),
            (55, 5, 'Comunicação', 'Habilidade de se expressar'),
            (56, 5, 'Liderança', 'Capacidade de guiar equipes'),
            (57, 5, 'Colaboração', 'Trabalhar bem em equipe'),
            (58, 5, 'Criatividade', 'Pensar fora da caixa'),
            (59, 5, 'Gestão de Tempo', 'Organizar tarefas e prazos'),
            (60, 5, 'Inteligência Emocional', 'Gerir as próprias emoções')
        ]
        cursor.executemany("INSERT INTO skill (skill_id, categoria_id, nome, descricao) VALUES (?, ?, ?, ?)", soft_skills)
        
        # Interesses
        interesses = [
            (1, 'Desenvolvimento Backend', 'Interesse em criar APIs, microsserviços e lógica de servidor'),
            (2, 'Data Science e IA', 'Interesse em machine learning, análise de dados e redes neurais'),
            (3, 'Desenvolvimento Frontend', 'Interesse em criar interfaces de usuário ricas e responsivas'),
            (4, 'Gestão de Projetos', 'Interesse em metodologias ágeis e liderança de equipes')
        ]
        cursor.executemany("INSERT INTO interesse (interesse_id, nome, descricao) VALUES (?, ?, ?)", interesses)

        conn.commit()
        print("✅ Tabelas de lookup populadas com sucesso!")

    except sqlite3.Error as e:
        print(f"❌ Ocorreu um erro ao popular o banco: {e}")
        conn.rollback() # Desfaz qualquer mudança se houver erro
    finally:
        conn.close()
        print(f"📦 Conexão com '{DB_FILE}' fechada.")

if __name__ == "__main__":
    criar_e_popular_banco()