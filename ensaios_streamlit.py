import streamlit as st
import random
import sqlite3
import pandas as pd

# ======= CONFIGURAÇÕES =======

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

def gerar_grau_compactacao(tipo):
    if tipo == "1º Aterro / Ligação":
        return round(random.uniform(94.5, 96.4), 1)
    return round(random.uniform(100.0, 102.0), 1)

def calcula_propriedades(u, tipo, dens_max, volume_cm3, peso_cilindro):
    grau = gerar_grau_compactacao(tipo)
    dens_sec = grau * dens_max / 100
    dens_umid = (100 + u) * dens_sec / 100
    peso_solo = dens_umid * volume_cm3
    peso_total = peso_solo + peso_cilindro
    return grau, dens_sec, dens_umid, peso_solo, peso_total

def gerar_umidades_com_criterios(
    umidade_hot, quantidade, peso_cilindro, volume_cm3,
    densidade_maxima, tipo, limitar_umidade, limitar_peso,
    diferenca_minima, diferenca_peso_minima, somente_pares
):
    inicio = round(umidade_hot - 1.0, 1)
    fim = round(umidade_hot - 0.1, 1)
    valores_possiveis = [round(i, 1) for i in frange(inicio, fim, 0.1)]

    umidades = []
    atual = random.choice(valores_possiveis)
    umidades.append(atual)

    _, _, _, _, peso_total_anterior = calcula_propriedades(
        atual, tipo, densidade_maxima, volume_cm3, peso_cilindro
    )

    for _ in range(1, quantidade):
        candidatos = []
        for u in valores_possiveis:
            if limitar_umidade and abs(u - atual) * 10 < diferenca_minima:
                continue

            _, _, _, _, peso_total = calcula_propriedades(
                u, tipo, densidade_maxima, volume_cm3, peso_cilindro
            )
            if limitar_peso and abs(peso_total - peso_total_anterior) < diferenca_peso_minima:
                continue

            if not somente_pares or int(round(peso_total)) % 2 == 0:
                candidatos.append(u)

        if not candidatos:
            candidatos = valores_possiveis

        atual = random.choice(candidatos)
        umidades.append(atual)
        _, _, _, _, peso_total_anterior = calcula_propriedades(
            atual, tipo, densidade_maxima, volume_cm3, peso_cilindro
        )

    return umidades

# ======= CACHE DA CONEXÃO SQLite =======

@st.cache_resource
def get_db_connection():
    return sqlite3.connect('cilindros.db', check_same_thread=False)

def buscar_cilindro(numero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT peso, volume FROM cilindros WHERE numero = ?", (numero,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        st.error(f"Erro no banco de cilindros: {e}")
        return None

# ======= INTERFACE =======

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])

qtd = st.number_input("Quantidade de ensaios", min_value=1, step=1, value=5)
numero_cilindro = st.number_input("Número do cilindro", min_value=1, step=1, value=1)

# Recupera peso e volume do cilindro
peso_cilindro = volume_cilindro_cm3 = None
resultado = buscar_cilindro(numero_cilindro)
if resultado:
    peso_cilindro, volume_cilindro_cm3 = resultado

col1, col2 = st.columns(2)
with col1:
    st.text_input("Peso do cilindro (g)",
                  value=str(int(peso_cilindro)) if peso_cilindro else "",
                  disabled=True)
with col2:
    st.text_input("Volume do cilindro (cm³)",
                  value=str(int(volume_cilindro_cm3)) if volume_cilindro_cm3 else "",
                  disabled=True)

densidade_input = st.number_input("Densidade máxima (kg/m³)", min_value=0.0, step=1.0, value=1883.0)
umidade_hot = st.number_input("Umidade ótima (%)", min_value=0.0, step=0.1, value=7.4)

st.markdown("---")
limitar_umidade = st.checkbox("Limitar diferença mínima de umidade", value=False)
limitar_peso = st.checkbox("Limitar diferença mínima de peso total", value=False)
somente_pares = st.checkbox("Apenas números pares no peso total", value=True)
st.markdown("---")

executar = st.button("Gerar Ensaios")

# ======= EXECUÇÃO =======

if executar:
    # validação de cilindro
    if peso_cilindro is None or volume_cilindro_cm3 is None:
        st.error("❌ Peso ou volume do cilindro não encontrados.")
        st.stop()

    try:
        densidade_maxima = densidade_input / 1000  # converte kg/m³ → g/cm³
    except Exception as e:
        st.error(f"⚠️ Erro ao converter densidade: {e}")
        st.stop()

    try:
        umidades = gerar_umidades_com_criterios(
            umidade_hot, qtd, peso_cilindro, volume_cilindro_cm3,
            densidade_maxima, tipo, limitar_umidade, limitar_peso,
            diferenca_minima=3, diferenca_peso_minima=5, somente_pares=somente_pares
        )
    except Exception as e:
        st.error(f"⚠️ Falha ao gerar umidades: {e}")
        st.stop()

    st.success("✅ Ensaios gerados com sucesso!")

    resultados = []
    for i, u in enumerate(umidades):
        grau, dens_sec, dens_umid, peso_solo, peso_total = calcula_propriedades(
            u, tipo, densidade_maxima, volume_cilindro_cm3, peso_cilindro
        )
        delta_umid = round(u - umidade_hot, 2)

        resultados.append({
            "Cilindro": numero_cilindro,
            "Peso_Total": int(round(peso_total)),
            "Umidade": f"{u:.1f}".replace('.', ',')
        })

        with st.expander(f"🔹 Ensaio {i+1:02}"):
            st.markdown(f"- **Peso do Cilindro + Solo:** {int(round(peso_total))} g")
            st.markdown(f"- **Peso do Solo:** {int(round(peso_solo))} g")
            st.markdown(f"- **Densidade Úmida:** {int(round(dens_umid * 1000))} g/cm³")
            st.markdown(f"- **Umidade:** {u:.1f}".replace('.', ',') + " %")
            st.markdown(f"- **Densidade Seca:** {int(round(dens_sec * 1000))} g/cm³")
            st.markdown(f"- **Grau de Compactação:** {grau:.1f}".replace('.', ',") + " %")
            st.markdown(f"- **Δ Umidade:** {delta_umid}".replace('.', ','))

    # Exportar para CSV
    df_export = pd.DataFrame(resultados)
    csv = df_export.to_csv(index=False, sep=";", encoding="utf-8").encode()

    st.download_button(
        label="📥 Baixar CSV dos Ensaios",
        data=csv,
        file_name="ensaios.csv",
        mime="text/csv"
    )
