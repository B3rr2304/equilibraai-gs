# --- ia_core_equilibraai.py ---
# Versão Final - Adaptada para o banco de dados SQLite 'meu_banco.db'
# Inclui: Machine Learning (Skills) + Redes Neurais (Aspirações - BERT Português)

import numpy as np
import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModel
import warnings
import os

# Suprime avisos técnicos para limpar a saída
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
tf.get_logger().setLevel('ERROR')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_NAME = 'meu_banco.db'

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    if not os.path.exists(DB_NAME):
        raise FileNotFoundError(f"Arquivo '{DB_NAME}' não encontrado. Rode 'banco_dados.py' e 'importar_dados.py' antes.")
    return sqlite3.connect(DB_NAME)

def fetch_colaboradores_data():
    """
    Busca dados do banco e formata para o DataFrame usado pela IA.
    """
    print(f"\n[IA-CORE] 🔌 Conectando ao banco '{DB_NAME}'...")
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Colaboradores
    colaboradores = cursor.execute("SELECT * FROM colaborador").fetchall()
    
    data_formatada = []
    
    for colab in colaboradores:
        colab_id = colab['colaborador_id']
        
        # 2. Hard Skills
        hard_query = """
        SELECT s.nome FROM skill s
        JOIN colaborador_skill cs ON s.skill_id = cs.skill_id
        JOIN categoria_skill cat ON s.categoria_id = cat.categoria_id
        WHERE cs.colaborador_id = ? AND cat.tipo = 'hard_skill'
        """
        hard_skills = [row['nome'] for row in cursor.execute(hard_query, (colab_id,)).fetchall()]
        
        # 3. Soft Skills
        soft_query = """
        SELECT s.nome FROM skill s
        JOIN colaborador_skill cs ON s.skill_id = cs.skill_id
        JOIN categoria_skill cat ON s.categoria_id = cat.categoria_id
        WHERE cs.colaborador_id = ? AND cat.tipo = 'soft_skill'
        """
        soft_skills = [row['nome'] for row in cursor.execute(soft_query, (colab_id,)).fetchall()]

        # 4. Aspirações (Interesses)
        asp_query = """
        SELECT i.nome, i.descricao FROM interesse i
        JOIN colaborador_interesse ci ON i.interesse_id = ci.interesse_id
        WHERE ci.colaborador_id = ?
        """
        aspiracoes = [f"{row['nome']}: {row['descricao']}" for row in cursor.execute(asp_query, (colab_id,)).fetchall()]
        aspiracao_texto = " ".join(aspiracoes) if aspiracoes else ""

        # 5. Senioridade (Média dos pesos)
        sen_query = """
        SELECT AVG(ne.peso) as peso_medio FROM nivel_experiencia ne
        JOIN colaborador_skill cs ON ne.nivel_id = cs.nivel_experiencia_id
        WHERE cs.colaborador_id = ?
        """
        res = cursor.execute(sen_query, (colab_id,)).fetchone()
        peso_senioridade = res['peso_medio'] if res['peso_medio'] else 0.0

        # 6. Carga (Mock - Simulado)
        carga_mock = np.random.randint(20, 90)

        data_formatada.append({
            'id': colab_id,
            'nome': colab['nome'],
            'senioridade_peso': peso_senioridade,
            'carga_atual_percent': carga_mock,
            'skills_hard': hard_skills,
            'skills_soft': soft_skills,
            'aspiracao_carreira': aspiracao_texto
        })

    conn.close()
    print(f"[IA-CORE] ✅ {len(data_formatada)} colaboradores carregados.")
    return pd.DataFrame(data_formatada)

# --- MÓDULO DE MACHINE LEARNING (SKILLS) ---

def calcular_similaridade_skills(lista_tarefa, lista_colaborador):
    """Similaridade de Cosseno para listas de tags."""
    if not lista_colaborador or not lista_tarefa:
        return 0.0

    txt_tarefa = " ".join(lista_tarefa)
    txt_colab = " ".join(lista_colaborador)

    try:
        vectorizer = CountVectorizer().fit_transform([txt_tarefa, txt_colab])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]
    except ValueError:
        return 0.0

# --- MÓDULO LÓGICO (SENIORIDADE & CARGA) ---

def calcular_score_senioridade(peso_req, peso_colab):
    if peso_colab == 0: return 0.0
    diff = abs(peso_req - peso_colab)
    if diff <= 0.2: return 1.0
    elif diff <= 0.4: return 0.5
    else: return 0.0

def calcular_score_carga(percentual):
    return 1.0 - (percentual / 100.0)

# --- MÓDULO REDES NEURAIS (ASPIRAÇÃO - BERT) ---

