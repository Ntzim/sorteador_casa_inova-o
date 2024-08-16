import streamlit as st
import pandas as pd
import random
from io import BytesIO

# Função para realizar sorteio por grupo
def realizar_sorteio_por_grupo(df, quantidade_por_grupo):
    ganhadores_por_grupo = {}
    
    # Filtra para ampla concorrência
    df_ampla_concorrencia = df[df['Ampla Concorrência'] == True]
    
    for grupo in quantidade_por_grupo.keys():
        if grupo == 'Ampla Concorrência':
            continue  # Deixamos o sorteio de ampla concorrência por último
        
        df_grupo = df[df[grupo] == True]
        
        if len(df_grupo) > 0:
            quantidade_real = min(quantidade_por_grupo[grupo], len(df_grupo))
            ganhadores = df_grupo.sample(n=quantidade_real, random_state=random.randint(0, 10000))
            
            # Se sobrar vagas, preenche com ampla concorrência
            if quantidade_real < quantidade_por_grupo[grupo]:
                vagas_restantes = quantidade_por_grupo[grupo] - quantidade_real
                ganhadores_extra = df_ampla_concorrencia.sample(n=vagas_restantes, random_state=random.randint(0, 10000))
                df_ampla_concorrencia = df_ampla_concorrencia.drop(ganhadores_extra.index)
                ganhadores = pd.concat([ganhadores, ganhadores_extra])
            
            ganhadores_por_grupo[grupo] = ganhadores
        else:
            st.warning(f"Não há candidatos no grupo '{grupo}'. Todas as vagas serão preenchidas pela ampla concorrência.")
            ganhadores_extra = df_ampla_concorrencia.sample(n=quantidade_por_grupo[grupo], random_state=random.randint(0, 10000))
            df_ampla_concorrencia = df_ampla_concorrencia.drop(ganhadores_extra.index)
            ganhadores_por_grupo[grupo] = ganhadores_extra
    
    # Sorteio de ampla concorrência com as vagas restantes
    if len(df_ampla_concorrencia) > 0:
        ganhadores_ampla = df_ampla_concorrencia.sample(n=quantidade_por_grupo['Ampla Concorrência'], random_state=random.randint(0, 10000))
        ganhadores_por_grupo['Ampla Concorrência'] = ganhadores_ampla
    
    return pd.concat(ganhadores_por_grupo.values())

# Função para baixar o arquivo Excel
def baixar_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ganhadores')
    processed_data = output.getvalue()
    return processed_data

# Configuração da aplicação
st.title("Sorteio Edital | Casa da Inovação 🏠")

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

    # Definição das quantidades de vagas por grupo
    quantidade_por_grupo = {
        'Ampla Concorrência': 15,
        'Negro ou Pardo': 3,
        'Pessoa com deficiência - PCD': 3,
        'Estudante de escola pública': 3,
        'Beneficiário Socioassistencial': 3
    }

    # Botão para realizar o sorteio
    if st.button("Realizar Sorteio"):
        if titulo_sorteio:
            ganhadores = realizar_sorteio_por_grupo(df, quantidade_por_grupo)
            
            if not ganhadores.empty:
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
                st.warning("Nenhum ganhador foi selecionado. Verifique se há candidatos nos grupos especificados.")
        else:
            st.warning("Por favor, insira um título para o sorteio.")
