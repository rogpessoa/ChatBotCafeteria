import json
import os
from datetime import datetime
from nltk.stem import RSLPStemmer

PASTA_PEDIDO = "./pedido"
ARQUIVO_PEDIDO = os.path.join(PASTA_PEDIDO, "pedido.json")
stemmer = RSLPStemmer()


def registrar_pedido(item, modo_entrega):
    pedido = {
        "item": item,
        "modo_entrega": modo_entrega,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if not os.path.exists(PASTA_PEDIDO):
        os.makedirs(PASTA_PEDIDO)

    if os.path.exists(ARQUIVO_PEDIDO):
        with open(ARQUIVO_PEDIDO, "r", encoding="utf-8") as f:
            pedidos = json.load(f)
    else:
        pedidos = []

    pedidos.append(pedido)

    with open(ARQUIVO_PEDIDO, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=4)


def buscar_pedidos_por_tag(tag_usuario):
    tag_proc = stemmer.stem(tag_usuario.lower())

    if not os.path.exists(ARQUIVO_PEDIDO):
        return []

    with open(ARQUIVO_PEDIDO, "r", encoding="utf-8") as f:
        pedidos = json.load(f)

    resultados = []
    for pedido in pedidos:
        palavras = pedido["item"].lower().split()
        palavras_processadas = [stemmer.stem(p) for p in palavras]
        if tag_proc in palavras_processadas:
            resultados.append(pedido)

    return resultados
