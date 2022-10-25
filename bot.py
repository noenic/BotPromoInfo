import discord
from dotenv import load_dotenv
import os

#Indiquer où est le fichier de config
load_dotenv(dotenv_path="config")

#Création du client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#Evenements
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    #Sécurité
    if message.author == client.user:
        return

    if message.content == "!menu":

        await message.channel.send(f"Ya plus rien le gros lard de Matis Chabanat à tout gobé !")

#Démarrage du client
client.run(os.getenv("TOKEN"))
