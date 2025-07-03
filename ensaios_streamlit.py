import streamlit as st
import random

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

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

# Inicializa valores no session_state para os campos, se ainda não existirem
if "tipo" not in st.session_state:
    st.session_state.tipo = ""
if "qtd" not in st.session_state:
    st.session_state.qtd = 1
if "peso_cilindro" not in st.session_state:
    st.session_state.peso_cilindro = 0.0
if "volume_cilindro" not in st.session_state:
    st.session_state.volume_cilindro = 0.0
if "densidade_maxima" not in st.session_state:
    st.session_state.densidade_maxima = 0.0
if "umidade_hot" not in st.session_state:
    st.session_state.umidade_hot = 0.0

def reset_campos():
    st.session_state.qtd = 1
    st.session_state.peso_cilindro = 0.0
    st.session_state.volume_cilindro = 0.0
    st.session_state.densidade_maxima = 0.0
    st.session_state.umidade_hot = 0.0

def on_tipo_change():
    if st.session_state.tipo != "":
        reset_campos()

tipo = st.selectbox(
    "Tipo de ensaio:",
    options=["", "1º Aterro / Ligação", "2º Aterro / Sub-base"],
    format_func=lambda x: "Selecione o tipo" if x == "" else x,
    key="tipo",
    on_change=on_tipo_change
)

disabled_inputs = (st.session_state.tipo == "")

qtd = st.number_input(
    "Quantidade de ensaios", min_value=1, value=st.session_state.qtd, step=1,
    disabled=disabled_inputs, key="qtd"
)
peso_cilindro = st.number_input(
    "Peso do cilindro (g)", min_value=0.0, value=st.session_state.peso_cilindro,
    format="%.2f", disabled=disabled_inputs, key="peso_cilindro"
)
volume_cilindro = st.number_input(
    "Volume do cilindro (L)", min_value=0.0, value=st.session_state.volume_cilindro,
    format="%.2f", disabled=disabled_inputs, key="volume_cilindro"
)
densidade_maxima = st.number_input(
    "Densidade máxima (ex: 1788 → 1.788)", min_value=0.0,
    value=st.session_state.densidade_maxima, format="%.3f",
    disabled=disabled_inputs, key="densidade_maxima"
)
umidade_hot = st.number_input(
    "Umidade ótima (%)", min_value=0.0, value=st.session_state.umidade_hot,
    format="%.1f", disabled=disabled_inputs, key="umidade_hot"
)

executar = st.button("Gerar Ensaios", disabled=disabled_inputs)

if executar:
    if densidade_maxima == 0.0 or umidade_hot == 0.0 or volume_cilindro == 0.0 or peso_cilindro == 0.0:
        st.error("⚠️ Preencha todos os campos corretamente.")
    else:
        umidades = gerar_umidades(umidade_hot, qtd)
        st.success("✅ Ensaios gerados com sucesso!")

        for i in range(qtd):
            umidade = umidades[i]
            grau = gerar_grau_compactacao(tipo)
            dens_sec = (grau * densidade_maxima) / 100
            dens_umid = ((100 + umidade) * dens_sec) / 100
            volume_cm3 = volume_cilindro * 1000
            peso_solo = dens_umid * volume_cm3
            peso_total = peso_solo + peso_cilindro
            delta_umid = round(umidade - umidade_hot, 2)

            with st.expander(f"🔹 Ensaio {i+1:02}"):
                st.markdown(f"- **Umidade:** {umidade:.1f} %")
                st.markdown(f"- **Grau de Compactação:** {grau:.1f} %")
                st.markdown(f"- **Densidade Seca:** {dens_sec:.3f} g/cm³")
                st.markdown(f"- **Densidade Úmida:** {dens_umid:.3f} g/cm³")
                st.markdown(f"- **Peso do Solo:** {peso_solo:.2f} g")
                st.markdown(f"- **Peso do Cilindro + Solo:** {int(round(peso_total))} g")
                st.markdown(f"- **Δ Umidade:** {delta_umid:.2f} %")
