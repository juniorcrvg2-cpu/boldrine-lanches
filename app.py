import os
from urllib.parse import quote
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

WHATSAPP = os.getenv("WHATSAPP_NUMBER", "5521988000094")

PRECOS = {
    ("NORMAL", "Salsicha"): 18.00,
    ("NORMAL", "Linguiça"): 20.00,
    ("SUPER", "Salsicha"): 23.00,
    ("SUPER", "Linguiça"): 25.00,
}

PROMOCOES_QUINTA = {
    ("NORMAL", "Salsicha"): 32.00,
    ("NORMAL", "Linguiça"): 35.00,
    ("SUPER", "Salsicha"): 42.00,
    ("SUPER", "Linguiça"): 45.00,
}

MOLHOS = [
    "Billy Jack",
    "Cheddar",
    "Ketchup",
    "Ketchup de goiabada",
    "Maionese",
    "Maionese com alho",
    "Mostarda"
]

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


def eh_quinta_feira():
    return datetime.now().weekday() == 1


@app.route("/", methods=["GET"])
def inicio():

    promocao_ativa = eh_quinta_feira()

    return render_template(
        "index.html",
        molhos=MOLHOS,
        acompanhamentos=ACOMPANHAMENTOS,
        promocao_ativa=promocao_ativa,
        promocoes=(
            PROMOCOES_QUINTA
            if promocao_ativa
            else {}
        )
    )


@app.route("/pedido", methods=["POST"])
def pedido():

    tamanho = request.form.get("tamanho")
    tipo = request.form.get("tipo")

    try:
        quantidade = int(
            request.form.get("quantidade", "1")
        )
    except ValueError:
        quantidade = 1

    if quantidade < 1:
        quantidade = 1

    preco = PRECOS.get(
        (tamanho, tipo)
    )

    if preco is None:
        return "Pedido inválido.", 400

    nome = request.form.get(
        "nome", ""
    ).strip()

    endereco = request.form.get(
        "endereco", ""
    ).strip()

    pagamento = request.form.get(
        "pagamento", ""
    ).strip()

    observacoes = request.form.get(
        "observacoes", ""
    ).strip()

    molhos = request.form.getlist(
        "molhos"
    )

    acompanhamentos = request.form.getlist(
        "acompanhamentos"
    )

    total = preco * quantidade

    if tamanho == "NORMAL":
        tamanho_cm = "14 CM"
    else:
        tamanho_cm = "32 CM"

    mensagem = [
        "🌭 *NOVO PEDIDO — BOLDRINE LANCHES*",
        "",
        f"👤 *Cliente:* {nome or 'Não informado'}",
        f"📍 *Endereço:* {endereco or 'Não informado'}",
        "",
        "🛒 *ITENS DO PEDIDO*",
        "",
        f"1. *{tamanho} — {tipo}*",
        f"📏 Tamanho: {tamanho_cm}",
        f"🔢 Quantidade: {quantidade}",
        f"💰 Valor unitário: R$ {preco:.2f}".replace(".", ","),
        f"💵 Subtotal: R$ {total:.2f}".replace(".", ","),
        "",
        "🥫 *Molhos:* "
        + (
            ", ".join(molhos)
            if molhos
            else "Nenhum"
        ),
        "",
        "🥗 *Acompanhamentos:* "
        + (
            ", ".join(acompanhamentos)
            if acompanhamentos
            else "Nenhum"
        ),
        "",
        f"💳 *Pagamento:* "
        f"{pagamento or 'Não informado'}"
    ]

    if observacoes:
        mensagem.extend([
            "",
            f"📝 *Observações:* {observacoes}"
        ])

    mensagem.extend([
        "",
        f"💵 *TOTAL DO PEDIDO: R$ {total:.2f}*".replace(".", ","),
        "",
        "❤️ Obrigado por pedir na Boldrine Lanches!"
    ])

    texto = "\n".join(mensagem)

    whatsapp_url = (
        f"https://wa.me/{WHATSAPP}"
        f"?text={quote(texto)}"
    )

    return render_template(
        "sucesso.html",
        whatsapp_url=whatsapp_url
    )


@app.route("/health")
def health():

    return {
        "status": "ok",
        "app": "Boldrine Lanches"
    }


if __name__ == "__main__":

    port = int(
        os.getenv("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )