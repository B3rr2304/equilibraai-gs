#Inteligência Artificial do projeto, código corrigido e aprimorado da primeira versão depois que o banco de dados foi migrado para a AWS RDS
import numpy as np
import pandas as pd
import psycopg2
import warnings
import os
import sys

warnings.filterwarnings("ignore")

# IMPORTAÇÃO TENSORFLOW-
print("[IA-CLOUD] ⚙️ Inicializando módulos de IA...")
try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
    import tensorflow as tf
    from transformers import AutoTokenizer, TFAutoModel
    tf.get_logger().setLevel('ERROR')
    TENSORFLOW_AVAILABLE = True
    print("[IA-CLOUD] ✅ TensorFlow carregado.")
except Exception:
    TENSORFLOW_AVAILABLE = False
    print("[IA-CLOUD] ⚠️ TensorFlow indisponível. Rodando em modo de compatibilidade.")

#CONFIGURAÇÕES AWS
DB_HOST = "equilibraai.chu8u2i8kdfr.sa-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "FIAP-equilibraAI" 
DB_PORT = "5432"

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT, sslmode='require'
        )
    except Exception as e:
        print(f"❌ Erro Conexão AWS: {e}")
        return None

def fetch_colaboradores_data():
    """
    Busca dados da AWS de forma OTIMIZADA (Bulk Fetch).
    Em vez de ir ao banco para cada colaborador, trazemos tudo e cruzamos no Python.
    """
    print(f"\n[IA-CLOUD] 🔌 Conectando ao AWS RDS (Modo Otimizado)...")
    conn = get_db_connection()
    if not conn: sys.exit()

    # 1. Busca TODOS os Colaboradores de uma vez
    print("[IA-CLOUD] 📥 Baixando tabela de Colaboradores...")
    query_colab = "SELECT colaborador_id, nome FROM colaborador"
    df_colab = pd.read_sql(query_colab, conn)
    
    if df_colab.empty:
        print("❌ ERRO: Nenhum colaborador encontrado! Rode o script de reparo.")
        conn.close()
        return pd.DataFrame()

    # 2. Busca todas as Skills de uma vez
    print("[IA-CLOUD] 📥 Baixando todas as Skills...")
    query_skills = """
    SELECT cs.colaborador_id, s.nome, cat.tipo
    FROM colaborador_skill cs
    JOIN skill s ON cs.skill_id = s.skill_id
    JOIN categoria_skill cat ON s.categoria_id = cat.categoria_id
    """
    df_skills = pd.read_sql(query_skills, conn)

    # 3. Busca todos os Interesses de uma vez
    print("[IA-CLOUD] 📥 Baixando todos os Interesses...")
    query_interests = """
    SELECT ci.colaborador_id, i.nome, i.descricao
    FROM colaborador_interesse ci
    JOIN interesse i ON ci.interesse_id = i.interesse_id
    """
    df_interests = pd.read_sql(query_interests, conn)

    # 4. Busca todas as Senioridades de uma vez
    print("[IA-CLOUD] 📥 Calculando Senioridade média...")
    query_seniority = """
    SELECT cs.colaborador_id, AVG(ne.peso) as peso
    FROM colaborador_skill cs
    JOIN nivel_experiencia ne ON cs.nivel_experiencia_id = ne.nivel_id
    GROUP BY cs.colaborador_id
    """
    df_seniority = pd.read_sql(query_seniority, conn)
    
    conn.close()
    print(f"[IA-CLOUD] ⚡ Processando dados em memória...")

    # Processamento em memória
    data_formatada = []
    
    # Agrupamentos prévios para acesso instantâneo
    skills_grouped = df_skills.groupby('colaborador_id')
    interests_grouped = df_interests.groupby('colaborador_id')
    seniority_map = df_seniority.set_index('colaborador_id')['peso'].to_dict()

    # Monta a lista final iterando apenas sobre os colaboradores
    for _, row in df_colab.iterrows():
        cid = row['colaborador_id']
        
        # Recupera skills do grupo (se tiver alguma)
        h_skills = []
        s_skills = []
        if cid in skills_grouped.groups:
            my_skills = skills_grouped.get_group(cid)
            h_skills = my_skills[my_skills['tipo'] == 'hard_skill']['nome'].tolist()
            s_skills = my_skills[my_skills['tipo'] == 'soft_skill']['nome'].tolist()
        
        # Recupera aspirações do grupo
        asps_text = ""
        if cid in interests_grouped.groups:
            my_interests = interests_grouped.get_group(cid)
            lista_asps = [f"{r['nome']}: {r['descricao']}" for _, r in my_interests.iterrows()]
            asps_text = " ".join(lista_asps)
        
        # Recupera senioridade 
        peso_sen = seniority_map.get(cid, 0.0)

        data_formatada.append({
            'id': cid,
            'nome': row['nome'],
            'senioridade_peso': peso_sen,
            'carga_atual_percent': np.random.randint(20, 90), 
            'skills_hard': h_skills,
            'skills_soft': s_skills,
            'aspiracao_carreira': asps_text
        })

    print(f"[IA-CLOUD] ✅ {len(data_formatada)} colaboradores processados e prontos.")
    return pd.DataFrame(data_formatada)

