import json
import os
import re
from datetime import datetime

ARQUIVO = "financas.json"
SALDO_INICIAL = 380.00


# ============================================================
# MEMÓRIA E PERSISTÊNCIA
# ============================================================

def carregar_dados():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            try:
                return json.load(arquivo)
            except json.JSONDecodeError:
                pass

    dados = {
        "historico": []
    }

    salvar_dados(dados)
    return dados


def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


# ============================================================
# OPERAÇÕES FINANCEIRAS (PRECISÃO GARANTIDA)
# ============================================================

def calcular_saldo(dados):
    """
    Garante que o saldo seja SEMPRE 100% preciso, recalculando 
    com base no histórico completo e saldo inicial.
    """
    total = SALDO_INICIAL
    for m in dados["historico"]:
        if m["tipo"] == "entrada":
            total += m["valor"]
        elif m["tipo"] == "saida":
            total -= m["valor"]
    return total


def adicionar_movimentacao(dados, tipo, valor, descricao):
    if valor <= 0:
        print("🤖 IA: O valor precisa ser maior que zero!")
        return False

    movimentacao = {
        "id": len(dados["historico"]) + 1,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo": tipo,
        "valor": round(valor, 2),
        "descricao": descricao
    }

    dados["historico"].append(movimentacao)
    salvar_dados(dados)
    return True


# ============================================================
# INTERFACE E EXIBIÇÃO
# ============================================================

def mostrar_saldo(dados):
    saldo = calcular_saldo(dados)
    print(f"\n💰 Seu saldo atual é: R$ {saldo:.2f}")


def mostrar_historico(dados):
    print("\n========== HISTÓRICO ==========")

    if not dados["historico"]:
        print("Nenhuma movimentação registrada.")
        return

    for movimento in dados["historico"]:
        sinal = "+" if movimento["tipo"] == "entrada" else "-"

        print(
            f"{movimento['id']} | "
            f"{movimento['data']} | "
            f"{sinal} R$ {movimento['valor']:.2f} | "
            f"{movimento['descricao']}"
        )

    print("===============================")


def mostrar_resumo(dados):
    entradas = sum(
        m["valor"] for m in dados["historico"] if m["tipo"] == "entrada"
    )

    saidas = sum(
        m["valor"] for m in dados["historico"] if m["tipo"] == "saida"
    )

    saldo = calcular_saldo(dados)

    print("\n========== RESUMO ==========")
    print(f"Saldo Inicial:  R$ {SALDO_INICIAL:.2f}")
    print(f"Total recebido: R$ {entradas:.2f}")
    print(f"Total gasto:    R$ {saidas:.2f}")
    print(f"Saldo atual:    R$ {saldo:.2f}")
    print("============================")


def mostrar_ajuda():
    print("""
========== COMANDOS ==========

Você pode falar naturalmente comigo, por exemplo:
 - "recebi 50 da pizzaria"
 - "gastei 12 com almoço"
 - "R$ 100 de freela"

Ou usar comandos diretos:
 - saldo       : Mostra seu saldo atual
 - historico   : Mostra todas as movimentações
 - resumo      : Resumo de entradas e saídas
 - ajuda       : Mostra esta lista
 - sair        : Fecha o programa
===============================
""")


# ============================================================
# PROCESSADOR DE LINGUAGEM NATURAL (IA BÁSICA)
# ============================================================

def processar_texto_livre(dados, mensagem):
    """
    Analisa frases do usuário e extrai valores e intenções automaticamente.
    """
    # Procura por números no texto (ex: 50, 12.50, 12,50)
    match_valor = re.search(r'(\d+([.,]\d{1,2})?)', mensagem)
    if not match_valor:
        return False

    # Converte o valor encontrado para float
    valor_str = match_valor.group(1).replace(",", ".")
    valor = float(valor_str)

    # Define se é entrada ou saída baseado em palavras-chave
    palavras_entrada = ["recebi", "ganhei", "deposito", "entrada", "recebidos", "salario"]
    palavras_saida = ["gastei", "paguei", "saida", "gastos", "comprei"]

    tipo = None
    if any(p in mensagem for p in palavras_entrada):
        tipo = "entrada"
    elif any(p in mensagem for p in palavras_saida):
        tipo = "saida"

    if tipo:
        # Usa o resto do texto como descrição
        descricao = mensagem
        if adicionar_movimentacao(dados, tipo, valor, descricao):
            print(f"\n🤖 IA: Entendi! Registrei uma {tipo} de R$ {valor:.2f}.")
            mostrar_saldo(dados)
        return True

    return False


def interpretar_comando(dados, mensagem):
    msg_limpa = mensagem.lower().strip()

    if msg_limpa in ["saldo", "quanto tenho", "quanto eu tenho"]:
        mostrar_saldo(dados)
        return

    if msg_limpa in ["historico", "histórico", "extrato"]:
        mostrar_historico(dados)
        return

    if msg_limpa in ["resumo", "relatorio", "relatório"]:
        mostrar_resumo(dados)
        return

    if msg_limpa in ["ajuda", "help"]:
        mostrar_ajuda()
        return

    # Tenta interpretar como texto livre (ex: "gastei 20 no mercado")
    if processar_texto_livre(dados, msg_limpa):
        return

    print("\n🤖 IA: Não entendi o comando.")
    print("Digite 'ajuda' para ver como interagir.")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    dados = carregar_dados()

    print("======================================")
    print("       🤖 MINHA IA FINANCEIRA")
    print("======================================")
    mostrar_saldo(dados)

    while True:
        mensagem = input("\nVocê: ").strip()

        if not mensagem:
            continue

        if mensagem.lower() in ["sair", "exit", "quit"]:
            print("\n🤖 IA: Dados salvos com segurança.")
            mostrar_saldo(dados)
            print("Até mais! 👋")
            break

        interpretar_comando(dados, mensagem)


if __name__ == "__main__":
    main()