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
        valores = [round(i, 1) for i in frange(94.5, 96.4, 0.1)]
    else:
        valores = [round(i, 1) for i in frange(100.0, 102.0, 0.1)]
    return random.choice(valores)

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])
qtd = st.text_input("Quantidade de ensaios")
peso_cilindro = st.text_input("Peso do cilindro (g)")
volume_cilindro = st.text_input("Volume do cilindro (L)")
densidade_maxima = st.text_input("Densidade máxima (ex: 1788 → 1.788)")
umidade_hot = st.text_input("Umidade ótima (%)")
executar = st.button("Gerar Ensaios")

if executar:
    try:
        qtd = int(qtd)
        peso_cilindro = float(peso_cilindro.replace(',', '.'))
        volume_cilindro = float(volume_cilindro.replace(',', '.'))
        dens_max = float(densidade_maxima.replace(',', '').replace('.', '')) / 1000
        umidade_hot = float(umidade_hot.replace(',', '.'))
    except ValueError:
        st.error("⚠️ Preencha todos os campos corretamente.")
    else:
        umidades = gerar_umidades(umidade_hot, qtd)
        st.success("✅ Ensaios gerados com sucesso!")

        for i in range(qtd):
            umidade = umidades[i]
            grau = gerar_grau_compactacao(tipo)
            dens_sec = (grau * dens_max) / 100
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
