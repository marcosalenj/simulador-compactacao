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

# Estado inicial
if "tipo" not in st.session_state:
    st.session_state.tipo = ""
if "qtd" not in st.session_state:
    st.session_state.qtd = ""
if "peso_cilindro" not in st.session_state:
    st.session_state.peso_cilindro = ""
if "volume_cilindro" not in st.session_state:
    st.session_state.volume_cilindro = ""
if "densidade_maxima" not in st.session_state:
    st.session_state.densidade_maxima = ""
if "umidade_hot" not in st.session_state:
    st.session_state.umidade_hot = ""

def reset_campos():
    st.session_state.qtd = ""
    st.session_state.peso_cilindro = ""
    st.session_state.volume_cilindro = ""
    st.session_state.densidade_maxima = ""
    st.session_state.umidade_hot = ""

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

qtd_str = st.text_input(
    "Quantidade de ensaios", value=st.session_state.qtd,
    disabled=disabled_inputs, key="qtd"
)
peso_cilindro_str = st.text_input(
    "Peso do cilindro (g)", value=st.session_state.peso_cilindro,
    disabled=disabled_inputs, key="peso_cilindro"
)
volume_cilindro_str = st.text_input(
    "Volume do cilindro (L)", value=st.session_state.volume_cilindro,
    disabled=disabled_inputs, key="volume_cilindro"
)
densidade_maxima_str = st.text_input(
    "Densidade máxima (ex: 1788 → 1.788)", value=st.session_state.densidade_maxima,
    disabled=disabled_inputs, key="densidade_maxima"
)
umidade_hot_str = st.text_input(
    "Umidade ótima (%)", value=st.session_state.umidade_hot,
    disabled=disabled_inputs, key="umidade_hot"
)

executar = st.button("Gerar Ensaios", disabled=disabled_inputs)

def valida_numero(valor_str, tipo=int):
    try:
        return tipo(valor_str)
    except:
        return None

if executar:
    qtd = valida_numero(qtd_str, int)
    peso_cilindro = valida_numero(peso_cilindro_str, float)
    volume_cilindro = valida_numero(volume_cilindro_str, float)
    densidade_maxima = valida_numero(densidade_maxima_str, float)
    umidade_hot = valida_numero(umidade_hot_str, float)

    erros = []
    if qtd is None or qtd < 1:
        erros.append("Quantidade de ensaios deve ser inteiro maior ou igual a 1.")
    if peso_cilindro is None or peso_cilindro <= 0:
        erros.append("Peso do cilindro deve ser número positivo.")
    if volume_cilindro is None or volume_cilindro <= 0:
        erros.append("Volume do cilindro deve ser número positivo.")
    if densidade_maxima is None or densidade_maxima <= 0:
        erros.append("Densidade máxima deve ser número positivo.")
    if umidade_hot is None or umidade_hot <= 0:
        erros.append("Umidade ótima deve ser número positivo.")

    if erros:
        for e in erros:
            st.error(f"⚠️ {e}")
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
