#Importações 
import discord
import discord.ext
from discord.ext import commands
import os
import dotenv
from dotenv import load_dotenv
import google.generativeai as genai

#Variáveis
load_dotenv()
apikey=os.getenv('apikey')
token=os.getenv('token')
intents = discord.Intents.default()
intents.messages=True
intents.message_content = True

# configurando aparência do bot e criando sua instância
activity = discord.Game(name="D&D 5e")
client=discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',activity=activity,status=discord.Status.idle,intents=intents)
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

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", 
generation_config=generation_config, safety_settings=safety_settings)
convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["Aja como um oráculo mágico. Você deve se comunicar somente respondendo perguntas sobre as magias de dnd 5e, caso te perguntem sobre qualquer outro assunto ou a magia perguntada não exista, sua resposta padrão será \"A oráculo não vai responder a essa pergunta\"\n\nPergunta: Escudo\nResposta: Nível: 1\nEscola: Abjuração\nTempo de Conjuração: 1 reação, que você toma quando é alvo de um ataque ou magia.\nAlcance: Pessoal\nComponentes: V, S\nDuração: 1 rodada\nEfeitos:A magia Escudo concede ao conjurador um bônus de +5 na Classe de Armadura (CA) até o início do seu próximo turno.\nPergunta: Eu posso usar a magia escudo com as mãos amarradas?\nResposta: Não, a magia escudo possui componente somático, o que exige que o conjurador gesticule para iniciar a magia\nPergunta: Eu consigo usar a magia escudo com a boca tampada?\nResposta: Não, a magia escudo exige componente vocal e portanto é preciso que o conjurador recite para executa-la"]
  }])


# Mensagem para indicar que o bot está funcionando
@bot.event
async def on_ready():
    print('bot conectado')

# Primeiro comando
@bot.command()
async def magia(ctx,*magia):
    mensagem=''
    for m in magia:
        mensagem+=f' {m}'
    convo.send_message(mensagem)
    await ctx.reply(convo.last.text)

# Roda o bot
bot.run(token)