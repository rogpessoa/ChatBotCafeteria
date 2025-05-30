from chatterbot import ChatBot
import json
from processar_prod import buscar_por_tag, obter_tags_conhecidas
from nltk.stem import RSLPStemmer
import os
from pedido.pedido import registrar_pedido, buscar_pedidos_por_tag


# CAMINHO_BD = "."
# BD_ARTIGOS = f"{CAMINHO_BD}/artigos.sqlite3"
NOME_ROBO = "Cafeteria Wesley Cafezão"
BD_ROBO = "chat.sqlite3"
CONFIANCA_MINIMA = 0.7


stemmer = RSLPStemmer()

def inicializar():
    sucesso, robo = False, None

    try:
        robo = ChatBot(NOME_ROBO, read_only=True, storage_adapter="chatterbot.storage.SQLStorageAdapter",
                        database_uri=f"sqlite:///{BD_ROBO}")
        sucesso = True

    except Exception as e:
        print(f"Erro ao inicializar o robo: {str(e)}")
    return sucesso, robo


def responder_usuario_por_tag(entrada_usuario):
    resultados = buscar_por_tag(entrada_usuario)

    if resultados:
        resposta = f"\n🔎 Resultados para '{entrada_usuario}':\n"
        for item in resultados:
            resposta += f"- {item['nome']}: {item['descricao']}\n"
    else:
        resposta = f"\n❌ Nenhum resultado encontrado para '{entrada_usuario}'."

    return resposta


def modo_fazer_pedido():
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

    registrar_pedido(item, "retirada no local" if entrega in ["retirar", "local"] else "delivery")

    print(f"\n✅ Pedido registrado com sucesso!\n📝 Item: {item}\n📦 Entrega: {entrega}\n")


def executar(robo):
    tags_conhecidas = obter_tags_conhecidas()
   
    while True:
        mensagem = input("👤:  ") #Aguarda o usuario enviar alguma informação
        
        #Verifica se tem pedido
        with open("./pedido/msg_pedido.json", "r", encoding="utf-8") as f:
            pedidos = json.load(f).get("mensagens", [])
            f.close()

        if mensagem in pedidos:
            modo_fazer_pedido()
            continue
        #Caso o usuario deseje encerrar a conversa
        if mensagem in ["finalizar", "desistir", "acabar", "é so isso", "sair", "cancelar"]:
            print("Você escolheu encerrar nossa conversa 😔. Espero vê-lo em breve!")
            break
        #Retirar espaços
        msg_usuario = mensagem.split()
        encontrou_tag = False
        #Percorre frase do usuario em busca de tag
        for palavra in msg_usuario:
            palavra_processada = stemmer.stem(palavra)
            if palavra_processada in tags_conhecidas: #Se a palavra que o usuario digitou estiver nas tags vai entrar
                resposta = responder_usuario_por_tag(palavra)
                print(f"🤖: {resposta}")
                encontrou_tag = True
                break
        
        if encontrou_tag:
            continue         
        resposta = robo.get_response(mensagem.lower()) #Pega a mensagem enviada pelo usuario e busca a resposta refente
        if resposta.confidence >= CONFIANCA_MINIMA: #confidence é um retorno junto ao text para saber o nivel de confiança da resposta dada
            print(f"🤖: {resposta.text}")
            
        else:
            print(f"🤖 Infelizmente ainda não sei responder esta pergunta. Mas fique tranquilo, estou registrando sua duvida e entraremos em contato")
            
            with open("./conversas/mensagem_aprender.json", "r", encoding="utf-8") as msg:
                aprender = json.load(msg)
                aprender["mensagens"].append(mensagem)
                msg.close()
            
            with open("./conversas/mensagem_aprender.json", "w", encoding="utf-8") as msg:
                json.dump(aprender, msg, ensure_ascii=False, indent=4 )

            print(f"A mensagem que não respondi foi: {mensagem}")
            print("A mensagem foi registrada com sucesso, em breve já teremos uma resposta")
            #Registrar a pergunta em um log
       

if __name__ == "__main__":
    sucesso, robo = inicializar()
    if sucesso:
        executar(robo)
