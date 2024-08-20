import streamlit as st
import pandas as pd
import random
from io import BytesIO

# Inicializa o DataFrame global no session state
if 'sorteados_global' not in st.session_state:
    st.session_state.sorteados_global = pd.DataFrame(columns=['ID', 'Name', 'Curso'])

# Função para realizar sorteio por grupo
def realizar_sorteio_por_grupo(df, quantidade_por_grupo, curso_selecionado):
    ganhadores_por_grupo = {}
    
    # Filtra para ampla concorrência
    df_ampla_concorrencia = df[df['Ampla Concorrência'] == True]
    
    for grupo in quantidade_por_grupo.keys():
        if grupo == 'Ampla Concorrência':
            continue  # Deixamos o sorteio de ampla concorrência por último
        
        df_grupo = df[df[grupo] == True]
        total_grupo = len(df_grupo)
        
        if total_grupo > 0:
            quantidade_real = min(quantidade_por_grupo[grupo], total_grupo)
            ganhadores = df_grupo.sample(n=quantidade_real, random_state=random.randint(0, 10000))
            
            # Se sobrar vagas, preenche com ampla concorrência
            if quantidade_real < quantidade_por_grupo[grupo]:
                vagas_restantes = quantidade_por_grupo[grupo] - quantidade_real
                total_ampla_concorrencia = len(df_ampla_concorrencia)
                
                if vagas_restantes > total_ampla_concorrencia:
                    vagas_restantes = total_ampla_concorrencia
                
                if vagas_restantes > 0:
                    ganhadores_extra = df_ampla_concorrencia.sample(n=vagas_restantes, random_state=random.randint(0, 10000))
                    df_ampla_concorrencia = df_ampla_concorrencia.drop(ganhadores_extra.index)
                    ganhadores = pd.concat([ganhadores, ganhadores_extra])
            
            ganhadores_por_grupo[grupo] = ganhadores
        else:
            st.warning(f"Não há candidatos no grupo '{grupo}'. Todas as vagas serão preenchidas pela ampla concorrência.")
            vagas_restantes = quantidade_por_grupo[grupo]
            total_ampla_concorrencia = len(df_ampla_concorrencia)
            
            if vagas_restantes > total_ampla_concorrencia:
                vagas_restantes = total_ampla_concorrencia
            
            if vagas_restantes > 0:
                ganhadores_extra = df_ampla_concorrencia.sample(n=vagas_restantes, random_state=random.randint(0, 10000))
                df_ampla_concorrencia = df_ampla_concorrencia.drop(ganhadores_extra.index)
                ganhadores_por_grupo[grupo] = ganhadores_extra
    
    # Sorteio de ampla concorrência com as vagas restantes
    if len(df_ampla_concorrencia) > 0 and quantidade_por_grupo['Ampla Concorrência'] > 0:
        total_ampla_concorrencia = len(df_ampla_concorrencia)
        quantidade_real = min(quantidade_por_grupo['Ampla Concorrência'], total_ampla_concorrencia)
        ganhadores_ampla = df_ampla_concorrencia.sample(n=quantidade_real, random_state=random.randint(0, 10000))
        ganhadores_por_grupo['Ampla Concorrência'] = ganhadores_ampla
    
    ganhadores = pd.concat(ganhadores_por_grupo.values())
    ganhadores['Curso'] = curso_selecionado
    return ganhadores

# Função para baixar o arquivo Excel
def baixar_excel(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ganhadores')
    processed_data = output.getvalue()
    return processed_data

# Configuração da aplicação
st.title("Sorteio Edital | Casa da Inovação 🏠")

# Seletores de curso
curso_selecionado = st.selectbox("Selecione o curso", [
    'Criação de Aplicativos | Manhã',
    'Programação de Games | Teens | Manhã',
    'Introdução à Robótica | Kids | Manhã',
    'Inclusão Digital | +50 anos | Manhã',
    'Criação de Aplicativos | Tarde',
    'Programação de Games | Teens | Tarde',
    'Programação de Games | Kids | Tarde',
    'Digital Influencer | Tarde',
    'Introdução à Robótica | Kids | Tarde',
    'Introdução à Robótica | Teens | Tarde',
    'Introdução ao Mundo Digital e Pacote Office | Noite',
    'Marketing Digital | Noite',
])

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leitura do arquivo Excel
    df = pd.read_excel(uploaded_file)
    
    # Filtrando candidatos que já foram sorteados
    df = df[~df['ID'].isin(st.session_state.sorteados_global['ID'])]
    
    # Mostrar os primeiros registros do arquivo carregado
    st.write(f"Primeiros registros do arquivo ({curso_selecionado}):")
    st.dataframe(df.head())

    # Definição das quantidades de vagas por grupo
    if curso_selecionado in ['Programação de Games | Teens | Tarde','Programação de Games | Teens | Manhã', 'Introdução à Robótica | Teens | Tarde',
                             'Introdução à Robótica | Kids | Tarde']:
        quantidade_por_grupo = {
            'Ampla Concorrência': 15,
            'Negro ou Pardo': 3,
            'Pessoa com deficiência - PCD': 3,
            'Estudante de escola pública': 3,
            'Beneficiário Socioassistencial': 3
        }
    else:
        quantidade_por_grupo = {
            'Ampla Concorrência': 15,
            'Negro ou Pardo': 3,
            'Pessoa com deficiência - PCD': 3,
            'Estudante de escola pública': 3,
            'Beneficiário Socioassistencial': 3
        }

    # Botão para realizar o sorteio
    if st.button(f"Realizar Sorteio para {curso_selecionado}"):
        ganhadores = realizar_sorteio_por_grupo(df, quantidade_por_grupo, curso_selecionado)
        
        if not ganhadores.empty:
            st.write(f"**{curso_selecionado}** - Lista de ganhadores:")
            st.dataframe(ganhadores)
            
            # Adicionando os sorteados ao DataFrame global
            st.session_state.sorteados_global = pd.concat([st.session_state.sorteados_global, ganhadores[['ID', 'Name', 'Curso']]])
            
        

            # Adicionar botão para baixar as inscrições dos ganhadores
            inscricoes_data = baixar_excel(ganhadores[['ID', 'Name', 'Curso']], 'inscricoes_ganhadores.xlsx')
            st.download_button(
                label="Baixar inscrições dos ganhadores",
                data=inscricoes_data,
                file_name=f'{curso_selecionado.replace(" | ", "_").replace(" ", "_")}_inscricoes_ganhadores.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Nenhum ganhador foi selecionado. Verifique se há candidatos nos grupos especificados.")

# Exibir todos os sorteados globais até agora
if not st.session_state.sorteados_global.empty:
    st.write("### Ganhadores acumulados até agora:")
    st.dataframe(st.session_state.sorteados_global)

    # Adicionar botão para baixar todos os ganhadores acumulados
    todos_ganhadores_excel = baixar_excel(st.session_state.sorteados_global, 'todos_ganhadores.xlsx')
    st.download_button(
        label="Baixar todos os ganhadores acumulados",
        data=todos_ganhadores_excel,
        file_name='todos_ganhadores_acumulados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
