import os
from urllib.parse import quote
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request


app = Flask(__name__)


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

WHATSAPP = os.getenv(
    "WHATSAPP_NUMBER",
    "5521988000094"
)

FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")


# ==========================================================
# PREÇOS NORMAIS
# ==========================================================

PRECOS = {
    ("NORMAL", "Salsicha"): 18.00,
    ("NORMAL", "Linguiça"): 20.00,
    ("SUPER", "Salsicha"): 23.00,
    ("SUPER", "Linguiça"): 25.00,
}


# ==========================================================
# PROMOÇÕES DE QUINTA-FEIRA
# ==========================================================

PROMOCOES_QUINTA = {
    ("NORMAL", "Salsicha"): 32.00,
    ("NORMAL", "Linguiça"): 35.00,
    ("SUPER", "Salsicha"): 42.00,
    ("SUPER", "Linguiça"): 45.00,
}


# ==========================================================
# MOLHOS
# ==========================================================

MOLHOS = [
    "Billy Jack",
    "Cheddar",
    "Ketchup",
    "Ketchup de goiabada",
    "Maionese",
    "Maionese com alho",
    "Mostarda"
]


# ==========================================================
# ACOMPANHAMENTOS
# ==========================================================

ACOMPANHAMENTOS = [
    "Alho torrado",
    "Azeitona",
    "Batata palha",
    "Cebola",
    "Ervilha",
    "Milho",
    "Ovo de codorna",
    "Passas",
    "Pimentão",
    "Queijo ralado",
    "Tomate"
]


# ==========================================================
# DATA E HORA DO BRASIL
# ==========================================================

def agora_brasil():
    """
    Retorna a data e hora atual no horário de Brasília.
    """
    return datetime.now(FUSO_HORARIO)


# ==========================================================
# VERIFICA SE É QUINTA-FEIRA
# ==========================================================

def eh_quinta_feira():
    """
    Segunda-feira = 0
    Terça-feira   = 1
    Quarta-feira  = 2
    Quinta-feira  = 3
    Sexta-feira   = 4
    Sábado        = 5
    Domingo       = 6
    """

    return agora_brasil().weekday() == 3


# ==========================================================
# PÁGINA INICIAL
# ==========================================================

@app.route("/", methods=["GET"])
def inicio():

    promocao_ativa = eh_quinta_feira()

    if promocao_ativa:
        promocoes = PROMOCOES_QUINTA.copy()
    else:
        promocoes = {}

    return render_template(
        "index.html",
        molhos=MOLHOS,
        acompanhamentos=ACOMPANHAMENTOS,
        promocao_ativa=promocao_ativa,
        promocoes=promocoes
    )


# ==========================================================
# FINALIZAÇÃO DO PEDIDO
# ==========================================================

