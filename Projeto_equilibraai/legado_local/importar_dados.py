#código usando para colocar os dados dentro do banco de dados local no começo do projeto
import sqlite3
import csv
import os

def importar_dados_completos():
    print("🚀 Iniciando importação de dados...")
    
    conn = sqlite3.connect('meu_banco.db')
    cursor = conn.cursor()
    
    print("📖 Lendo colaboradores_100.csv...")
    with open('colaboradores_100.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        colaboradores = list(reader)
        
        for colab in colaboradores:
            cursor.execute('''
            INSERT OR REPLACE INTO colaborador (colaborador_id, nome, email, data_cadastro)
            VALUES (?, ?, ?, ?)
            ''', (colab['colaborador_id'], colab['nome'], colab['email'], colab['data_cadastro']))
    
    print(f"✅ {len(colaboradores)} colaboradores importados")
    
    print("📖 Lendo colaborador_skills_100.csv...")
    with open('colaborador_skills_100.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        skills = list(reader)
        
        for skill in skills:
            cursor.execute('''
            INSERT OR REPLACE INTO colaborador_skill 
            (colaborador_id, skill_id, nivel_experiencia_id, confianca, data_avaliacao)
            VALUES (?, ?, ?, ?, ?)
            ''', (skill['colaborador_id'], skill['skill_id'], skill['nivel_experiencia_id'], 
                  skill['confianca'], skill['data_avaliacao']))
    
    print(f"✅ {len(skills)} skills de colaboradores importadas")
    
    print("🔍 Verificando dados base...")
    
    cursor.execute("SELECT COUNT(*) FROM nivel_experiencia")
    if cursor.fetchone()[0] == 0:
        print("📊 Inserindo níveis de experiência...")
        niveis = [
            (1, 'Iniciante', 'Conhecimento básico', 0.3),
            (2, 'Intermediário', 'Conhecimento prático', 0.6),
            (3, 'Avançado', 'Domínio do assunto', 0.8),
            (4, 'Especialista', 'Referência no assunto', 1.0)
        ]
        cursor.executemany('''
        INSERT OR IGNORE INTO nivel_experiencia (nivel_id, nome, descricao, peso)
        VALUES (?, ?, ?, ?)
        ''', niveis)
    
    cursor.execute("SELECT COUNT(*) FROM categoria_skill")
    if cursor.fetchone()[0] == 0:
        print("📚 Inserindo categorias e skills base...")
        
    print("\n📊 Validando importação...")
    
    cursor.execute("SELECT COUNT(*) FROM colaborador")
    total_colabs = cursor.fetchone()[0]
    print(f"👥 Colaboradores no banco: {total_colabs}")
    
    cursor.execute("SELECT COUNT(*) FROM colaborador_skill")
    total_skills = cursor.fetchone()[0]
    print(f"🛠 Skills registradas: {total_skills}")
    
    if total_colabs > 0:
        media_skills = total_skills / total_colabs
        print(f"📚 Média de skills por colaborador: {media_skills:.2f}")
    
    conn.commit()
    conn.close()
    
    print("\n🎊 Importação concluída com sucesso!")
    print("📁 Dados importados:")
    print("   ✅ colaboradores_100.csv → tabela 'colaborador'")
    print("   ✅ colaborador_skills_100.csv → tabela 'colaborador_skill'")

def verificar_estrutura_banco():
    """Verifica se as tabelas existem antes de importar"""
    print("🔍 Verificando estrutura do banco...")
    
    conn = sqlite3.connect('meu_banco.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    
    print("📋 Tabelas encontradas:")
    for tabela in tabelas:
        print(f"   - {tabela[0]}")
    
    conn.close()
    
    tabelas_necessarias = ['colaborador', 'colaborador_skill', 'nivel_experiencia']
    tabelas_encontradas = [t[0] for t in tabelas]
    
    for tabela in tabelas_necessarias:
        if tabela not in tabelas_encontradas:
            print(f"❌ Tabela '{tabela}' não encontrada!")
            return False
    
    print("✅ Estrutura do banco OK!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("📥 IMPORTADOR DE DADOS PARA BANCO SQLite")
    print("=" * 50)
    
    arquivos_necessarios = ['colaboradores_100.csv', 'colaborador_skills_100.csv']
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo {arquivo} não encontrado!")
            exit(1)
    
    if verificar_estrutura_banco():
        importar_dados_completos()
    else:
        print("❌ Estrutura do banco incompleta. Execute primeiro o script de criação.")