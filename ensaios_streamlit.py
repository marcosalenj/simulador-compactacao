import streamlit as st
import streamlit.components.v1 as components
import random

# ========== Funções auxiliares ==========

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

def gerar_umidades(umidade_hot, quantidade):
    inicio = round(umidade_hot - 1.0, 1)
    fim = round(umidade_hot - 0.1, 1)
    valores = [round(i, 1) for i in frange(inicio, fim, 0.1)]
    return random.choices(valores, k=quantidade)

def gerar_grau_compactacao(tipo):
    if tipo == "1º Aterro / Ligação":
        return round(random.uniform(94.5, 96.4), 1)
    return round(random.uniform(100.0, 102.0), 1)

# ========== Configuração da Página ==========
st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

# ========== Seleção do Tipo ==========
tipo = st.selectbox(
    "Tipo de ensaio:",
    options=["", "1º Aterro / Ligação", "2º Aterro / Sub-base"],
    format_func=lambda x: "Selecione o tipo" if x == "" else x
)

# ========== Quantidade ==========
qtd = st.number_input("Quantidade de ensaios", min_value=1, value=1, step=1)

# ========== Campos customizados com seleção automática ==========

st.markdown("Peso do cilindro (g):")
components.html("""
    <input id="peso" name="peso" type="number" value="0"
           style="width: 100%%; padding: 6px; font-size: 16px;"
           onfocus="this.select()">
""", height=50)

st.markdown("Volume do cilindro (L):")
components.html("""
    <input id="volume" name="volume" type="number" value="0"
           style="width: 100%%; padding: 6px; font-size: 16px;"
           onfocus="this.select()">
""", height=50)

st.markdown("Densidade máxima (g/cm³):")
components.html("""
    <input id="densidade" name="densidade" type="number" value="0"
           style="width: 100%%; padding: 6px; font-size: 16px;"
           onfocus="this.select()">
""", height=50)

st.markdown("Umidade ótima (%):")
components.html("""
    <input id="umidade" name="umidade" type="number" value="0"
           style="width: 100%%; padding: 6px; font-size: 16px;"
           onfocus="this.select()">
""", height=50)

st.warning("⚠️ Para que o cálculo funcione, essa versão ainda **não captura os valores digitados** nos campos personalizados. Deseja que eu faça isso também?")

# ========== Botão de execução ==========
executar = st.button("Gerar Ensaios")
