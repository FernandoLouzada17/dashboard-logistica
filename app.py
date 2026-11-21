import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração inicial da página
st.set_page_config(page_title="Dashboard de Logística", page_icon="📦", layout="wide")

# Função em cache para carregar dados mais rápido
@st.cache_data
def carregar_dados():
    conn = sqlite3.connect('data/logistica.db')
    query = """
    SELECT p.*, t.nome as transportadora 
    FROM pedidos p
    JOIN transportadoras t ON p.id_transportadora = t.id_transportadora
    """
    df = pd.read_sql_query(query, conn)
    
    # Tratamento de datas
    for col in ['data_compra', 'data_prevista', 'data_entregue']:
        df[col] = pd.to_datetime(df[col])
        
    # Cálculos de negócio
    df['dias_atraso'] = (df['data_entregue'] - df['data_prevista']).dt.days
    df['status'] = df['dias_atraso'].apply(lambda x: 'No Prazo' if x <= 0 else 'Atrasado')
    df['mes_compra'] = df['data_compra'].dt.to_period('M').astype(str)
    
    return df

try:
    df = carregar_dados()
except sqlite3.OperationalError:
    st.error("⚠️ Banco de dados não encontrado. Execute o script 'gerar_dados.py' primeiro.")
    st.stop()

st.title("📦 Dashboard de KPIs Logísticos")
st.markdown("Monitoramento de OTIF, Performance de Transportadoras e Custos de Frete.")

# Barra lateral para Filtros
st.sidebar.header("Filtros de Análise")
meses_disponiveis = ['Todos'] + sorted(df['mes_compra'].unique().tolist())
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", meses_disponiveis)

# Aplicar filtro
if mes_selecionado != 'Todos':
    df = df[df['mes_compra'] == mes_selecionado]

# Linha de KPIs (Indicadores)
total_pedidos = len(df)
otif = (len(df[df['status'] == 'No Prazo']) / total_pedidos) * 100 if total_pedidos > 0 else 0
custo_total = df['custo_frete'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📦 Total de Pedidos", f"{total_pedidos:,}")
col2.metric("🎯 OTIF (No Prazo)", f"{otif:.1f}%")
col3.metric("💰 Custo Total de Frete", f"R$ {custo_total:,.2f}")

st.markdown("---")

# Linha de Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Performance por Transportadora")
    df_transp = df.groupby(['transportadora', 'status']).size().reset_index(name='contagem')
    fig1 = px.bar(df_transp, x='transportadora', y='contagem', color='status', barmode='group',
                  color_discrete_map={'No Prazo': '#00CC96', 'Atrasado': '#EF553B'})
    st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.subheader("Evolução do Custo de Frete")
    df_custo = df.groupby('mes_compra')['custo_frete'].sum().reset_index()
    fig2 = px.line(df_custo, x='mes_compra', y='custo_frete', markers=True)
    st.plotly_chart(fig2, use_container_width=True)