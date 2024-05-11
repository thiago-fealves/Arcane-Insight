#Importações 
import os
import dotenv
from dotenv import load_dotenv
import google.generativeai as genai
import nextcord # type: ignore
from nextcord.ext import commands # type: ignore
import json
import pandas as pd
import numpy as np
from unidecode import unidecode

#Variaveis
load_dotenv()
apikey=os.getenv('apikey')
genai.configure(api_key=apikey)
token=os.getenv('token')
intents = nextcord.Intents.default()
intents.messages=True
intents.message_content = True
database='dnd5e.spells.json'
data=json.loads(open(database,encoding='utf8').read())
df = pd.json_normalize(data=data["magias"],meta=['titulo','description','embed'])

# configurando aparência do bot e criando sua instância
activity = nextcord.Game(name="D&D 5e")
client=nextcord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',activity=activity,status=nextcord.Status.idle,intents=intents)
bot.remove_command('help')

def gerar_e_buscar_consulta(consulta):    
    embed_da_consulta=genai.embed_content(model='models/embedding-001',content=consulta, task_type="RETRIEVAL_QUERY")["embedding"]
    produtos_escalares=np.dot(np.stack(df["embed"]),embed_da_consulta)
    indice=np.argsort(produtos_escalares)[::-1][:5]
    descricoes=''
    for i in indice:
        descricoes += f'\n\n{df.iloc[i]["title"]}\n{df.iloc[i]["description"]}'
    return descricoes

#configurando o gemini
genai.configure(api_key=apikey)
# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]
model = genai.GenerativeModel(model_name="gemini-1.0-pro", 
generation_config=generation_config, safety_settings=safety_settings)
prompt_inicial =["Aja como um oráculo mágico.Você receberá uma lista com 5 magias e suas descrições, escolha a que tiver mais a ver com a pergunta.Responda sempre em menos de 2000 caracteres, não se prenda somente a respostas formatadas como a dos exemplos a seguir, interprete a magia de acordo com a pergunta, inclua todos os detalhes da magia, incluindo a descrição completa dela em sua resposta,os componentes estão abreviados em S para somático(Uso de gestos), V para verbal(uso de recitação) e M para material(uso de items), uma magia que tenha componente somático exige movimento livre das mãos para ser realizada, e uma magia que tenha componente verbal necessita que a boca do usuário não esteja tampada para ser realizada, independentemente da descrição da magia.\nExemplos:\nPergunta: Eu posso usar a magia escudo arcano com as mãos amarradas?\nResposta: Não, a magia escudo arcano possui componente somático, o que exige que o conjurador gesticule para iniciar a magia\nPergunta: Eu consigo usar a magia escudo com a boca tampada?\nResposta: Não, a magia escudo exige componente vocal e portanto é preciso que o conjurador recite para executa-la\nPergunta: Eu consigo usar a magia ataque certeiro com as mãos amarradas?\nResposta: Sim, a magia ataque certeiro não exige componente somático, portanto, isso não vai te impedir de executar a magia"]

# Mensagem para indicar que o bot está funcionando
@bot.event
async def on_ready():
    print('bot conectado')
@bot.command(aliases=['Help','h'])

#comando de ajuda
async def help(ctx):
    text="# Lista de comandos\n## Magia ou m ou magia {prompt}:\nFaça uma pergunta à oráculo, ela pode responder qualquer coisa relacionada à qualquer magia de DnD5e\n**Observação**:O Gemini pode não identificar o nome da magia em português as vezes devido a conflitos de tradução, se isso ocorrer tente com o nome em inglês\n## Help ou help ou h:\nMostra essa mensagem\n### Obrigado por usar o Arcane Insights!"
    await ctx.reply(text)

#comando principal
@bot.command(aliases=['g'])
async def grimorio(ctx, *entrada:str):
    entrada=' '.join(entrada)
    entrada=unidecode(entrada)
    magia=gerar_e_buscar_consulta(entrada)
    response=model.generate_content(f'{prompt_inicial}\n\n{magia}\n\nPergunta:{entrada}')
    await ctx.reply(response.text)
# Roda o bot
bot.run(token)