
import sys
from discord.ext import commands
import interactions

#On ajoute le dossier Cogs ainsi que ses sources au path pour pouvoir importer les fichiers d'extensions
sys.path.append('Cogs')
sys.path.append('Cogs/src')
client = interactions.Client(
    token="token",
    default_scope="guild"
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
    await ctx.send("Je degage!")
    exit()


client.start()