"""This program initializes a discord bot that answers users questions based on a database of the oficial D&D5e spells"""
# Library Imports
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import nextcord
from nextcord.ext import commands
import pandas as pd
import numpy as np

# Getting secrets on .env
load_dotenv()
apikey = os.getenv('apikey')
token = os.getenv('token')

# Configuring discord bot permissions
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True

# Connecting the bot to the database with the spells
DB = 'dnd5e.spells.json'
data = json.loads(open(DB,encoding='utf8').read())
df = pd.json_normalize(data=data["magias"],meta=['titulo','description','embed'])

# Configuring bot appearance on the server and creating it's instance
activity = nextcord.Game(name="D&D 5e")
client = nextcord.Client(intents=intents)
status = nextcord.Status.idle
bot = commands.Bot(command_prefix='.', activity = activity, status = status, intents = intents)
bot.remove_command('help')

def gerar_e_buscar_consulta(request):
    """Function that searches for the closest spell match to the users request on the database"""
    request_embed = genai.embed_content(model='models/embedding-001', content = request, task_type = "RETRIEVAL_QUERY")["embedding"]
    scalar_products=np.dot(np.stack(df["embed"]), request_embed)
    index = np.argsort(scalar_products)[::-1][:5]
    descriptions=''
    for i in index:
        descriptions += f'\n\n{df.iloc[i]["title"]}\n{df.iloc[i]["description"]}'
    return descriptions

# Configuring the chat settings for the chatbot
genai.configure(api_key=apikey)
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0
}

# Diminishing the restrictions of the api, because in previous tests with higher restriction, bot was acussing several false positives.
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]
# Initializing the model
model = genai.GenerativeModel(model_name="gemini-1.0-pro",
generation_config = generation_config, safety_settings=safety_settings)
default_prompt = ["Aja como um oráculo mágico.Você receberá uma lista com varias magias e suas descrições,limpe as tags html delas e escolha a que tiver mais a ver com a pergunta.Responda sempre em menos de 2000 caracteres, não se prenda somente a respostas formatadas como a dos exemplos a seguir, interprete a magia de acordo com a pergunta, inclua todos os detalhes da magia, incluindo a descrição completa dela em sua resposta,os componentes estão abreviados em S para somático(Uso de gestos), V para verbal(uso de recitação) e M para material(uso de items), uma magia que tenha componente somático exige movimento livre das mãos para ser realizada, e uma magia que tenha componente verbal necessita que a boca do usuário não esteja tampada para ser realizada, independentemente da descrição da magia.\nExemplos:\nPergunta: Eu posso usar a magia escudo arcano com as mãos amarradas?\nResposta: Não, a magia escudo arcano possui componente somático, o que exige que o conjurador gesticule para iniciar a magia\nPergunta: Eu consigo usar a magia escudo com a boca tampada?\nResposta: Não, a magia escudo exige componente vocal e portanto é preciso que o conjurador recite para executa-la\nPergunta: Eu consigo usar a magia ataque certeiro com as mãos amarradas?\nResposta: Sim, a magia ataque certeiro não exige componente somático, portanto, isso não vai te impedir de executar a magia"]

@bot.event
async def on_ready():
    """Visual confirmation to knwo when the bot is online"""
    print('bot conectado')


@bot.command(aliases=['Help','h'])
async def help(ctx): 
    """Bot help command"""
    text="# Lista de comandos\n!g {prompt} ou !grimorio {prompt}:\nFaça uma pergunta à oráculo, ela pode responder qualquer coisa relacionada à qualquer magia de DnD5e\n**Observação**:O Arcane Insight pode errar as vezes, se a resposta parecer estranha confira em uma fonte oficial \n Help ou help ou h:\nMostra essa mensagem\n### Obrigado por usar o Arcane Insights!"
    await ctx.reply(text)


@bot.command(aliases=['g','G','grimorio','Grimorio'])
async def grimoire(ctx, *request: str):
    """Searches for the closest available spell related to the users request and returns a gemini-powered response."""
    request =' '.join(request)
    spell = gerar_e_buscar_consulta(input)
    response = model.generate_content(f'{default_prompt}\n\n{spell}\n\nPergunta:{input}')
    await ctx.reply(response.text)

# Start the bot
bot.run(token)