@app.route("/pedido", methods=["POST"])
def pedido():

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    endereco = request.form.get(
        "endereco",
        ""
    ).strip()

    pagamento = request.form.get(
        "pagamento",
        ""
    ).strip()

    observacoes = request.form.get(
        "observacoes",
        ""
    ).strip()

    tamanho = request.form.get(
        "tamanho",
        ""
    ).strip()

    tipo = request.form.get(
        "tipo",
        ""
    ).strip()


    # ======================================================
    # QUANTIDADE
    # ======================================================

    try:

        quantidade = int(
            request.form.get(
                "quantidade",
                "1"
            )
        )

    except (ValueError, TypeError):

        quantidade = 1


    if quantidade < 1:
        quantidade = 1


    # ======================================================
    # VALIDAÇÃO DO PRODUTO
    # ======================================================

    chave_produto = (
        tamanho,
        tipo
    )

    preco_normal = PRECOS.get(
        chave_produto
    )


    if preco_normal is None:

        return "Pedido inválido.", 400


    # ======================================================
    # VERIFICA SE A PROMOÇÃO ESTÁ ATIVA
    # ======================================================

    promocao_ativa = eh_quinta_feira()


    # ======================================================
    # PREÇO DO PEDIDO
    #
    # Na quinta-feira:
    # Normal Salsicha = R$ 32,00
    # Normal Linguiça = R$ 35,00
    # Super Salsicha  = R$ 42,00
    # Super Linguiça  = R$ 45,00
    #
    # A promoção representa 2 lanches.
    # ======================================================

    usando_promocao = False

    if promocao_ativa and quantidade == 2:

        preco_promocao = PROMOCOES_QUINTA.get(
            chave_produto
        )

        if preco_promocao is not None:

            preco = preco_promocao
            subtotal = preco_promocao
            usando_promocao = True

        else:

            preco = preco_normal
            subtotal = preco_normal * quantidade

    else:

        preco = preco_normal
        subtotal = preco_normal * quantidade


    # ======================================================
    # COMPLEMENTOS
    # ======================================================

    molhos = request.form.getlist(
        "molhos"
    )

    acompanhamentos = request.form.getlist(
        "acompanhamentos"
    )


    # ======================================================
    # ORDENAÇÃO ALFABÉTICA
    # ======================================================

    molhos_ordenados = sorted(
        molhos,
        key=lambda x: x.lower()
    )

    acompanhamentos_ordenados = sorted(
        acompanhamentos,
        key=lambda x: x.lower()
    )


    # ======================================================
    # TAXA DE CARTÃO
    #
    # A taxa é cobrada somente UMA VEZ por pedido.
    # ======================================================

    if pagamento in [
        "Cartão de Débito",
        "Cartão de Crédito"
    ]:

        taxa_cartao = 1.00

    else:

        taxa_cartao = 0.00


    # ======================================================
    # TOTAL DO PEDIDO
    # ======================================================

    total = subtotal + taxa_cartao


    # ======================================================
    # TAMANHO EM CM
    # ======================================================

    if tamanho == "NORMAL":

        tamanho_cm = "14 CM"

    elif tamanho == "SUPER":

        tamanho_cm = "32 CM"

    else:

        tamanho_cm = "Não informado"


    # ======================================================
    # MENSAGEM WHATSAPP
    # ======================================================

    mensagem = []

    mensagem.append(
        "NOVO PEDIDO - BOLDRINE LANCHES"
    )

    mensagem.append("")


    # ======================================================
    # CLIENTE
    # ======================================================

    mensagem.append(
        f"Cliente: {nome or 'Não informado'}"
    )

    mensagem.append(
        f"Endereço: {endereco or 'Não informado'}"
    )

    mensagem.append("")


    # ======================================================
    # PEDIDO
    # ======================================================

    mensagem.append(
        "PEDIDO"
    )

    mensagem.append("")


    if usando_promocao:

        mensagem.append(
            f"PROMOÇÃO DE QUINTA - 2 {tamanho} {tipo}"
        )

        mensagem.append(
            f"Tamanho: {tamanho_cm}"
        )

        mensagem.append(
            "Quantidade: 2 lanches"
        )

        mensagem.append(
            f"Valor da promoção: R$ {preco:.2f}".replace(
                ".",
                ","
            )
        )

        mensagem.append(
            f"Subtotal: R$ {subtotal:.2f}".replace(
                ".",
                ","
            )
        )

    else:

        mensagem.append(
            f"1. {tamanho} - {tipo}"
        )

        mensagem.append(
            f"Tamanho: {tamanho_cm}"
        )

        mensagem.append(
            f"Quantidade: {quantidade}"
        )

        mensagem.append(
            f"Valor unitário: R$ {preco:.2f}".replace(
                ".",
                ","
            )
        )

        mensagem.append(
            f"Subtotal: R$ {subtotal:.2f}".replace(
                ".",
                ","
            )
        )


    mensagem.append("")


    # ======================================================
    # MOLHOS
    # ======================================================

    mensagem.append(
        "Molhos:"
    )

    if molhos_ordenados:

        mensagem.append(
            " | ".join(
                molhos_ordenados
            )
        )

    else:

        mensagem.append(
            "Nenhum"
        )

    mensagem.append("")


    # ======================================================
    # ACOMPANHAMENTOS
    # ======================================================

    mensagem.append(
        "Acompanhamentos:"
    )

    if acompanhamentos_ordenados:

        mensagem.append(
            " | ".join(
                acompanhamentos_ordenados
            )
        )

    else:

        mensagem.append(
            "Nenhum"
        )


    # ======================================================
    # OBSERVAÇÕES
    # ======================================================

    if observacoes:

        mensagem.append("")

        mensagem.append(
            f"Observações: {observacoes}"
        )


    # ======================================================
    # PAGAMENTO
    # ======================================================

    mensagem.append("")

    mensagem.append(
        "----------------"
    )

    mensagem.append("")

    mensagem.append(
        f"Pagamento: "
        f"{pagamento or 'Não informado'}"
    )


    # ======================================================
    # TAXA DO CARTÃO
    # ======================================================

    if taxa_cartao > 0:

        mensagem.append(
            f"Taxa cartão: R$ {taxa_cartao:.2f}".replace(
                ".",
                ","
            )
        )


    # ======================================================
    # TOTAL
    # ======================================================

    mensagem.append("")

    mensagem.append(
        f"TOTAL DO PEDIDO: "
        f"R$ {total:.2f}".replace(
            ".",
            ","
        )
    )

    mensagem.append("")


    mensagem.append(
        "Obrigado por pedir na Boldrine Lanches!"
    )


    # ======================================================
    # TRANSFORMA A LISTA EM TEXTO
    # ======================================================

    texto = "\n".join(
        mensagem
    )


    # ======================================================
    # LINK WHATSAPP
    # ======================================================

    whatsapp_url = (
        f"https://wa.me/{WHATSAPP}"
        f"?text={quote(texto)}"
    )


    # ======================================================
    # PÁGINA DE SUCESSO
    # ======================================================

    return render_template(
        "sucesso.html",
        whatsapp_url=whatsapp_url
    )


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "app": "Boldrine Lanches"
    }


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )