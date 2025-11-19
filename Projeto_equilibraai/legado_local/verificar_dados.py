import sqlite3
import pandas as pd

def verificar_dados_importados():
    print("🔍 Verificando dados importados...")
    
    conn = sqlite3.connect('meu_banco.db')
    
    # 1. Colaboradores
    print("👥 Primeiros 5 colaboradores:")
    df_colabs = pd.read_sql_query("SELECT * FROM colaborador LIMIT 5", conn)
    print(df_colabs[['colaborador_id', 'nome', 'email']])
    
    # 2. Skills dos colaboradores (CONSULTA CORRIGIDA)
    print("\n🛠 Primeiras 10 skills de colaboradores:")
    df_skills = pd.read_sql_query('''
    SELECT cs.colaborador_id, c.nome, cs.skill_id, cs.nivel_experiencia_id, cs.confianca
    FROM colaborador_skill cs
    JOIN colaborador c ON cs.colaborador_id = c.colaborador_id
    LIMIT 10
    ''', conn)
    print(df_skills)
    
    # 3. Estatísticas
    total_colabs = pd.read_sql_query("SELECT COUNT(*) as total FROM colaborador", conn).iloc[0,0]
    total_skills = pd.read_sql_query("SELECT COUNT(*) as total FROM colaborador_skill", conn).iloc[0,0]
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de colaboradores: {total_colabs}")
    print(f"   Total de skills registradas: {total_skills}")
    print(f"   Média de skills por colaborador: {total_skills/total_colabs:.2f}")
    
    # 4. Distribuição de níveis
    print(f"\n🎯 Distribuição de níveis de experiência:")
    dist_niveis = pd.read_sql_query('''
    SELECT nivel_experiencia_id, COUNT(*) as quantidade
    FROM colaborador_skill
    GROUP BY nivel_experiencia_id
    ORDER BY nivel_experiencia_id
    ''', conn)
    print(dist_niveis)
    
    # 5. Colaborador com mais skills
    print(f"\n🏆 Colaboradores com mais skills:")
    top_colabs = pd.read_sql_query('''
    SELECT c.colaborador_id, c.nome, COUNT(cs.skill_id) as total_skills
    FROM colaborador c
    JOIN colaborador_skill cs ON c.colaborador_id = cs.colaborador_id
    GROUP BY c.colaborador_id, c.nome
    ORDER BY total_skills DESC
    LIMIT 5
    ''', conn)
    print(top_colabs)
    
    # 6. Skills mais comuns
    print(f"\n📈 Skills mais populares:")
    top_skills = pd.read_sql_query('''
    SELECT skill_id, COUNT(*) as total_colaboradores
    FROM colaborador_skill
    GROUP BY skill_id
    ORDER BY total_colaboradores DESC
    LIMIT 10
    ''', conn)
    print(top_skills)
    
    conn.close()
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    verificar_dados_importados()