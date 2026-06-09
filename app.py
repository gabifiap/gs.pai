import streamlit as st
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURAÇÃO E SEGURANÇA ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada no arquivo .env.")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="Você é um computador de bordo de missão espacial. Responda sempre de forma objetiva, sem entrar muito a fundo em diagnósticos técnincos, indique tudo o que precisa ser alertado e os proximos passos recomendados"
)

# Configuração da página
st.set_page_config(page_title="Synapse Mission Control", layout="wide")

# Estilização visual (CSS via Python)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-family: 'Courier New', monospace; }
    .stAlert { border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DA MISSÃO ---
def gerar_dados_realistas():
    return {
        "temp": round(random.uniform(20, 110), 1),
        "energia": random.randint(5, 100),
        "comunicacao": random.choice(["Estável", "Instável", "Crítica"]),
        "status": "OPERACIONAL"
    }

def verificar_alertas(d):
    alertas = []
    if d["temp"] > 100:
        alertas.append("⚠️ TEMPERATURA CRÍTICA")
    if d["energia"] < 20:
        alertas.append("⚠️ ENERGIA BAIXA")
    if d["comunicacao"] == "Crítica":
        alertas.append("⚠️ FALHA DE COMUNICAÇÃO")
    return alertas

# --- ESTADO DA APLICAÇÃO ---
if 'dados' not in st.session_state:
    st.session_state.dados = gerar_dados_realistas()
    st.session_state.historico = []

# --- INTERFACE ---
st.title("🛰️ Synapse Mission Control AI")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Telemetria Atual")
    d = st.session_state.dados

    # STATUS DA TEMPERATURA
    if d['temp'] > 100:
        status_temp = "🔴 CRÍTICA"
    elif d['temp'] > 80:
        status_temp = "🟡 ATENÇÃO"
    else:
        status_temp = "🟢 NORMAL"

    st.metric("Temperatura", f"{d['temp']}°C")
    st.caption(f"Status: {status_temp}")
    st.progress(min(d['temp'] / 120, 1.0))

    # STATUS DA ENERGIA
    if d['energia'] < 20:
        status_energia = "🔴 CRÍTICA"
    elif d['energia'] < 40:
        status_energia = "🟡 ATENÇÃO"
    else:
        status_energia = "🟢 NORMAL"

    st.metric("Energia", f"{d['energia']}%")
    st.caption(f"Status: {status_energia}")
    st.progress(d['energia'] / 100)

    # STATUS DA COMUNICAÇÃO
    status_comunicacao = {
        "Estável": "🟢 NORMAL",
        "Instável": "🟡 ATENÇÃO",
        "Crítica": "🔴 CRÍTICA"
    }

    st.write(f"**Comunicação:** {d['comunicacao']}")
    st.caption(f"Status: {status_comunicacao[d['comunicacao']]}")

# Lógica de decisão visual
alertas = verificar_alertas(d)
for a in alertas:
    st.error(a)

st.markdown("---")

# Simulação automática (IA)
if st.button("🤖 Simular Novo Ciclo por IA"):
    st.session_state.dados = gerar_dados_realistas()
    st.rerun()

# Inserção manual de dados
with st.expander("📝 Inserir Dados Manualmente"):

    temp_manual = st.number_input(
        "Temperatura (°C)",
        min_value=0.0,
        max_value=200.0,
        value=float(d["temp"])
    )

    energia_manual = st.slider(
        "Energia (%)",
        min_value=0,
        max_value=100,
        value=d["energia"]
    )

    comunicacao_manual = st.selectbox(
        "Comunicação",
        ["Estável", "Instável", "Crítica"],
        index=["Estável", "Instável", "Crítica"].index(d["comunicacao"])
    )

    if st.button("Inserir Dados"):
        st.session_state.dados = {
            "temp": temp_manual,
            "energia": energia_manual,
            "comunicacao": comunicacao_manual,
            "status": "OPERACIONAL"
        }
        st.rerun()

with col2:
    st.subheader("Diagnóstico da Inteligência Artificial")

    if st.button("Obter Diagnóstico Final"):
        with st.spinner('IA analisando o ciclo atual...'):
            prompt = f"Analise estes dados da missão Synapse: {d}. Alertas detectados: {alertas}. Dê um diagnóstico objetivo e uma ação imediata."
            resposta = model.generate_content(prompt)

            st.session_state.historico.append({
                "dados": d,
                "ia": resposta.text
            })

            st.info(resposta.text)

    # Exibição de histórico
    if st.session_state.historico:
        st.markdown("---")
        st.subheader("Histórico de Diagnósticos")

        for item in reversed(st.session_state.historico[-2:]):
            with st.expander(f"Ciclo: {item['dados']}"):
                st.write(item['ia'])

st.caption("Synapse Mission Control AI | Global Solution 2026.1 | FIAP")