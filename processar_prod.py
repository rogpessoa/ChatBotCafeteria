from nltk import word_tokenize, corpus
import json
from nltk.stem import RSLPStemmer


# Carrega a base de conhecimento
with open("./base_conhecimento/base.json", "r", encoding="utf-8") as f:
    dados = json.load(f)
    f.close()


# Inicializa o stemmer e stopwords
stemmer = RSLPStemmer()
stopwords_pt = set(corpus.stopwords.words("portuguese"))

# Pré-processa as tags e cria um índice
indice_tags = {}

for item in dados["base_conhecimento"]:
    for tag in item["tags"]:
        tag_processada = stemmer.stem(tag.lower())
        if tag_processada not in indice_tags:
            indice_tags[tag_processada] = []
        indice_tags[tag_processada].append(item)

def buscar_por_tag(termo_usuario):
    termo_processado = stemmer.stem(termo_usuario.lower())
    resultados = indice_tags.get(termo_processado, [])

    return resultados

def obter_tags_conhecidas():
    return list(indice_tags.keys())