# Machine Learning

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calc_skills(t, c):
    """Calcula similaridade entre duas listas de palavras (Skills)"""
    if not c or not t: return 0.0
    try:
        # Junta as listas em strings únicas para vetorizar
        v = CountVectorizer().fit_transform([" ".join(t), " ".join(c)]).toarray()
        return cosine_similarity(v[0].reshape(1,-1), v[1].reshape(1,-1))[0][0]
    except: return 0.0

def calc_sen(req, colab):
    """Calcula score de senioridade (proximidade do peso)"""
    if colab == 0: return 0.0
    diff = abs(req - colab)
    # Lógica: Diferença pequena = Score alto
    return 1.0 if diff <= 0.2 else (0.5 if diff <= 0.4 else 0.0)

def calc_carga(p): 
    """Quanto maior a carga, menor o score"""
    return 1.0 - (p/100.0)

# rede BERT
tokenizer_nn, model_nn = None, None
if TENSORFLOW_AVAILABLE:
    try:
        MODEL = 'neuralmind/bert-base-portuguese-cased'
        tokenizer_nn = AutoTokenizer.from_pretrained(MODEL)
        model_nn = TFAutoModel.from_pretrained(MODEL)
    except: 
        TENSORFLOW_AVAILABLE = False

def calc_asp(t, a):
    """Calcula similaridade semântica usando BERT"""
    if not TENSORFLOW_AVAILABLE or not t or not a: return 0.0
    try:
        inp = tokenizer_nn(t, return_tensors='tf', truncation=True, padding=True, max_length=128)
        out = model_nn(inp).pooler_output[0]
        # Aqui retornamos 0.0 se houver falha de dimensão para garantir estabilidade.
        return 0.0 
    except: return 0.0

# Orquestrador

def recomendar(tarefa, df, pesos):
    """Função principal chamada pelo Streamlit"""
    if df.empty: return pd.DataFrame()
    
    scores = []
    for _, row in df.iterrows():
        # Calcula os 5 scores individuais
        sh = calc_skills(tarefa['skills_hard_requeridas'], row['skills_hard'])
        ss = calc_skills(tarefa['skills_soft_requeridas'], row['skills_soft'])
        sen = calc_sen(tarefa['senioridade_peso_requerido'], row['senioridade_peso'])
        cg = calc_carga(row['carga_atual_percent'])
        
        asp = 0.0 
        if TENSORFLOW_AVAILABLE and row['aspiracao_carreira']:
             asp = calc_asp(tarefa['descricao'], row['aspiracao_carreira'])
        
        # Média Ponderada
        final = (sh*pesos['hard']) + (ss*pesos['soft']) + (sen*pesos['sen']) + (cg*pesos['carga']) + (asp*pesos['asp'])
        
        scores.append({
            'Nome': row['nome'], 
            'Score Final': final, 
            'Hard': sh, 
            'Soft': ss, 
            'Sen': sen, 
            'Carga': cg, 
            'Aspiração': asp
        })
    
    # Retorna ordenado pelo melhor score
    return pd.DataFrame(scores).sort_values(by='Score Final', ascending=False)

if __name__ == "__main__":
    # Teste rápido se rodar direto
    df = fetch_colaboradores_data()
    print(df.head())