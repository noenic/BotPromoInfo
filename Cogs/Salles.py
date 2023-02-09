import interactions,sys
import datetime as datetime
import threading 
import time
import traceback
from src.TrouveTaSalle import TrouveTaSalle
#------------CONSTANTES------------#
ID_PROMOS={
    "1-TD1-TP1": "368",
    "1-TD1-TP2": "369",
    "1-TD2-TP3": "371",
    "1-TD2-TP4": "372",
    "1-TD3-TP5": "373",
    "2-TD1-TP1": "394",
    "2-TD1-TP2": "395",
    "2-TD2-TP3": "397",
    "2-TD2-TP4": "398"
}

#ID des rôles pour chaque TD,TP et Année
ROLES={"TD":{"959814970336510022":"TD1",
            "959815001642790942":"TD2",
            "959815034530324590":"TD3",},
       "TP":{"959815069665996800":"TP1",
             "959815092390752256":"TP2",
             "959815110157828147":"TP3",
             "959815124938534962":"TP4",
             "959815142038700052":"TP5",},
       "Année":{"959809924798496799":"1",
                "959809978875650108":"2",},
    
}





def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp-3600).strftime("%H:%M")


#Fonction threadée pour mettre à jour l'emploi du temps toutes les 5 minutes
def refresh_edt(Salle):
    #On lance une boucle infinie dans un thread
    while True:
        try:
            #On attend 5 minutes
            out=Salle.edt.refresh()
            if out=="hour" or out=="weekend":
                #Si on est en dehors des heures de cours, on attend d'être le lendemain
                delai=(24-datetime.datetime.now().hour)*3660
                print("[Salles] On est en dehors des heures de cours, on attend d'être le lendemain\n[Salles] On essaye dans ",delai," secondes")
                Salle.change_state(False)
            else:
                Salle.change_state(True)
                delai=600
        except Exception as e:
            print("[Salles] Erreur lors de la mise à jour de l'emploi du temps: ",e)
            print("[Salles] On reessaye dans 30 secondes")
            print(traceback.format_exc())
            delai=30
        time.sleep(delai)

    
