import interactions,sys
import datetime as datetime
from src.TrouveTaSalle import TrouveTaSalle

def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp-3600).strftime("%H:%M")


class Salles(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.edt=TrouveTaSalle(["1","988","240","239"])

    @interactions.extension_command(
    name="salles_libres", 
    description="Retourne les salles libres actuellement, triées par durée de disponibilité",
    )
    async def salle_libre(self, ctx: interactions.CommandContext):
        info=self.edt.get_salle_libre()
        msg='''```Salles libres actuellement, triées par durée de disponibilité:\n'''

        for salle in info:
            if salle in self.edt.listeSallesPC:
                strsalle="🖥️ "+salle
                if len(salle)==2:
                    strsalle+=" "
            else:
                strsalle="📚 "+salle
            # msg+=strsalle+" : ["+datetime.datetime.fromtimestamp(info[salle][0][0],tzinfo=datetime.timezone.utc).strftime("%H:%M")+" - "+datetime.datetime.fromtimestamp(info[salle][0][1],tzinfo=datetime.timezone.utc).strftime("%H:%M")+"]\n"
            #L'heure est en UTC+1, on la convertit en UTC
            msg+=strsalle+" : "+datetime.datetime.fromtimestamp(info[salle][0][0]-3600).strftime("%H:%M")+" - "+datetime.datetime.fromtimestamp(info[salle][0][1]-3600).strftime("%H:%M")+"\n"


        msg+="```"
        await ctx.send(msg)

    @interactions.extension_command(
        name="info_salle",
        description="Retourne les informations sur une salle",
        options = [
        interactions.Option(
            name="salle",
            description="De quel salle veux-tu les informations ?",
            type=interactions.OptionType.INTEGER,
            required=True,
            max_value=130,
            min_value=15,
        ),
    ],
        
    )
    async def info_salle(self, ctx: interactions.CommandContext, salle: int):
        #On retourne ce que l'utilisateur a écrit
        info=self.edt.get_info_salle(str(salle))
        if "error" in info:
            if info["error"]=="NOT FOUND":
                await ctx.send("```🤯 Je ne connais pas cette salle : "+str(salle)+" 🤯```")
                return
            if info["error"]=="NO DATA":
                await ctx.send("```❌ Je n'ai pas de données pour la salle : "+str(salle)+"\nElle n'est pas inscrite dans l'emploi du temp. ❌\nElle est probablement libre 🤔```")
                return
        msg='''```Informations sur la salle {}:\n'''.format(salle)
        if info["now"]:
            msg+="🔴 "+info["now"]["name"]+" de "+format_time(info["now"]["begin"])+" à  "+format_time(info["now"]["end"])+"\n"
        else:
            msg+="🟢 Libre\n"

        msg+='''```'''
        await ctx.send(msg)

        
        
        
        



def setup(client):
    Salles(client)
    print("[Salles] chargé")
