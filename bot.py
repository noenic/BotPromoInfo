import discord
import os
import menu

#Création du client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    #Sécurité
    if message.author == client.user:
        return

    if message.content == "!menu":
        dico = menu.majMenu()
        print(dico)
        #Vérification de si le menu est vide ou pas 
        if dico == {}:
            messageText = "❌ Menu pas encore disponible ❌"
        else:
            menuJours = menu.menuDuJours(dico)
            messageText = ""
            messageText += "🍽 ___***" + menuJours[0] + "***___ 🍽" + "\n"
            
            for i in range(len(menuJours[1])):
                messageText += '• ' + menuJours[1][i] + "\n"
        await message.channel.send(messageText)
        

    if message.content == '!menuAll':
        dico = menu.majMenu()
        messageText = ""
        #Vérification de si le menu est vide ou pas 
        if dico == {}:
            messageText = "❌ Menu pas encore disponible ❌"
        else:
            for jours in dico:
                messageText += "🍽 ___***" + jours + "***___ 🍽" + "\n"
                for y in range(len(dico[jours])):
                    messageText += '• ' + dico[jours][y] + "\n"
                messageText += '\n'
        await message.channel.send(messageText)

    if message.content == '!help':
        messageText = ""
        #Vérification de si le menu est vide ou pas 
        messageText = "🚧 ___***Liste des commandes***___ 🚧\n!menu : Voir le menu du jours\n!menuAll : Voir tous les menus disponibles"
        await message.channel.send(messageText)

#Démarrage du client
client.run(os.environ["TOKEN"])
