
import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
st.set_page_config(page_title="Finance Dashboard", layout="wide")

global category_file
category_file = './Finance/data/categories.json'

def load_transactions(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = ['Data', 'Descricao', 'Valor']
        df['Data'] = pd.to_datetime(df['Data'])
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['Dia'] = df['Data'].dt.day
        # df['Data'] = df['Data'].dt.date
        df['Parcela'] = df['Descricao'].apply(lambda x: x.split(' - Parcela')[1] if ' - Parcela' in x else 'Unica')
        df['Descricao'] = df['Descricao'].apply(lambda x: x.split(' - Parcela')[0])

        df = df[['Ano', 'Mes', 'Dia', 'Descricao', 'Parcela', 'Valor']]
        df = categorizar(df)
        # st.write(df)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def save_categories():
    with open(category_file, 'w') as f:
        json.dump(st.session_state.categories, f)

def categorizar(df):
    df['Categoria'] = 'Sem Categoria'
    for categoria, palavras_chave in st.session_state.categories.items():
        if categoria =='Sem Categoria' or not palavras_chave:
            continue
        for idx, row in df.iterrows():
            detalhes = row['Descricao'].lower()
            if any(palavra.lower() in detalhes for palavra in palavras_chave):
                df.at[idx, 'Categoria'] = categoria
    return df

def add_categoria(categoria, palavras_chave):
    palavras_chave = palavras_chave.strip()
    if palavras_chave and palavras_chave not in st.session_state.categories[categoria]:
        st.session_state.categories[categoria].append(palavras_chave)
        save_categories()
        st.success(f"Palavra-chave '{palavras_chave}' adicionada à categoria '{categoria}'")
    
def main():
    st.title("Finance Dashboard")

    uploaded_file = st.file_uploader("Upload your transactions csv file", type=["csv"])
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        df_debito = df[df['Valor'] > 0]
        df_credito = df[df['Valor'] < 0]

        st.session_state.df_debito = df_debito
        st.session_state.df_credito = df_credito

        tab1, tab2 = st.tabs(["Débitos", "Créditos"])  
        with tab1:
            st.header("Análise de Débitos")
            new_categories = st.text_input("Adicionar nova categoria:")
            add_button = st.button("Adicionar Categoria")
            if add_button and new_categories:
                st.session_state.categories[new_categories] = []
                save_categories()
                st.success(f"Categoria '{new_categories}' adicionada com sucesso!")
                st.rerun()

            st.subheader("Seus Gasstos")
            lista_categorias = list(st.session_state.categories.keys())
            lista_categorias.sort()
            df_editable = st.data_editor(
                st.session_state.df_debito,
                column_config={
                    'Categoria': st.column_config.SelectboxColumn(
                        options=lista_categorias,
                        label="Categoria",
                    )
                },
                hide_index=True,
                # width='content',
                key="debito_editor"
                )
            save_button = st.button("Salvar Categorias", type="primary")
            if save_button:
                for idx, row in df_editable.iterrows():
                    new_categorie = row['Categoria']
                    if new_categorie == st.session_state.df_debito.at[idx, 'Categoria']:
                        continue
                    details  =row['Descricao']
                    st.session_state.df_debito.at[idx, 'Categoria'] = new_categorie
                    add_categoria(new_categorie, details)
                st.success("Categorias atualizadas com sucesso!")
                st.rerun()

            #Analise Visual
            st.subheader("Análise Visual")
            subtab1, subtab2 = st.tabs(["Categoria", "Subcategoria"])  
            df_debito_2 = df_debito.copy()
            df_debito_2['SubCategoria'] = df_debito_2['Categoria'].apply(lambda x: x.split('/')[1] if '/' in x else 'Geral')
            df_debito_2['Categoria'] = df_debito_2['Categoria'].apply(lambda x: x.split('/')[0])

            with subtab1:
                total_por_categoria = df_debito_2.groupby('Categoria')['Valor'].sum().reset_index()
                total_por_categoria = total_por_categoria.sort_values(by='Valor', ascending=False)
                fig = px.bar(total_por_categoria, x='Categoria', y='Valor', title='Total de Débitos por Categoria')
                st.plotly_chart(fig, use_container_width=True)
            with subtab2:
                total_por_subcategoria = df_debito_2.groupby('SubCategoria')['Valor'].sum().reset_index()
                total_por_subcategoria = total_por_subcategoria.sort_values(by='Valor', ascending=False)
                fig2 = px.bar(total_por_subcategoria, x='SubCategoria', y='Valor', title='Total de Débitos por Subcategoria')
                st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.header("Análise de Créditos")
            st.write(df_credito) 
