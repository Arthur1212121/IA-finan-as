import json
import os
import re
from datetime import datetime
import streamlit as st

ARQUIVO = "financas.json"
SALDO_INICIAL = 380.00

# Configuração da página Web
st.set_page_config(page_title="Minha IA Financeira", page_icon="💰", layout="centered")

# ============================================================
# BANCO DE DADOS LOCAL
# ============================================================

def carregar_dados():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            try:
                return json.load(arquivo)
            except json.JSONDecodeError:
                pass
    return {"historico": []}

def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

def calcular_saldo(dados):
    total = SALDO_INICIAL
    for m in dados["historico"]:
        if m["tipo"] == "entrada":
            total += m["valor"]
        elif m["tipo"] == "saida":
            total -= m["valor"]
    return total

def adicionar_movimentacao(dados, tipo, valor, descricao):
    if valor <= 0:
        return False, "O valor precisa ser maior que zero!"

    movimentacao = {
        "id": len(dados["historico"]) + 1,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo": tipo,
        "valor": round(valor, 2),
        "descricao": descricao
    }

    dados["historico"].append(movimentacao)
    salvar_dados(dados)
    return True, f"Registrado: {tipo.upper()} de R$ {valor:.2f}"

def processar_texto(dados, texto):
    texto = texto.lower().strip()
    match_valor = re.search(r'(\d+([.,]\d{1,2})?)', texto)
    if not match_valor:
        return False, "Não encontrei nenhum valor numérico no texto."

    valor = float(match_valor.group(1).replace(",", "."))

    palavras_entrada = ["recebi", "ganhei", "deposito", "entrada", "recebidos", "salario"]
    palavras_saida = ["gastei", "paguei", "saida", "gastos", "comprei"]

    tipo = None
    if any(p in texto for p in palavras_entrada):
        tipo = "entrada"
    elif any(p in texto for p in palavras_saida):
        tipo = "saida"

    if tipo:
        return adicionar_movimentacao(dados, tipo, valor, texto)
    
    return False, "Não entendi se foi uma entrada ou gasto. Use termos como 'gastei' ou 'recebi'."

# ============================================================
# INTERFACE WEB (STREAMLIT)
# ============================================================

dados = carregar_dados()
saldo_atual = calcular_saldo(dados)

st.title("🤖 IA Financeira Personalizada")

# Exibição dos Cards Principais
col1, col2 = st.columns(2)
col1.metric("Saldo Atual", f"R$ {saldo_atual:.2f}")

entradas = sum(m["valor"] for m in dados["historico"] if m["tipo"] == "entrada")
saidas = sum(m["valor"] for m in dados["historico"] if m["tipo"] == "saida")
col2.metric("Gasto Total", f"R$ {saidas:.2f}", delta=f"+ R$ {entradas:.2f} recebidos")

st.divider()

# Campo para o usuário conversar / enviar comandos
st.subheader("💬 Digite uma movimentação")
comando = st.text_input("Exemplo: 'gastei 30 no mercado' ou 'recebi 150 de freela'", key="input_comando")

if st.button("Enviar"):
    if comando:
        sucesso, mensagem = processar_texto(dados, comando)
        if sucesso:
            st.success(mensagem)
            st.rerun()
        else:
            st.warning(mensagem)
    else:
        st.info("Digite alguma mensagem antes de enviar.")

st.divider()

# Histórico
st.subheader("📋 Histórico de Transações")
if dados["historico"]:
    for m in reversed(dados["historico"]):
        sinal = "🟢 +" if m["tipo"] == "entrada" else "🔴 -"
        st.write(f"**{m['id']}** | {m['data']} | {sinal} R$ {m['valor']:.2f} — *{m['descricao']}*")
else:
    st.write("Nenhuma movimentação registrada ainda.")