print("[IA-CORE] 🧠 Carregando Rede Neural (BERT em Português)...")
try:
    # Modelo neuralmind/bert-base-portuguese-cased é mais robusto para PT-BR
    MODEL_NAME = 'neuralmind/bert-base-portuguese-cased'
    tokenizer_nn = AutoTokenizer.from_pretrained(MODEL_NAME)
    model_nn = TFAutoModel.from_pretrained(MODEL_NAME)
    print("[IA-CORE] ✅ Modelo BERT carregado.")
except Exception as e:
    print(f"[IA-CORE] ⚠️ Erro ao carregar BERT: {e}. Modulo de aspiração será ignorado.")
    tokenizer_nn, model_nn = None, None

def get_embedding(text):
    if tokenizer_nn is None or not text: return None
    inputs = tokenizer_nn(text, return_tensors='tf', truncation=True, padding=True, max_length=128)
    outputs = model_nn(inputs)
    return outputs.pooler_output[0]

def calcular_similaridade_semantica(txt_tarefa, txt_aspiracao):
    if not txt_tarefa or not txt_aspiracao or model_nn is None: return 0.0
    emb_tarefa = get_embedding(txt_tarefa)
    emb_asp = get_embedding(txt_aspiracao)
    if emb_tarefa is None or emb_asp is None: return 0.0
    
    return cosine_similarity(tf.reshape(emb_tarefa, (1, -1)), tf.reshape(emb_asp, (1, -1)))[0][0]

# --- MOTOR DE RECOMENDAÇÃO ---

def recomendar(tarefa, df, pesos):
    scores = []
    for _, colab in df.iterrows():
        s_hard = calcular_similaridade_skills(tarefa['skills_hard_requeridas'], colab['skills_hard'])
        s_soft = calcular_similaridade_skills(tarefa['skills_soft_requeridas'], colab['skills_soft'])
        s_sen = calcular_score_senioridade(tarefa['senioridade_peso_requerido'], colab['senioridade_peso'])
        s_carga = calcular_score_carga(colab['carga_atual_percent'])
        s_asp = calcular_similaridade_semantica(tarefa['descricao'], colab['aspiracao_carreira'])
        
        final = (s_hard * pesos['hard']) + (s_soft * pesos['soft']) + (s_sen * pesos['sen']) + (s_carga * pesos['carga']) + (s_asp * pesos['asp'])
        
        scores.append({
            'Nome': colab['nome'],
            'Score Final': round(final, 3),
            'Hard Skills': round(s_hard, 2),
            'Soft Skills': round(s_soft, 2),
            'Senioridade': round(s_sen, 2),
            'Carga': round(s_carga, 2),
            'Aspiração': round(s_asp, 2)
        })
    
    return pd.DataFrame(scores).sort_values(by='Score Final', ascending=False)

# --- EXECUÇÃO ---

if __name__ == "__main__":
    try:
        print("\n[IA-CORE] 🚀 Iniciando Simulação EquilibraAI...")
        df_colabs = fetch_colaboradores_data()

        # Tarefas Exemplo
        tarefa1 = {
            'nome': "API Pagamentos",
            'descricao': "Desenvolver API RESTful com Python e Flask para pagamentos.",
            'senioridade_peso_requerido': 0.8,
            'skills_hard_requeridas': ['Python', 'Flask', 'SQL'],
            'skills_soft_requeridas': ['Resolução de Problemas']
        }
        
        tarefa2 = {
            'nome': "Modelo de Churn",
            'descricao': "Criar modelo de Machine Learning para prever cancelamento de clientes.",
            'senioridade_peso_requerido': 0.8,
            'skills_hard_requeridas': ['Python', 'Pandas', 'Scikit-learn'],
            'skills_soft_requeridas': ['Pensamento Analítico']
        }

        # Pesos
        pesos_tec = {'hard': 0.4, 'soft': 0.1, 'sen': 0.25, 'carga': 0.15, 'asp': 0.1}
        pesos_dev = {'hard': 0.25, 'soft': 0.1, 'sen': 0.15, 'carga': 0.2, 'asp': 0.3}

        print("\n=== 🏆 Ranking: API Pagamentos (Foco Técnico) ===")
        print(recomendar(tarefa1, df_colabs, pesos_tec).head().to_markdown(index=False))

        print("\n=== 🏆 Ranking: Modelo Churn (Foco Desenvolvimento) ===")
        print(recomendar(tarefa2, df_colabs, pesos_dev).head().to_markdown(index=False))

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("DICA: Verifique se rodou 'banco_dados.py' e 'importar_dados.py'.")