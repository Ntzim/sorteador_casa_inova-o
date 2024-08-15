import streamlit as st
import pandas as pd
import random
from io import BytesIO

# Função para realizar o sorteio
def realizar_sorteio(df, quantidade):
    ganhadores = df.sample(n=quantidade, random_state=random.randint(0, 10000))
    return ganhadores

# Função para baixar o arquivo Excel
def baixar_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ganhadores')
    processed_data = output.getvalue()
    return processed_data

# Configuração da aplicação
st.title("Aplicação de Sorteio por Excel")

# Entrada do título do sorteio
titulo_sorteio = st.text_input("Digite o título do sorteio")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leitura do arquivo Excel
    df = pd.read_excel(uploaded_file)
    
    # Mostrar os primeiros registros do arquivo carregado
    st.write("Primeiros registros do arquivo:")
    st.dataframe(df.head())

    # Entrada da quantidade de ganhadores
    quantidade = st.number_input("Quantidade de ganhadores", min_value=1, max_value=len(df), step=1)

    # Botão para realizar o sorteio
    if st.button("Realizar Sorteio"):
        if quantidade > 0 and titulo_sorteio:
            ganhadores = realizar_sorteio(df, quantidade)
            st.write(f"**{titulo_sorteio}** - Lista de ganhadores:")
            st.dataframe(ganhadores)

            # Adicionar botão para baixar o Excel
            excel_data = baixar_excel(ganhadores, 'ganhadores.xlsx')
            st.download_button(
                label="Baixar lista de ganhadores",
                data=excel_data,
                file_name=f'{titulo_sorteio}_ganhadores.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Por favor, insira um título para o sorteio e uma quantidade válida de ganhadores.")
