import sqlite3
import csv
import os

def importar_dados_completos():
    print("🚀 Iniciando importação de dados...")
    
    # Conectar ao banco
    conn = sqlite3.connect('meu_banco.db')
    cursor = conn.cursor()
    
    # 1. IMPORTAR COLABORADORES
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
    
    # 2. IMPORTAR SKILLS DOS COLABORADORES
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
    
    # 3. VERIFICAR E INSERIR DADOS BASE (se necessário)
    print("🔍 Verificando dados base...")
    
    # Verificar se existem níveis de experiência
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
    
    # Verificar se existem categorias e skills
    cursor.execute("SELECT COUNT(*) FROM categoria_skill")
    if cursor.fetchone()[0] == 0:
        print("📚 Inserindo categorias e skills base...")
        # Aqui você pode adicionar as categorias e skills que definimos anteriormente
        # Ou carregar de um CSV se tiver
        
    # 4. VALIDAR IMPORTACAO
    print("\n📊 Validando importação...")
    
    # Contar colaboradores
    cursor.execute("SELECT COUNT(*) FROM colaborador")
    total_colabs = cursor.fetchone()[0]
    print(f"👥 Colaboradores no banco: {total_colabs}")
    
    # Contar skills de colaboradores
    cursor.execute("SELECT COUNT(*) FROM colaborador_skill")
    total_skills = cursor.fetchone()[0]
    print(f"🛠 Skills registradas: {total_skills}")
    
    # Média de skills por colaborador
    if total_colabs > 0:
        media_skills = total_skills / total_colabs
        print(f"📚 Média de skills por colaborador: {media_skills:.2f}")
    
    # Salvar e fechar
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
    
    # Listar todas as tabelas
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
    
    # Verificar se os arquivos existem
    arquivos_necessarios = ['colaboradores_100.csv', 'colaborador_skills_100.csv']
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo {arquivo} não encontrado!")
            exit(1)
    
    # Verificar estrutura do banco
    if verificar_estrutura_banco():
        # Importar dados
        importar_dados_completos()
    else:
        print("❌ Estrutura do banco incompleta. Execute primeiro o script de criação.")