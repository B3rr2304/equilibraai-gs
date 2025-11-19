⚖️ EquilibraAI - Sistema Inteligente de Alocação de Talentos

Global Solution 2025.2 - O Futuro do Trabalho > Uma solução para combater o burnout e otimizar a produtividade através de IA e Cloud Computing.

📄 Sobre o Projeto

O EquilibraAI é uma plataforma Web que utiliza Inteligência Artificial para resolver um dos maiores desafios do trabalho moderno: a má alocação de talentos.

Diferente de ferramentas tradicionais que olham apenas para a disponibilidade ("quem está livre?"), o EquilibraAI utiliza um algoritmo multidimensional que cruza 5 fatores críticos para sugerir o colaborador ideal para cada tarefa, promovendo bem-estar e eficiência.

🧠 As 5 Dimensões da Nossa IA:

Hard Skills: Compatibilidade técnica (Machine Learning / Cosseno).

Soft Skills: Habilidades comportamentais.

Senioridade: Adequação do nível de experiência.

Carga de Trabalho: Prevenção ativa de burnout (quem está sobrecarregado recebe menor score).

Aspiração de Carreira (Deep Learning): Uso do modelo BERT (Transformers) para entender semanticamente se a tarefa se alinha com os objetivos de carreira do colaborador.

🏗️ Arquitetura Técnica

O projeto foi desenvolvido seguindo uma arquitetura moderna e escalável, totalmente integrada à nuvem.

Frontend & Aplicação: Desenvolvido em Streamlit, hospedado na nuvem (Streamlit Community Cloud), garantindo acessibilidade global.

Backend & IA: Processamento em Python utilizando Scikit-Learn para vetorização de skills e TensorFlow/Transformers para processamento de linguagem natural (NLP).

Banco de Dados (Nuvem): Persistência de dados realizada no Amazon AWS RDS (Relational Database Service) rodando PostgreSQL. Isso garante segurança, backup e escalabilidade real, saindo do ambiente local.

📂 Estrutura do Repositório

Abaixo, a explicação de cada módulo do projeto para avaliação técnica:

PROJETO-EQUILIBRAAI/
│
├── app.py                     # [FRONTEND] A interface web principal (Streamlit).
├── ia_core_aws.py             # [BACKEND/IA] O cérebro do sistema. Conecta na AWS e roda os modelos.
├── requirements.txt           # [INFRA] Lista de dependências para o deploy na nuvem.
│
├── data/                      # [DADOS] Fonte da verdade (CSVs originais).
│   ├── colaboradores_100.csv
│   └── colaborador_skills_100.csv
│
├── setup_nuvem/               # [DEVOPS] Scripts de migração e ETL.
│   └── reparar_banco.py       # Script que migrou os dados locais para o PostgreSQL na AWS.
│
└── versao_local_legacy/       # [HISTÓRICO] Versão 1.0 do projeto (SQLite/Local).
    ├── banco_dados.py         # (Legado) Criação do banco local.
    └── ia_core_equilibraai.py # (Legado) IA rodando offline.


🚀 Como Executar o Projeto

Opção 1: Acesso Online (Recomendado)

O projeto está implantado e rodando na nuvem. Acesse através do link:
🔗 https://myh5mb32wl6jyxvt6aklj4.streamlit.app/

Opção 2: Rodar Localmente

Para executar o projeto na sua máquina, siga os passos:

Clone o repositório:

git clone https://github.com/B3rr2304/equilibraai-gs.git
cd equilibraai-gs


Instale as dependências:

pip install -r requirements.txt


Configuração de Credenciais:

O projeto conecta-se a uma instância AWS RDS. As credenciais estão configuradas no arquivo ia_core_aws.py.

Nota: Em um ambiente de produção real, estas variáveis seriam injetadas via Secrets/Variáveis de Ambiente.

Execute a aplicação:

streamlit run app.py


🛠️ Tecnologias Utilizadas

Linguagem: Python 3.10+

Framework Web: Streamlit

Cloud Computing: Amazon Web Services (AWS RDS), Streamlit Cloud

Banco de Dados: PostgreSQL

Data Science: Pandas, NumPy

Machine Learning: Scikit-learn (CountVectorizer, Cosine Similarity)

Deep Learning / NLP: TensorFlow, Hugging Face Transformers (Modelo neuralmind/bert-base-portuguese-cased)

👥 Integrantes do Grupo

Nome 1 - RM: XXXXX

Nome 2 - RM: XXXXX

Nome 3 - RM: XXXXX

Nome 4 - RM: XXXXX

Nome 5 - RM: XXXXX

Projeto desenvolvido para a Global Solution - FIAP 2025.
