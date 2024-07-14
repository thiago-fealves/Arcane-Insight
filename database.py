import os
import dotenv
from dotenv import load_dotenv
import google.generativeai as genai
import json
import numpy as np

load_dotenv()
apikey=os.getenv('apikey')
genai.configure(api_key=apikey)
database='dnd5e.spells.json'
data=json.loads(open(database,'r',encoding='utf8').read())
for i in data:
    text= genai.embed_content(model='models/embedding-001',content=data[i]['description'],task_type="RETRIEVAL_DOCUMENT",title=i)
    data[i]['embed']=text["embedding"]
    with open("dnd5e.spells.json", "w") as jsonFile:
        json.dump(data, jsonFile)
        print('-----')