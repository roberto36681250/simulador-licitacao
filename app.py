import streamlit as st
import pandas as pd
import json
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Simulador de Licitação", layout="wide")
st.title("🧮 Simulador de Preços para Licitação Pública")

# SESSION STATE INICIAL
if "produtos" not in st.session_state:
    st.session_state.produtos = []

st.sidebar.header("Parâmetros Globais")
desconto_max = st.sidebar.number_input("Desconto máximo (R$)", value=0.5, step=0.01, format="%.2f")
intervalo = st.sidebar.number_input("Intervalo (R$)", value=0.01, step=0.01, format="%.2f")

st.markdown("## Cadastro de Produto")
with st.form("produto_form"):
    cols = st.columns(7)
    nome = cols[0].text_input("Produto", "Fralda P")
    custo = cols[1].number_input("Custo (R$)", min_value=0.0, value=1.30, step=0.01)
    frete = cols[2].number_input("Frete (R$)", min_value=0.0, value=0.10, step=0.01)
    imposto = cols[3].number_input("Imposto (%)", min_value=0.0, value=10.0, step=0.1) / 100
    margem = cols[4].number_input("Lucro real (%)", min_value=0.0, value=15.0, step=0.1) / 100
    add = cols[5].form_submit_button("Adicionar Produto")
    clear = cols[6].form_submit_button("Limpar Todos")

    if add:
        st.session_state.produtos.append({
            "nome": nome,
            "custo": custo,
            "frete": frete,
            "imposto": imposto,
            "margem": margem
        })
    elif clear:
        st.session_state.produtos = []

if not st.session_state.produtos:
    st.info("Cadastre pelo menos um produto para iniciar a simulação.")
    st.stop()

# SIMULAÇÃO
st.markdown("---")
st.subheader("📊 Simulação por Produto")
resultados = []

for prod in st.session_state.produtos:
    preco_ideal = (prod["custo"] + prod["frete"]) / (1 - (prod["imposto"] + (1 - prod["imposto"]) * prod["margem"]))
    melhor_lucro = {"lucro": float('-inf')}
    simulacoes = []
    centavos = 0.0
    while centavos <= desconto_max:
        preco_venda = preco_ideal - centavos
        imposto_valor = preco_venda * prod["imposto"]
        custo_total = prod["custo"] + prod["frete"] + imposto_valor
        lucro = preco_venda - custo_total
        lucro_pct = lucro / custo_total if custo_total else 0
        simulacoes.append({
            "Produto": prod["nome"],
            "Desconto": centavos,
            "Preço Venda": preco_venda,
            "Imposto": imposto_valor,
            "Custo Total": custo_total,
            "Lucro R$": lucro,
            "Lucro %": lucro_pct
        })
        if lucro > melhor_lucro.get("lucro", 0):
            melhor_lucro = {"lucro": lucro, "preco": preco_venda}
        centavos += intervalo
    resultados.extend(simulacoes)

# TABELA FINAL
st.markdown("## 🧾 Resultado Consolidado")
df = pd.DataFrame(resultados)

# Alerta de lucro negativo
if (df["Lucro R$"] < 0).any():
    st.warning("⚠️ Atenção: existem cenários com prejuízo (lucro negativo). Avalie os descontos com cuidado.")

# Gráfico de lucro por produto
st.markdown("### 📈 Gráfico de Lucro por Produto")
fig = px.line(df, x="Desconto", y="Lucro R$", color="Produto", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Formatar DataFrame
df_formatado = df.copy()
df_formatado["Preço Venda"] = df_formatado["Preço Venda"].map(lambda x: f"R$ {x:.4f}")
df_formatado["Imposto"] = df_formatado["Imposto"].map(lambda x: f"R$ {x:.4f}")
df_formatado["Custo Total"] = df_formatado["Custo Total"].map(lambda x: f"R$ {x:.4f}")
df_formatado["Lucro R$"] = df_formatado["Lucro R$"].map(lambda x: f"R$ {x:.4f}")
df_formatado["Lucro %"] = df_formatado["Lucro %"].map(lambda x: f"{x:.2%}")
st.dataframe(df_formatado, use_container_width=True)

# MELHOR POR PRODUTO
st.markdown("---")
st.subheader("🏆 Melhor Preço por Produto")
melhores = df.loc[df.groupby("Produto")["Lucro R$"].idxmax()].reset_index(drop=True)
melhores["Lucro %"] = melhores["Lucro %"].map(lambda x: f"{x:.2%}")
melhores["Preço Venda"] = melhores["Preço Venda"].map(lambda x: f"R$ {x:.4f}")
melhores["Lucro R$"] = melhores["Lucro R$"].map(lambda x: f"R$ {x:.4f}")
st.dataframe(melhores, use_container_width=True)

# EXPORTAR EXCEL
st.markdown("---")
st.subheader("📥 Exportar Simulação")
def gerar_excel():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Simulacoes", index=False)
        melhores.to_excel(writer, sheet_name="Resumo", index=False)
    return buffer.getvalue()

st.download_button("📤 Baixar Excel com Simulações", gerar_excel(), file_name="simulacao_licitacao.xlsx")

# SALVAR E CARREGAR JSON
st.markdown("---")
st.subheader("💾 Salvar ou Recarregar Simulações")
col1, col2 = st.columns(2)

with col1:
    json_data = json.dumps(st.session_state.produtos)
    st.download_button("💾 Baixar Configuração (.json)", json_data, file_name="simulacao.json")

with col2:
    file = st.file_uploader("📂 Carregar arquivo .json", type="json")
    if file:
        st.session_state.produtos = json.load(file)
        st.success("Produtos carregados com sucesso. Atualize a página para ver os dados.")

