import streamlit as st
import random
import sqlite3

# ================== Funções ==================

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

# 🔧 Diferença mínima entre ensaios consecutivos (em décimos)
diferenca_minima = 3  # ← AJUSTE AQUI SE QUISER OUTRO VALOR (ex: 2 para 0,2 de diferença)

def gerar_umidades_diferenciadas(umidade_hot, quantidade):
    """Gera uma sequência de umidades com diferença mínima entre valores consecutivos"""
    inicio = round(umidade_hot - 1.0, 1)
    fim = round(umidade_hot - 0.1, 1)
    valores_possiveis = [round(i, 1) for i in frange(inicio, fim, 0.1)]

    umidades = []
    atual = random.choice(valores_possiveis)
    umidades.append(atual)

    for _ in range(1, quantidade):
        opcoes_validas = [u for u in valores_possiveis if abs(u - atual) * 10 >= diferenca_minima]
        if not opcoes_validas:
            opcoes_validas = valores_possiveis  # fallback de segurança
        atual = random.choice(opcoes_validas)
        umidades.append(atual)

    return umidades

def gerar_grau_compactacao(tipo):
    if tipo == "1º Aterro / Ligação":
        return round(random.uniform(94.5, 96.4), 1)
    return round(random.uniform(100.0, 102.0), 1)

def buscar_cilindro(numero):
    try:
        conn = sqlite3.connect('cilindros.db')
        cursor = conn.cursor()
        cursor.execute("SELECT peso, volume FROM cilindros WHERE numero = ?", (numero,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    except:
        return None

# ================== Interface ==================

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])

qtd_raw = st.text_input("Quantidade de ensaios", placeholder="Ex: 5")
cilindro_raw = st.text_input("Número do cilindro", placeholder="Ex: 4")

peso_cilindro = None
volume_cilindro = None
volume_cilindro_cm3 = None

if cilindro_raw.isdigit():
    resultado = buscar_cilindro(int(cilindro_raw))
    if resultado:
        peso_cilindro, volume_cilindro_cm3 = resultado
        volume_cilindro = volume_cilindro_cm3 / 1000
    else:
        st.warning("Cilindro não encontrado no banco.")

col1, col2 = st.columns(2)
with col1:
    st.text_input("Peso do cilindro (g)", value=str(int(peso_cilindro)) if peso_cilindro else "", disabled=True)
with col2:
    st.text_input("Volume do cilindro (cm³)", value=str(int(volume_cilindro_cm3)) if volume_cilindro_cm3 else "", disabled=True)

dens_raw = st.text_input("Densidade máxima", placeholder="Ex: 1.89")
umidade_raw = st.text_input("Umidade ótima (%)", placeholder="Ex: 12.5")

executar = st.button("Gerar Ensaios")

# ================== Execução ==================

if executar:
    try:
        qtd = int(qtd_raw)
        numero_cilindro = int(cilindro_raw)

        if not peso_cilindro or not volume_cilindro:
            st.error("❌ Peso ou volume do cilindro não encontrados.")
            st.stop()

        densidade_maxima = float(dens_raw.replace(",", "").replace(".", "")) / 1000
        umidade_hot = float(umidade_raw.replace(",", "."))
    except:
        st.error("⚠️ Preencha todos os campos corretamente.")
    else:
        umidades = gerar_umidades_diferenciadas(umidade_hot, qtd)
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
                st.markdown(f"- **Peso do Cilindro + Solo:** {int(round(peso_total))} g")
                st.markdown(f"- **Peso do Solo:** {int(round(peso_solo))} g")
                st.markdown(f"- **Densidade Úmida:** {int(round(dens_umid * 1000))} g/cm³")
                st.markdown(f"- **Umidade:** {str(umidade).replace('.', ',')} %")
                st.markdown(f"- **Densidade Seca:** {int(round(dens_sec * 1000))} g/cm³")
                st.markdown(f"- **Grau de Compactação:** {str(grau).replace('.', ',')} %")
                st.markdown(f"- **Δ Umidade:** {str(delta_umid).replace('.', ',')}")
