import streamlit as st
import random
import csv
from io import StringIO

# ===== Configurações visuais =====
st.set_page_config(page_title="Ensaios de Solo", layout="centered")
st.title("Simulador de Ensaios de Solo")

# ===== Funções auxiliares =====

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

def gerar_umidades_baseadas(umidade_hot, quantidade, min_diff, limitar=True):
    umidades = []
    valores_possiveis = [round(x, 1) for x in frange(umidade_hot - 1.0, umidade_hot - 0.1, 0.1)]

    while len(umidades) < quantidade:
        tentativa = random.choice(valores_possiveis)
        if not limitar:
            umidades.append(tentativa)
        elif len(umidades) == 0 or abs(tentativa - umidades[-1]) >= min_diff / 10:
            umidades.append(tentativa)
    return umidades

def gerar_graus_compactacao(tipo, quantidade, min_diff, limitar=True):
    graus = []
    faixa = (94.5, 96.4) if tipo == "1º Aterro / Ligação" else (100.0, 102.0)

    while len(graus) < quantidade:
        tentativa = round(random.uniform(*faixa), 1)
        if not limitar:
            graus.append(tentativa)
        elif len(graus) == 0 or abs(tentativa - graus[-1]) >= min_diff:
            graus.append(tentativa)
    return graus

# ===== Interface =====

tipo = st.selectbox("Tipo de ensaio:", ["1º Aterro / Ligação", "2º Aterro / Sub-base"])
registro_raw = st.text_input("Registro (opcional):", placeholder="Ex: lote, obra, setor etc.")

# ⚙️ Checkboxes para ajustes
st.markdown("**Opções Avançadas:**")
usar_limite_umidade = st.checkbox("Usar limite mínimo entre umidades", value=True)
usar_limite_peso = st.checkbox("Usar limite mínimo entre pesos", value=True)
apenas_pares = st.checkbox("Apenas números pares no peso total", value=False)

# Variáveis configuráveis
MIN_DIFF_UMIDADE = 3   # ← Altere aqui o mínimo de diferença entre umidades (%)
MIN_DIFF_PESO = 5      # ← Altere aqui o mínimo de diferença entre pesos (g)

# Dados de entrada
qtd_raw = st.text_input("Quantidade de ensaios")
cilindro_raw = st.text_input("Número do cilindro")
dens_raw = st.text_input("Densidade máxima")
umidade_raw = st.text_input("Umidade ótima (%)")

executar = st.button("Gerar Ensaios")

if executar:
    try:
        qtd = int(qtd_raw)
        numero_cilindro = int(cilindro_raw)
        densidade_maxima = float(dens_raw.replace(",", "").replace(".", "")) / 1000
        umidade_hot = float(umidade_raw.replace(",", "."))
    except:
        st.error("⚠️ Preencha todos os campos corretamente.")
    else:
        # Valores fixos do cilindro
        pesos_cilindros = {
            1: 986, 2: 964, 3: 952, 4: 1080, 5: 1048, 6: 1190,
            7: 1197, 8: 1097, 9: 1111, 10: 1186, 11: 1116, 12: 1045
        }
        volumes_cilindros = {
            1: 984, 2: 986, 3: 986, 4: 958, 5: 985, 6: 985,
            7: 967, 8: 985, 9: 958, 10: 958, 11: 967, 12: 967
        }

        if numero_cilindro not in pesos_cilindros:
            st.error("⚠️ Número de cilindro inválido.")
        else:
            peso_cilindro = pesos_cilindros[numero_cilindro]
            volume_cilindro = volumes_cilindros[numero_cilindro]

            # Geração dos dados
            umidades = gerar_umidades_baseadas(umidade_hot, qtd, MIN_DIFF_UMIDADE, usar_limite_umidade)
            graus = gerar_graus_compactacao(tipo, qtd, MIN_DIFF_PESO, usar_limite_peso)

            pesos_totais = []

            st.success("✅ Ensaios gerados com sucesso!")
            for i in range(qtd):
                umidade = umidades[i]
                grau = graus[i]

                dens_sec = (grau * densidade_maxima) / 100
                dens_umid = ((100 + umidade) * dens_sec) / 100
                volume_cm3 = volume_cilindro
                peso_solo = dens_umid * volume_cm3
                peso_total = int(round(peso_solo + peso_cilindro))

                # Verifica paridade se checkbox marcado
                if apenas_pares and peso_total % 2 != 0:
                    peso_total += 1  # Força para próximo número par

                pesos_totais.append(peso_total)
                delta_umid = round(umidade - umidade_hot, 2)

                with st.expander(f"🔹 Ensaio {i+1:02}"):
                    st.markdown(f"- **Cilindro:** {numero_cilindro}")
                    st.markdown(f"- **Peso do Cilindro + Solo:** {peso_total} g")
                    st.markdown(f"- **Peso do Solo:** {int(round(peso_solo))} g")
                    st.markdown(f"- **Densidade Úmida:** {int(round(dens_umid * 1000))}")
                    st.markdown(f"- **Umidade:** {str(umidade).replace('.', ',')} %")
                    st.markdown(f"- **Densidade Seca:** {int(round(dens_sec * 1000))}")
                    st.markdown(f"- **Grau de Compactação:** {str(grau).replace('.', ',')} %")
                    st.markdown(f"- **Δ Umidade:** {str(delta_umid).replace('.', ',')}")

            # Geração do CSV
            csv_buffer = StringIO()
            campos = ["Cilindro", "Peso_Total", "Umidade"]
            if registro_raw.strip():
                campos.append("Registro")
            writer = csv.writer(csv_buffer, delimiter=';')
            writer.writerow(campos)

            for i in range(qtd):
                linha = [
                    numero_cilindro,
                    pesos_totais[i],
                    str(umidades[i]).replace('.', ',')
                ]
                if registro_raw.strip():
                    linha.append(registro_raw.strip())
                writer.writerow(linha)

            st.download_button(
                label="📥 Baixar CSV dos Ensaios",
                data=csv_buffer.getvalue(),
                file_name="ensaios.csv",
                mime="text/csv"
            )
