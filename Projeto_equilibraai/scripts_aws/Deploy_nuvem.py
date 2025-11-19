import psycopg2
import csv
import os

# --- CONFIGURAÇÕES DO SEU RDS ---
# DICA: Verifique se não há espaços em branco antes ou depois das strings!
DB_HOST = "equilibraai.chu8u2i8kdfr.sa-east-1.rds.amazonaws.com"
DB_NAME = "postgres" 
DB_USER = "postgres" 
DB_PASS = "FIAP-equilibraAI" # <--- ATENÇÃO: COLOQUE SUA SENHA DO RDS AQUI NOVAMENTE
DB_PORT = "5432"

def get_db_connection():
    """Conecta ao PostgreSQL no AWS RDS com SSL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode='require' 
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no RDS: {e}")
        return None

def criar_tabelas_postgres():
    """Cria as tabelas e popula dados MESTRES (Níveis e Categorias)"""
    print("\n☁️ Criando tabelas no AWS RDS...")
    
    conn = get_db_connection()
    if not conn: return
    
    cur = conn.cursor()
    
    # Comandos SQL
    comandos_sql = [
        '''
        CREATE TABLE IF NOT EXISTS nivel_experiencia (
            nivel_id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT,
            peso REAL NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS categoria_skill (
            categoria_id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('hard_skill', 'soft_skill')), 
            descricao TEXT
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS skill (
            skill_id SERIAL PRIMARY KEY,
            categoria_id INTEGER NOT NULL,
            nome VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categoria_skill(categoria_id)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS colaborador (
            colaborador_id SERIAL PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(150) UNIQUE,
            data_cadastro DATE DEFAULT CURRENT_DATE
        )
        ''',
        '''
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
        ''',
        '''
        CREATE TABLE IF NOT EXISTS interesse (
            interesse_id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            descricao TEXT
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS colaborador_interesse (
            colaborador_id INTEGER NOT NULL,
            interesse_id INTEGER NOT NULL,
            PRIMARY KEY (colaborador_id, interesse_id),
            FOREIGN KEY (colaborador_id) REFERENCES colaborador(colaborador_id),
            FOREIGN KEY (interesse_id) REFERENCES interesse(interesse_id)
        )
        '''
    ]

    try:
        for sql in comandos_sql:
            cur.execute(sql)
        conn.commit()
        print("✅ Tabelas criadas com sucesso no PostgreSQL!")
        
        # --- 1. Popular NÍVEIS ---
        niveis = [
            (1, 'Iniciante', 'Conhecimento básico', 0.3),
            (2, 'Intermediário', 'Conhecimento prático', 0.6),
            (3, 'Avançado', 'Domínio do assunto', 0.8),
            (4, 'Especialista', 'Referência no assunto', 1.0)
        ]
        cur.executemany("INSERT INTO nivel_experiencia (nivel_id, nome, descricao, peso) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", niveis)
        
        # --- 2. Popular CATEGORIAS (A CORREÇÃO ESTÁ AQUI) ---
        # Precisamos criar as categorias ANTES de criar as skills
        categorias = [
            (1, 'Desenvolvimento Backend', 'hard_skill', 'Tecnologias de servidor'),
            (2, 'Desenvolvimento Frontend', 'hard_skill', 'Tecnologias de cliente'),
            (3, 'Data Science', 'hard_skill', 'Análise e modelos de dados'),
            (4, 'DevOps', 'hard_skill', 'Infraestrutura e CI/CD'),
            (5, 'Habilidades Comportamentais', 'soft_skill', 'Competências interpessoais')
        ]
        cur.executemany("INSERT INTO categoria_skill (categoria_id, nome, tipo, descricao) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", categorias)

        conn.commit()
        print("✅ Dados mestres (Níveis e Categorias) inseridos.")
        
    except Exception as e:
        print(f"⚠️ Erro durante criação de tabelas/mestres: {e}")
    finally:
        cur.close()
        conn.close()

def migrar_dados_csv_para_nuvem():
    """Lê os CSVs locais e sobe para o RDS"""
    print("\n🚀 Migrando dados dos CSVs para a Nuvem...")
    
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()

    try:
        # 1. Migrar Colaboradores
        if os.path.exists('colaboradores_100.csv'):
            print("📤 Enviando Colaboradores...")
            with open('colaboradores_100.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                        INSERT INTO colaborador (colaborador_id, nome, email, data_cadastro)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (colaborador_id) DO NOTHING
                    """, (row['colaborador_id'], row['nome'], row['email'], row['data_cadastro']))
            print("✅ Colaboradores enviados.")

        # 2. Migrar Skills 
        print("⚙️ Garantindo que Skills existem...")
        # Agora isso vai funcionar porque a Categoria 1 já existe!
        skills_mock = [(i, 1, f'Skill {i}', 'Importada') for i in range(1, 51)]
        for s in skills_mock:
            cur.execute("INSERT INTO skill (skill_id, categoria_id, nome, descricao) VALUES (%s, %s, %s, %s) ON CONFLICT (skill_id) DO NOTHING", s)
        
        if os.path.exists('colaborador_skills_100.csv'):
            print("📤 Enviando Vínculos de Skills...")
            with open('colaborador_skills_100.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                        INSERT INTO colaborador_skill (colaborador_id, skill_id, nivel_experiencia_id, confianca, data_avaliacao)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (colaborador_id, skill_id) DO NOTHING
                    """, (row['colaborador_id'], row['skill_id'], row['nivel_experiencia_id'], row['confianca'], row['data_avaliacao']))
            print("✅ Vínculos de Skills enviados.")

        conn.commit()
        print("\n🎉 MIGRAÇÃO PARA AWS CONCLUÍDA COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # ATENÇÃO: Configure a variável DB_PASS no topo antes de rodar!
    criar_tabelas_postgres()
    migrar_dados_csv_para_nuvem()