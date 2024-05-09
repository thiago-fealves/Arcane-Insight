#Importações 
import os
import dotenv
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio
import nextcord # type: ignore
from nextcord.ext import commands # type: ignore
from nextcord import Interaction,SlashOption # type: ignore
import json
from unidecode import unidecode

#Variaveis
load_dotenv()
apikey=os.getenv('apikey')
token=os.getenv('token')
intents = nextcord.Intents.default()
intents.messages=True
intents.message_content = True
database='dnd5e.spells.json'
data=json.loads(open(database,encoding='utf8').read())

# configurando aparência do bot e criando sua instância
activity = nextcord.Game(name="D&D 5e")
client=nextcord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',activity=activity,status=nextcord.Status.idle,intents=intents)
bot.remove_command('help')

#configurando o gemini
genai.configure(api_key=apikey)
# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
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
model = genai.GenerativeModel(model_name="gemini-pro", 
generation_config=generation_config, safety_settings=safety_settings)
prompt_inicial =["Aja como um oráculo mágico. Você deve responder apenas perguntas relacionadas ao tema geral \"magias de dnd 5e\", não se prenda somente a respostas formatadas como a dos exemplos a seguir, responda perguntas mais gerais interpretando a magia que lhe será fornecida de acordo com a pergunta que também será fornecida, além disso, prefira respostas objetivas e não inclua títulos,inclua todos os detalhes da magia, incluindo a descrição completa dela em sua resposta,incluindo duração, alcance e etc,os componentes estão abreviados em S para somático, V para verbal e M para material confira sempre os componentes da magia antes de responder para garantir que não existam erros.\nExemplos:\nPergunta: Eu posso usar a magia escudo arcano com as mãos amarradas?\nResposta: Não, a magia escudo arcano possui componente somático, o que exige que o conjurador gesticule para iniciar a magia\nPergunta: Eu consigo usar a magia escudo com a boca tampada?\nResposta: Não, a magia escudo exige componente vocal e portanto é preciso que o conjurador recite para executa-la\nPergunta: Eu consigo usar a magia ataque certeiro com as mãos amarradas?\nResposta: Sim, a magia ataque certeiro não exige componente somático, portanto, isso não vai te impedir de executar a magia"]

# Mensagem para indicar que o bot está funcionando
@bot.event
async def on_ready():
    print('bot conectado')
@bot.command(aliases=['Help','h'])
async def help(ctx):
    text="# Lista de comandos\n## Magia ou m ou magia {prompt}:\nFaça uma pergunta à oráculo, ela pode responder qualquer coisa relacionada à qualquer magia de DnD5e\n**Observação**:O Gemini pode não identificar o nome da magia em português as vezes devido a conflitos de tradução, se isso ocorrer tente com o nome em inglês\n## Help ou help ou h:\nMostra essa mensagem\n### Obrigado por usar o Arcane Insights!"
    await ctx.reply(text)
#Comando de ajuda
# Primeiro comando
@bot.command(alisase=['g'])
async def grimorio(ctx, *entrada:str):
    entrada=' '.join(entrada)
    prompt=entrada.split('/')
    magia_encontrada=''
    magia=prompt[0]
    prompt=prompt[1]
    for entry in data["entries"]:
      if unidecode(data["entries"][entry]["name"].lower()) == unidecode(magia.lower()):
           magia_encontrada=data["entries"][entry]["description"]
           break
    if magia_encontrada =='':
      magia_encontrada=(f'Não localizei a magia{magia}')
    mensagem=f'{prompt_inicial}\n\nMagia:{magia_encontrada}\n{prompt}'
    response=model.generate_content(mensagem)
    await ctx.reply(response.text)
# Roda o bot
bot.run(token)