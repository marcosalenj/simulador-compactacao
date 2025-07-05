import streamlit as st
import random
import sqlite3
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# ========== FUNÇÕES ==========

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

# ========== INTERFACE ==========

st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])
registro = st.text_input("Registro (opcional)", placeholder="Digite o número do registro, se houver")

# Inputs HTML com teclado numérico (type="tel")
st.markdown("### Dados do Ensaio")

st.markdown("""
<input id="qtd_ensaios" type="tel" placeholder="Quantidade de ensaios"
style="width:100%; padding:8px; font-size:16px;" />
""", unsafe_allow_html=True)

st.markdown("""
<input id="num_cilindro" type="tel" placeholder="Número do cilindro"
style="width:100%; padding:8px; font-size:16px;" />
""", unsafe_allow_html=True)

st.markdown("""
<input id="densidade_max" type="tel" placeholder="Densidade máxima (ex: 1883)"
style="width:100%; padding:8px; font-size:16px;" />
""", unsafe_allow_html=True)

st.markdown("""
<input id="umidade_hot" type="tel" step="0.1" placeholder="Umidade ótima (ex: 7,4)"
style="width:100%; padding:8px; font-size:16px;" />
""", unsafe_allow_html=True)

# Captura via JS
qtd_raw = streamlit_js_eval("document.getElementById('qtd_ensaios')?.value", key="qtd")
cilindro_raw = streamlit_js_eval("document.getElementById('num_cilindro')?.value", key="cilindro")
dens_raw = streamlit_js_eval("document.getElementById('densidade_max')?.value", key="dens")
umidade_raw = streamlit_js_eval("document.getElementById('umidade_hot')?.value", key="umid")

# Salvar no session_state
if qtd_raw:
    st.session_state["qtd_raw"] = qtd_raw
if cilindro_raw:
    st.session_state["cilindro_raw"] = cilindro_raw
if dens_raw:
    st.session_state["dens_raw"] = dens_raw
if umidade_raw:
    st.session_state["umidade_raw"] = umidade_raw

# Usar valores salvos
qtd_raw = st.session_state.get("qtd_raw", "")
cilindro_raw = st.session_state.get("cilindro_raw", "")
dens_raw = st.session_state.get("dens_raw", "")
umidade_raw = st.session_state.get("umidade_raw", "")

# Limites fixos
diferenca_minima = 3        # décimos de umidade
diferenca_peso_minima = 5   # gramas

# Checkboxes
st.markdown("---")
limitar_umidade = st.checkbox("Limitar diferença mínima de umidade", value=False)
limitar_peso = st.checkbox("Limitar diferença mínima de peso total", value=False)
somente_pares = st.checkbox("Apenas números pares no peso total", value=True)
st.markdown("---")

# Peso/Volume do banco
peso_cilindro = None
volume_cilindro_cm3 = None

if cilindro_raw and str(cilindro_raw).isdigit():
    resultado = buscar_cilindro(int(cilindro_raw))
    if resultado:
        peso_cilindro, volume_cilindro_cm3 = resultado

col1, col2 = st.columns(2)
with col1:
    st.text_input("Peso do cilindro (g)", value=str(int(peso_cilindro)) if peso_cilindro else "", disabled=True)
with col2:
    st.text_input("Volume do cilindro (cm³)", value=str(int(volume_cilindro_cm3)) if volume_cilindro_cm3 else "", disabled=True)

# EXECUTAR
executar = st.button("Gerar Ensaios")

if executar:
    try:
        qtd = int(qtd_raw)
        numero_cilindro = int(cilindro_raw)

        if not peso_cilindro or not volume_cilindro_cm3:
            st.error("❌ Peso ou volume do cilindro não encontrados.")
            st.stop()

        densidade_maxima = float(str(dens_raw).replace(",", "").replace(".", "")) / 1000
        umidade_hot = float(str(umidade_raw).replace(",", "."))
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

            resultado_dict = {
                "Cilindro": numero_cilindro,
                "Peso_Total": int(round(peso_total)),
                "Umidade": str(umidade).replace('.', ',')
            }

            if registro.strip():
                resultado_dict["Registro"] = registro.strip()

            resultados.append(resultado_dict)

            with st.expander(f"🔹 Ensaio {i+1:02}"):
                st.markdown(f"- **Peso do Cilindro + Solo:** {int(round(peso_total))} g")
                st.markdown(f"- **Peso do Solo:** {int(round(peso_solo))} g")
                st.markdown(f"- **Densidade Úmida:** {int(round(dens_umid * 1000))} g/cm³")
                st.markdown(f"- **Umidade:** {str(umidade).replace('.', ',')} %")
                st.markdown(f"- **Densidade Seca:** {int(round(dens_sec * 1000))} g/cm³")
                st.markdown(f"- **Grau de Compactação:** {str(grau).replace('.', ',')} %")

        # Exportar para CSV
        df_export = pd.DataFrame(resultados)
        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8").encode()

        st.download_button(
            label="📥 Baixar CSV dos Ensaios",
            data=csv,
            file_name="ensaios.csv",
            mime="text/csv"
        )