class Salles(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client
        self.edt=TrouveTaSalle(ID_PROMOS,refresh_on_init=False)

    def change_state(self,state):
        self.edt.active=state
    
    async def check_state(self, ctx: interactions.CommandContext):
        if not self.edt.active:
            Embed=interactions.Embed(
                title=":x: ERREUR :x:",
                description="",
                color=0xff0000,
            )
            Embed.add_field(name="On est en dehors des heures de cours\nRessayez demain", value=":zzz:", inline=False)
            await ctx.send(embeds=Embed, ephemeral=True)
            return False
        if self.edt.lock:
            Embed=interactions.Embed(
                title=":x: ERREUR :x:",
                description="",
                color=0xff0000,
            )
            Embed.add_field(name="L'emploi du temps n'est pas encore chargé", value=":hourglass_flowing_sand: attends dans quelques secondes", inline=False)
            msg=await ctx.send(embeds=Embed, ephemeral=True)
            return False

        return True


    @interactions.extension_command(
    name="salles_libres", 
    description="Retourne les salles libres actuellement, triées par durée de disponibilité",
    )
    async def salle_libre(self, ctx: interactions.CommandContext):
        if not await self.check_state(ctx):
            return
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
            msg+=strsalle+" : "+format_time(info[salle][0][0])+" - "+format_time(info[salle][0][1])+"\n"


        msg+="```"
        await ctx.send(msg)

    @interactions.extension_command(
        name="info_salle",
        description="Retourne les informations sur une salle",
        options = [
        interactions.Option(
            name="salle",
            description="De quelle salle veux-tu les informations ?",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
        
    )
    async def info_salle(self, ctx: interactions.CommandContext, salle: str):
        if not await self.check_state(ctx):
            return
        info=self.edt.get_info_salle(salle)
        Embed=interactions.Embed(
            title="Informations sur la salle "+str(salle),
            description="",
            color=0xff8c3f,
            footer={"text":"Dernière mise à jour: "+format_time(info["checked"])+"\nLes informations peuvent être incomplètes ou inexactes"},
            )
        
        if "error" in info and info["error"]=="NOT FOUND":
            Embed.title=":x: ERREUR :x:"
            Embed.description="la salle "+str(salle)+" n'existe pas"
            Embed.color=0xff0000
            await ctx.send(embeds=Embed, ephemeral=True)
            return
        else:
            if "now" in info and info["now"]:
                Embed.set_thumbnail(url='https://media.tenor.com/LhSUbS1MsTgAAAAC/smile-no.gif')
                Embed.add_field(name="🔴 En cours", value=info["now"]["name"]+" de **"+format_time(info["now"]["begin"])+"** à  **"+format_time(info["now"]["end"])+"**", inline=False)
            else:
                Embed.set_thumbnail(url="https://media.tenor.com/QEk9IT7TRWcAAAAd/snacks-close.gif")
                Embed.add_field(name="🟢 Libre", value="", inline=False)
            
            if "error" not in info:
                if len(info["cours"])>0:
                    prochain=""
                    #On prend pas le premier cours, car c'est le cours actuel
                    for i in range(0,len(info["cours"])):
                        prochain+=info["cours"][i]["name"]+" de **"+format_time(info["cours"][i]["begin"])+"** à  **"+format_time(info["cours"][i]["end"])+"**\n"
                    Embed.add_field(name=":alarm_clock: Prochain cours", value=prochain, inline=False)
                

                if info["free"]:
                    free=""
                    for i in range(0,len(info["free"])):
                        free+="**"+format_time(info["free"][i][0])+"** à **"+format_time(info["free"][i][1])+"**\n"
                    Embed.add_field(name=":white_check_mark: Disponibilités", value=free, inline=False)
                

            
            await ctx.send(embeds=Embed)
    
    @interactions.extension_command(
        name="info_prof",
        description="Retourne les informations sur un professeur",
        options = [
        interactions.Option(
            name="prof",
            description="De quel professeur veux-tu les informations ?",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[
                #On est limité à 25 choix, donc on en met que 25 (On met que les plus importants)
                interactions.Choice(name="P. Lopistéguy", value="LOPISTÉGUY"),
                interactions.Choice(name="Y. Carpentier", value="CARPENTIER"),
                interactions.Choice(name="P. Etcheverry", value="ETCHEVERRY"),
                interactions.Choice(name="C. Marquesuzaà", value="MARQUESUZAÀ"),
                interactions.Choice(name="M. Bruyère", value="BRUYÈRE"),
                interactions.Choice(name="A. Moulin", value="MOULIN"),
                interactions.Choice(name="M. Borthwick", value="BORTHWICK"),
                interactions.Choice(name="D. Urruty", value="URRUTY"),
                interactions.Choice(name="M. Erritali", value="ERRITALI"),
                interactions.Choice(name="S. Sassi", value="SASSI"),
                interactions.Choice(name="R. Chbeir", value="CHBEIR"),
                interactions.Choice(name="T. Nodenot", value="NODENOT"),
                interactions.Choice(name="E. Chicha", value="CHICHA"),
                interactions.Choice(name="A. Boggia", value="BOGGIA"),
                interactions.Choice(name="M. Capliez", value="CAPLIEZ"),
                #interactions.Choice(name="O. DEZEQUE", value="DEZEQUE"),
                interactions.Choice(name="C. Rustici", value="RUSTICI"),
                interactions.Choice(name="P. Roose", value="ROOSE"),
                interactions.Choice(name="S. Voisin (Laplace) ", value="VOISIN"),
                interactions.Choice(name="N. Valles-Parlangeau", value="Valles-Parlangeau"),
                interactions.Choice(name="P. Dagorret", value="DAGORRET"),
                interactions.Choice(name="MA. Boudia", value="BOUDIA"),
                interactions.Choice(name="M. Walton", value="WALTON"),
                interactions.Choice(name="JM. Fiton", value="FITON"),
                interactions.Choice(name="Y. Dourisbourne", value="DOURISBOURE"),
                #interactions.Choice(name="M. Deguilhem", value="DEGUILHEM"),
                interactions.Choice(name="MA. Gastambide", value="GASTAMBIDE"),

            ]
        ),
    ],
    )
    async def info_prof(self, ctx: interactions.CommandContext, prof: str):
            if not await self.check_state(ctx):
                return
            info= self.edt.get_prof(prof)
            Embed=interactions.Embed(
                title="Informations sur "+str(prof),
                description="",
                color=0xff8c3f,
                footer={"text":"Dernière mise à jour: "+format_time(info["checked"])+"\nLes informations peuvent être incomplètes ou inexactes"},
            )
            if info['now']!=None:
                #Embed.set_thumbnail(url="https://media.tenor.com/0YJ3qQ2Qb9UAAAAC/working.gif")
                Embed.add_field(name="🔴 En cours", value=info["now"]["name"]+" de **"+format_time(info["now"]["begin"])+"** à  **"+format_time(info["now"]["end"])+"** en salle **"+info["now"]["salle"]+"**", inline=False)
            else:
                #Embed.set_thumbnail(url="https://media.tenor.com/LhSUbS1MsTgAAAAC/smile-no.gif")
                if prof=="CHBEIR":
                    Embed.add_field(name="🟡 Pas en cours", value="Actuellement en train d'apprendre le PL/SQL à une table basse", inline=False)
                else:
                    Embed.add_field(name="🟡 Pas en cours", value="", inline=False)

            if info['cours']!=[]:
                prochain=""
                #On prend pas le premier cours, car c'est le cours actuel
                for i in range(0,len(info["cours"])):
                    prochain+=info["cours"][i]["name"]+" de **"+format_time(info["cours"][i]["begin"])+"** à  **"+format_time(info["cours"][i]["end"])+"** en salle **"+info["cours"][i]["salle"]+"**\n"
                Embed.add_field(name=":alarm_clock: Prochain cours", value=prochain, inline=False)
            await ctx.send(embeds=Embed)


    @interactions.extension_command(
        name="emploi_du_temps",
        aliases=["edt"],
        description="Retourne ton emploi du temps par rapport à tes rôles",
    )
    async def emploi_du_temps(self, ctx: interactions.CommandContext):
        if not await self.check_state(ctx):
            return
        annee,td,tp="","",""

        for role in ctx.author.roles:
            if str(role) in ROLES["Année"]:
                annee=ROLES["Année"][str(role)]
            if str(role) in ROLES['TD']:
                td=ROLES["TD"][str(role)]
            if str(role) in ROLES['TP']:
                tp=ROLES["TP"][str(role)]
        info=self.edt.get_cours_TD(annee+"-"+td+"-"+tp)
        Embed=interactions.Embed(
                title="Informations sur l'emploi du temps du TD :\n"+td+"-"+tp+" du BUT"+annee+"",
                description="",
                color=0xff8c3f,
                footer={"text":"Dernière mise à jour: "+format_time(info["checked"])+"\nLes informations peuvent être incomplètes ou inexactes"},
        )
        if annee=="" or td=="" or tp=="":
            Embed.title=":x: ERREUR :x:"
            Embed.add_field(name="Tu n'as pas de rôle d'année, de TD ou de TP\nVérifie tes rôles ici : <#959813680101478470>", value="", inline=False)
            Embed.color=0xff0000
            await ctx.send(embeds=Embed, ephemeral=True)
            return
            #await ctx.send("Tu n'as pas de rôle d'année, de TD ou de TP\nVérifie tes rôles ici : <#959813680101478470>")
        else:
            for i in range(0,len(info["cours"])):
                Embed.add_field(name=format_time(info["cours"][i]["begin"])+" - "+format_time(info["cours"][i]["end"]), value=info["cours"][i]["name"]+" en salle "+info["cours"][i]["salle"]+" avec[none]", inline=False)
            await ctx.send(embeds=Embed)


        
        



def setup(client):
    #On fait un thread pour charger l'emploi du temps en arrière plan toutes les 10 minutes
    thread=threading.Thread(target=refresh_edt, args=(Salles(client),))
    thread.setDaemon(True)
    print("[Salles] chargé")
    thread.start()
