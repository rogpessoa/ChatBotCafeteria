from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import json


NOME_ROBO = "Cafeteria Wesley Cafezão"
BD_ROBO = "chat.sqlite3"
CONVERSAS = [
    "./conversas/cardapio.json",
    "./conversas/horario_pagamento.json",
    "./conversas/saudacoes.json"
    
]


def criar_treinador():
    robo = ChatBot(NOME_ROBO, storage_adapter = "chatterbot.storage.SQLStorageAdapter", database_uri=f"sqlite:///{BD_ROBO}")
    robo.storage.drop()
    return ListTrainer(robo) #Treina o robo e devolve

def carregar_conversas():
    conversas = []
    for arquivo_conversas in CONVERSAS: #Percorre as conversas
        with open(arquivo_conversas, "r", encoding="utf-8") as arquivo:
            lista_conversas = json.load(arquivo)
            conversas.append(lista_conversas["conversas"]) #salva as conversas

            arquivo.close()
    return conversas

def treinar(treinador, conversas):
    for conversa in conversas:
        for mensagens_geral in conversa:
            mensagens = mensagens_geral["mensagem_usuario"]
            resposta_bot = mensagens_geral["resposta_bot"]

            for mensagem in mensagens:
                print(f"Treinando mensagens do bot Cafeteria: {mensagem}, resposta: {resposta_bot}")
                treinador.train([mensagem, resposta_bot])


if __name__ == "__main__":
    treinador = criar_treinador()
    conversas = carregar_conversas()
    if treinador and conversas:
        treinar(treinador, conversas)