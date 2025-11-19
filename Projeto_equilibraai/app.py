import streamlit as st
import pandas as pd
import time
from ia_core_aws import fetch_colaboradores_data, recomendar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="EquilibraAI",
    page_icon="⚖️",
    layout="wide"
)

# --- CABEÇALHO ---
st.title("⚖️ EquilibraAI")
st.markdown("### Sistema Inteligente de Alocação de Talentos")
st.markdown("---")

# --- SIDEBAR (FILTROS E PESOS) ---
with st.sidebar:
    st.header("⚙️ Configuração da IA")
    st.info("Ajuste os pesos para o algoritmo de recomendação.")
    
    p_hard = st.slider("Peso: Hard Skills", 0.0, 1.0, 0.4, 0.05)
    p_soft = st.slider("Peso: Soft Skills", 0.0, 1.0, 0.1, 0.05)
    p_sen = st.slider("Peso: Senioridade", 0.0, 1.0, 0.25, 0.05)
    p_carga = st.slider("Peso: Carga Atual", 0.0, 1.0, 0.15, 0.05)
    p_asp = st.slider("Peso: Aspiração (IA)", 0.0, 1.0, 0.1, 0.05)
    
    pesos = {
        'hard': p_hard,
        'soft': p_soft,
        'sen': p_sen,
        'carga': p_carga,
        'asp': p_asp
    }
    
    # Verifica soma dos pesos
    soma = sum(pesos.values())
    if soma != 1.0:
        st.warning(f"⚠️ A soma dos pesos é {soma:.2f}. O ideal é 1.0.")
    else:
        st.success("Pesos balanceados corretamente (100%).")
    
    if st.button("🔄 Recarregar Dados da Nuvem"):
        st.cache_data.clear()
        st.rerun()

# --- CORPO PRINCIPAL ---

# 1. Carregar Dados (com Cache para não ficar lento)
@st.cache_data
def carregar_dados():
    return fetch_colaboradores_data()

with st.spinner('Conectando ao AWS RDS e carregando colaboradores...'):
    try:
        df_colabs = carregar_dados()
        if df_colabs.empty:
            st.error("Nenhum colaborador encontrado no banco de dados.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao conectar na AWS: {e}")
        st.stop()

# 2. Formulário de Nova Tarefa
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Nova Demanda")
    
    nome_tarefa = st.text_input("Título da Tarefa", "Desenvolver API de Pagamentos")
    desc_tarefa = st.text_area("Descrição (para análise da IA)", "Criar uma API RESTful usando Python e Flask, com integração ao banco de dados SQL. Necessário foco em segurança.")
    
    senioridade = st.selectbox("Senioridade Necessária", ["Iniciante", "Intermediário", "Avançado", "Especialista"])
    map_senioridade = {"Iniciante": 0.3, "Intermediário": 0.6, "Avançado": 0.8, "Especialista": 1.0}
    
    # Busca as skills únicas do DF para preencher o multiselect
    # Flatten list of lists
    todas_hard = sorted(list(set([skill for sublist in df_colabs['skills_hard'] for skill in sublist])))
    todas_soft = sorted(list(set([skill for sublist in df_colabs['skills_soft'] for skill in sublist])))
    
    # --- CORREÇÃO DO ERRO DE DEFAULT ---
    # Verifica se 'Python' existe na lista antes de marcar como padrão
    default_hard = ['Python'] if 'Python' in todas_hard else []
    
    req_hard = st.multiselect("Hard Skills Obrigatórias", todas_hard, default=default_hard)
    req_soft = st.multiselect("Soft Skills Desejadas", todas_soft)
    
    botao_recomendar = st.button("🔍 Buscar Melhores Talentos", type="primary")

# 3. Resultados da Recomendação
with col2:
    st.subheader("🏆 Recomendações da IA")
    
    if botao_recomendar:
        # Monta o dicionário da tarefa
        tarefa = {
            'nome': nome_tarefa,
            'descricao': desc_tarefa,
            'senioridade_peso_requerido': map_senioridade[senioridade],
            'skills_hard_requeridas': req_hard,
            'skills_soft_requeridas': req_soft
        }
        
        # CHAMA A SUA IA (do arquivo ia_core_aws.py)
        with st.spinner('A IA está analisando compatibilidade, carga e aspirações...'):
            time.sleep(1) # UX: Pequena pausa para "sentir" o processamento
            df_resultado = recomendar(tarefa, df_colabs, pesos)
        
        # Exibe os Top 5
        if not df_resultado.empty:
            top_5 = df_resultado.head(5)
            
            # Mostra métricas do Top 1
            melhor_match = top_5.iloc[0]
            st.markdown(f"### ✨ Melhor Match: **{melhor_match['Nome']}** (Score: {melhor_match['Score Final']:.3f})")
            
            # Gráfico de barras simples para os scores do Top 1
            chart_data = pd.DataFrame({
                'Critério': ['Hard Skills', 'Soft Skills', 'Senioridade', 'Carga (Disponibilidade)', 'Aspiração (IA)'],
                'Score': [
                    melhor_match['Hard'], 
                    melhor_match['Soft'], 
                    melhor_match['Sen'], 
                    melhor_match['Carga'], 
                    melhor_match['Aspiração']
                ]
            })
            st.bar_chart(chart_data, x='Critério', y='Score')

            # Tabela Detalhada
            st.markdown("#### Ranking Detalhado")
            st.dataframe(
                top_5.style.background_gradient(subset=['Score Final'], cmap='Greens'),
                use_container_width=True
            )
        else:
            st.warning("Nenhum colaborador atende aos critérios mínimos.")
    else:
        st.info("👈 Preencha os dados da tarefa ao lado e clique em 'Buscar' para ver a mágica acontecer.")
        
        # Mostra uma visão geral da equipe enquanto não busca
        st.markdown("#### Visão Geral da Equipe (Dados da AWS)")
        st.dataframe(df_colabs[['id', 'nome', 'skills_hard', 'skills_soft']].head(10), use_container_width=True)