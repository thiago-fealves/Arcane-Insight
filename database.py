import os
import json
import google.generativeai as genai

apikey = os.getenv('apikey')
genai.configure(api_key=apikey)
DATABASE = 'spells.json'

# Carregar o banco de dados
with open(DATABASE, 'r', encoding='utf8') as file:
    data = json.load(file)

# Processar cada magia e adicionar o embed
for spell in data["spells"]:
    text = genai.embed_content(
        model='models/embedding-001',
        content=spell["Description"],
        task_type="RETRIEVAL_DOCUMENT",
        title=spell["Description"]
    )
    spell['embed'] = text["embedding"]

# Salvar o banco de dados atualizado
with open(DATABASE, "w", encoding='utf8') as jsonFile:
    json.dump(data, jsonFile, indent=4)
    print('-----')
