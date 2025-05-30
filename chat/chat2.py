from flask import Flask, render_template, request, Response
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
with open("C://Users//ROGERIOPESSOAANDRADE//Documents//PARTICULAR//Pos_IFba/MODULO_2/SistemaEspecialistaWeb//cafeteria//pedido\msg_pedido.json", "r", encoding="utf-8") as f:
    pedidos = json.load(f).get("mensagens", [])
    f.close()

#Busca a base de conheciento
with open("C://Users//ROGERIOPESSOAANDRADE//Documents//PARTICULAR//Pos_IFba\MODULO_2//SistemaEspecialistaWeb//cafeteria//base_conhecimento//base.json", "r", encoding="utf-8") as f:
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
    resultados = indice_tags_chat.get(termo_processado, [])

    return resultados

#Função que faz pedido do usuario
def fazer_pedido_chat():
    pedido_feito = ""
    print("\n🛎️ Vamos fazer seu pedido! Você pode cancelar digitando 'cancelar'.\n")
    item = input("🤖 Qual item você gostaria de pedir? ").strip()
    if item.lower() == "cancelar":
        print("🤖 Pedido cancelado.")
        return

    entrega = input("🤖 Você deseja retirar no local ou delivery? ").strip().lower()
    if entrega == "cancelar":
        print("🤖 Pedido cancelado.")
        return
    while entrega not in ["retirar", "delivery", "local"]:
        entrega = input("🤖 Por favor, responda com 'retirar' ou 'delivery': ").strip().lower()
        if entrega == "cancelar":
            print("🤖 Pedido cancelado.")
            return
    pedido_feito = f"\n✅ Pedido registrado com sucesso!\n📝 Item: {item}\n📦 Entrega: {entrega}\n"
    return pedido_feito



def responder_usuario_por_tag_chat(entrada_usuario):
    resultados = buscar_tag_para_chat(entrada_usuario)
    if resultados:
        resposta = f"\n🔎 Resultados para '{entrada_usuario}':\n"
        for item in resultados:
            resposta += f"- {item['nome']}: {item['descricao']}\n"
    else:
        resposta = f"\n❌ Nenhum resultado encontrado para '{entrada_usuario}'."

    return resposta


def acessar_robo(url, para_enviar = None): #Se tiver algo para enviar o metodo é post se nao, get.
    sucesso, resposta = False, None

    try:
        if para_enviar: #Se para enviar contiver algum json ele entra aqui e devolve um post
            resposta = requests.post(url, json=para_enviar)
        else: #Se nao tiver nada é um get
            resposta = requests.get(url)
        
        resposta = resposta.json()
        sucesso = True
        
    except Exception as e:
        print(f"Erro acessando backend: {str(e)}")
        
    return sucesso, resposta


#Função para verificar se a URL do robo está online
def robo_alive():
    sucesso, resposta = acessar_robo(URL_ROBO_ALIVE)
    return sucesso and resposta["alive"] == "sim"


def perguntar_robo(pergunta):
    sucesso, resposta = acessar_robo(URL_ROBO_RESPONDER, {"pergunta": pergunta})
    mensagem = "Infelizmente ainda não sei responder essa pergunta."
    if sucesso and resposta["confianca"] >= CONFIANCA_MINIMA:
        mensagem = resposta["resposta"]
    return mensagem
    #Se a confiança for maior que a minima ele muda a mensagem padrão para a mensagem enviada pelo robo


@chat.get("/")
def index():
    return render_template("index.html")


#rota que interage com o chat
@chat.post("/responder")
def get_resposta():
    resposta = ""
    conteudo = request.json
    pergunta = conteudo["pergunta"]
    tags_processadas = obter_tags_chat()
    pergunta_processada = stemmer.stem(pergunta)
    #Se o ususario quiser fazer pedido
    if pergunta in pedidos:
        fazer_pedido_chat()
        return Response(json.dumps({"resposta": resposta}), status=200, mimetype="application/json")
    #Se usuario digitou alguma tag
    if pergunta_processada in tags_processadas:
        resposta = responder_usuario_por_tag_chat(pergunta)
        return Response(json.dumps({"resposta": resposta}), status=200, mimetype="application/json")
    #Responder as perguntas basicas
    else:
        resposta = perguntar_robo(pergunta)
        return Response(json.dumps({"resposta": resposta}), status=200, mimetype="application/json")


if __name__ == "__main__":
    chat.run(
        host = "0.0.0.0",
        port = 5001,
        debug=True
    )
