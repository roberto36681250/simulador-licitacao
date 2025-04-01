
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Preços para Licitação", layout="wide")
st.title("Simulador de Preços para Licitação Pública")

st.sidebar.header("Parâmetros Gerais")
desconto_max = st.sidebar.number_input("Desconto máximo (R$)", value=0.5, step=0.01, format="%.2f")
intervalo = st.sidebar.number_input("Intervalo (R$)", value=0.01, step=0.01, format="%.2f")

st.markdown("---")
st.subheader("Cadastro de Produto")

produto = st.text_input("Nome do Produto", "Fralda P")
custo = st.number_input("Preço de Custo (R$)", value=1.30, step=0.01, format="%.2f")
frete = st.number_input("Frete (R$)", value=0.10, step=0.01, format="%.2f")
imposto = st.number_input("Imposto sobre venda (%)", value=10.0, step=0.1, format="%.2f") / 100
lucro_desejado = st.number_input("Lucro real desejado (%)", value=15.0, step=0.1, format="%.2f") / 100

# Cálculo do Preço Ideal
try:
    preco_ideal = (custo + frete) / (1 - (imposto + (1 - imposto) * lucro_desejado))
    st.success(f"Preço de venda ideal: R$ {preco_ideal:.4f}")
except ZeroDivisionError:
    preco_ideal = 0
    st.error("Erro no cálculo do preço ideal. Verifique os parâmetros.")

# Simulação de descontos
dados = []
centavos = 0.0
while centavos <= desconto_max:
    preco_venda = preco_ideal - centavos
    imp = preco_venda * imposto
    custo_total = custo + frete + imp
    lucro = preco_venda - custo_total
    lucro_perc = lucro / custo_total if custo_total else 0
    dados.append({
        "Desconto": f"R$ {centavos:.2f}",
        "Preço Venda": preco_venda,
        "Imposto": imp,
        "Custo Total": custo_total,
        "Lucro R$": lucro,
        "Lucro %": lucro_perc
    })
    centavos += intervalo

# Exibir tabela
st.markdown("---")
st.subheader("Simulação de Descontos")
df = pd.DataFrame(dados)
df["Lucro %"] = df["Lucro %"].apply(lambda x: f"{x:.2%}")
df["Preço Venda"] = df["Preço Venda"].apply(lambda x: f"R$ {x:.4f}")
df["Imposto"] = df["Imposto"].apply(lambda x: f"R$ {x:.4f}")
df["Custo Total"] = df["Custo Total"].apply(lambda x: f"R$ {x:.4f}")
df["Lucro R$"] = df["Lucro R$"].apply(lambda x: f"R$ {x:.4f}")
st.dataframe(df, use_container_width=True)

# Melhor lucro
melhor_linha = max(dados, key=lambda x: x["Lucro R$"])
st.markdown("---")
st.success(f"Melhor lucro: R$ {melhor_linha['Lucro R$']:.4f} com preço de venda R$ {melhor_linha['Preço Venda']:.4f}")
