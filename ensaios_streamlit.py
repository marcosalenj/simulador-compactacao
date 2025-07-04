import streamlit as st
import random
import sqlite3
import pandas as pd
import io

# ======= CONFIGURAÇÕES =======

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

def gerar_grau_compactacao(tipo):
    if tipo == "1º Aterro / Ligação":
        return round(random.uniform(94.5, 96.4), 1)
    return round(random.uniform(100.0, 102.0), 1)

def gerar_umidades_com_criterios(umidade_hot, quantidade, peso_cilindro, volume_cm3, densidade_maxima, tipo,
                                  limitar_umidade, limitar_peso, diferenca_minima, diferenca_peso_minima, somente_pares):
    """Gera umidades respeitando critérios"""
    inicio = round(umidade_hot - 1.0, 1)
    fim = round(umidade_hot - 0.1, 1)
    valores_possiveis = [round(i, 1) for i in frange(inicio, fim, 0.1)]

    umidades = []
    atual = random.choice(valores_possiveis)
    umidades.append(atual)

    grau = gerar_grau_compactacao(tipo)
    dens_sec = (grau * densidade_maxima) / 100
    dens_umid = ((100 + atual) * dens_sec) / 100
    peso_solo = dens_umid * volume_cm3
    peso_total_anterior = peso_solo + peso_cilindro

    for _ in range(1, quantidade):
        candidatos = []

        for u in valores_possiveis:
            if limitar_umidade and abs(u - atual) * 10 < diferenca_minima:
                continue

            grau = gerar_grau_compactacao(tipo)
            dens_sec = (grau * densidade_maxima) / 100
            dens_umid = ((100 + u) * dens_sec) / 100
            peso_solo = dens_umid * volume_cm3
            peso_total = peso_solo + peso_cilindro

            if limitar_peso and abs(peso_total - peso_total_anterior) < diferenca_peso_minima:
                continue

            if not somente_pares or int(round(peso_total)) % 2 == 0:
                candidatos.append(u)

        if not candidatos:
            candidatos = valores_possiveis

        atual = random.choice(candidatos)
        umidades.append(atual)

        grau = gerar_grau_compactacao(tipo)
        dens_sec = (grau * densidade_maxima) / 100
        dens_umid = ((100 + atual) * dens_sec) / 100
        peso_solo = dens_umid * volume_cm3
        peso_total_anterior = peso_solo + peso_cilindro

    return umidades

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

# ======= INTERFACE =======

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])
qtd_raw = st.text_input("Quantidade de ensaios", placeholder="Ex: 5")
cilindro_raw = st.text_input("Número do cilindro", placeholder="Ex: 4")

# Configurações de limite
diferenca_minima = 3        # décimos de umidade (%)
diferenca_peso_minima = 5   # gramas

# Peso/volume do banco
peso_cilindro = None
volume_cilindro_cm3 = None

if cilindro_raw.isdigit():
    resultado = buscar_cilindro(int(cilindro_raw))
    if resultado:
        peso_cilindro, volume_cilindro_cm3 = resultado

col1, col2 = st.columns(2)
with col1:
    st.text_input("Peso do cilindro (g)", value=str(int(peso_cilindro)) if peso_cilindro else "", disabled=True)
with col2:
    st.text_input("Volume do cilindro (cm³)", value=str(int(volume_cilindro_cm3)) if volume_cilindro_cm3 else "", disabled=True)

dens_raw = st.text_input("Densidade máxima", placeholder="Ex: 1883")
umidade_raw = st.text_input("Umidade ótima (%)", placeholder="Ex: 7,4")

# === CHECKBOXES antes do botão ===
st.markdown("---")
limitar_umidade = st.checkbox("Limitar diferença mínima de umidade", value=False)
limitar_peso = st.checkbox("Limitar diferença mínima de peso total", value=False)
somente_pares = st.checkbox("Apenas números pares no peso total", value=True)
st.markdown("---")

executar = st.button("Gerar Ensaios")

# ======= EXECUÇÃO =======

if executar:
    try:
        qtd = int(qtd_raw)
        numero_cilindro = int(cilindro_raw)

        if not peso_cilindro or not volume_cilindro_cm3:
            st.error("❌ Peso ou volume do cilindro não encontrados.")
            st.stop()

        densidade_maxima = float(dens_raw.replace(",", "").replace(".", "")) / 1000
        umidade_hot = float(umidade_raw.replace(",", "."))
    except:
        st.error("⚠️ Preencha todos os campos corretamente.")
    else:
        umidades = gerar_umidades_com_criterios(
            umidade_hot, qtd, peso_cilindro, volume_cilindro_cm3, densidade_maxima, tipo,
            limitar_umidade, limitar_peso, diferenca_minima, diferenca_peso_minima, somente_pares
        )

        st.success("✅ Ensaios gerados com sucesso!")

        resultados = []

        for i in range(qtd):
            umidade = umidades[i]
            grau = gerar_grau_compactacao(tipo)
            dens_sec = (grau * densidade_maxima) / 100
            dens_umid = ((100 + umidade) * dens_sec) / 100
            peso_solo = dens_umid * volume_cilindro_cm3
            peso_total = peso_solo + peso_cilindro
            delta_umid = round(umidade - umidade_hot, 2)

            resultados.append({
                "Cilindro": numero_cilindro,
                "Peso_Total": int(round(peso_total)),
                "Umidade": str(umidade).replace('.', ',')
            })

            with st.expander(f"🔹 Ensaio {i+1:02}"):
                st.markdown(f"- **Peso do Cilindro + Solo:** {int(round(peso_total))} g")
                st.markdown(f"- **Peso do Solo:** {int(round(peso_solo))} g")
                st.markdown(f"- **Densidade Úmida:** {int(round(dens_umid * 1000))} g/cm³")
                st.markdown(f"- **Umidade:** {str(umidade).replace('.', ',')} %")
                st.markdown(f"- **Densidade Seca:** {int(round(dens_sec * 1000))} g/cm³")
                st.markdown(f"- **Grau de Compactação:** {str(grau).replace('.', ',')} %")
                st.markdown(f"- **Δ Umidade:** {str(delta_umid).replace('.', ',')}")

        # Exportar para CSV
        df_export = pd.DataFrame(resultados)
        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8").encode()

        st.download_button(
            label="📥 Baixar CSV dos Ensaios",
            data=csv,
            file_name="ensaios.csv",
            mime="text/csv"
        )
   