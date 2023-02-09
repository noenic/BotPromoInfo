
import sys
from discord.ext import commands
import interactions
#On load les informations du bot depuis le fichier config.ini
import configparser,ast
config = configparser.ConfigParser()
config.read('config.ini')
token = config['TOKEN']['token']
guilds=ast.literal_eval(config['GUILDS']['guilds'])


#On ajoute le dossier Cogs ainsi que ses sources au path pour pouvoir importer les fichiers d'extensions
sys.path.append('Cogs')
sys.path.append('Cogs/src')




client = interactions.Client(
    token=token,
    default_scope=guilds,
)   

#On charge les extensions
client.load("Salles")



@client.event
async def on_ready():
    #Fonction qui s'execute quand le bot est prêt
    print("[Main] Bot prêt")
    pass


@client.command()
async def kill(ctx: interactions.CommandContext):
    """Kill le bot"""
    #Si c'est moi qui lance la commande, il le fait sinon il répond par un gif plus ou moins approprié
    if ctx.author.id=="356383729125556228":
        await ctx.send("Je degage!")
        exit()
    else:
        await ctx.send("https://tenor.com/view/chut-ferme-la-tg-puceau-puceau-de-merde-gif-20903914",ephemeral=True)


client.start()