from flask import Flask, render_template, request, Response, session
import requests
from nltk.stem import RSLPStemmer
import json
import secrets

URL_ROBO = "http://localhost:5000"
URL_ROBO_ALIVE = f"{URL_ROBO}/alive"
URL_ROBO_RESPONDER = f"{URL_ROBO}/responder"

CONFIANCA_MINIMA = 0.7

chat = Flask(__name__)
chat.secret_key = secrets.token_hex(16)
stemmer = RSLPStemmer()

indice_tags_chat = {}

#Busca as mensagens de pedido
with open("C://Users//ROGERIOPESSOAANDRADE//Documents//PARTICULAR//Pos_IFba/MODULO_2/SistemaEspecialistaWeb//cafeteria//pedido/msg_pedido.json", "r", encoding="utf-8") as msg_pedido:
    pedidos = json.load(msg_pedido).get("mensagens", [])
    msg_pedido.close()

#Busca a base de conhecimento
with open("C://Users//ROGERIOPESSOAANDRADE//Documents//PARTICULAR//Pos_IFba/MODULO_2/SistemaEspecialistaWeb//cafeteria//base_conhecimento/base.json", "r", encoding="utf-8") as f:
    dados = json.load(f)
    f.close()

#Faz varredura no arquivo de base para encontrar as tags.
for item in dados["base_conhecimento"]:
    for tag in item["tags"]:
        tag_processada = stemmer.stem(tag.lower())
        if tag_processada not in indice_tags_chat:
            indice_tags_chat[tag_processada] = []
        indice_tags_chat[tag_processada].append(item)

#Função que busca as tags
def obter_tags_chat():
    return list(indice_tags_chat.keys())

def buscar_tag_para_chat(termo_usuario):
    termo_processado = stemmer.stem(termo_usuario.lower())
    return indice_tags_chat.get(termo_processado, [])

# Função que processa o pedido via sessão
def fazer_pedido_chat(pergunta):
    if "estado_pedido" not in session:
        session["estado_pedido"] = "esperando_item"
        return "🛎️ Qual item você gostaria de pedir?"

    estado = session["estado_pedido"]

    if estado == "esperando_item":
        session["pedido_item"] = pergunta
        session["estado_pedido"] = "esperando_entrega"
        return "📦 Você deseja retirar no local ou delivery?"

    elif estado == "esperando_entrega":
        if pergunta.lower() not in ["retirar", "delivery"]:
            return "Por favor, responda com 'retirar' ou 'delivery'."

        item = session.pop("pedido_item", "")
        entrega = pergunta
        session.pop("estado_pedido", None)
        return f"✅ Pedido registrado com sucesso!\n📝 Item: {item}\n📦 Entrega: {entrega}"

    return "Erro no processo do pedido. Por favor, tente novamente."

def responder_usuario_por_tag_chat(entrada_usuario):
    resultados = buscar_tag_para_chat(entrada_usuario)
    if resultados:
        resposta = f"\n🔎 Resultados para '{entrada_usuario}':\n"
        for item in resultados:
            resposta += f"- {item['nome']}: {item['descricao']}\n"
    else:
        resposta = f"\n❌ Nenhum resultado encontrado para '{entrada_usuario}'."
    return resposta

def acessar_robo(url, para_enviar=None):
    try:
        resposta = requests.post(url, json=para_enviar) if para_enviar else requests.get(url)
        return True, resposta.json()
    except Exception as e:
        print(f"Erro acessando backend: {str(e)}")
        return False, None

def robo_alive():
    sucesso, resposta = acessar_robo(URL_ROBO_ALIVE)
    return sucesso and resposta["alive"] == "sim"

def perguntar_robo(pergunta):
    sucesso, resposta = acessar_robo(URL_ROBO_RESPONDER, {"pergunta": pergunta})
    if sucesso and resposta["confianca"] >= CONFIANCA_MINIMA:
        return resposta["resposta"]
    return "Infelizmente ainda não sei responder essa pergunta."

@chat.get("/")
def index():
    return render_template("index.html")

#Rota que interage com usuario

@chat.post("/responder")
def get_resposta():
    conteudo = request.json
    pergunta = conteudo.get("pergunta", "").strip().lower()
    tags_processadas = obter_tags_chat()
    pergunta_processada = stemmer.stem(pergunta)
    if pergunta in pedidos or session.get("estado_pedido"):
        resposta = fazer_pedido_chat(pergunta)
    elif pergunta_processada in tags_processadas:
        resposta = responder_usuario_por_tag_chat(pergunta)
    else:
        resposta = perguntar_robo(pergunta)

    return Response(json.dumps({"resposta": resposta}), status=200, mimetype="application/json")

if __name__ == "__main__":
    chat.run(host="0.0.0.0", port=5001, debug=True)
