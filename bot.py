import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

client.run('MTAzNDQzNzIxOTkxMTQ2NzAzOQ.GMCQIZ.PztRDk_d8QhYeWd9_4pnpHiu4cgum1TtJ1n3cQ')
