from ics  import *
import time
import requests
import datetime
import concurrent 
import concurrent.futures

import pytz
timezone = pytz.timezone("Europe/Paris")




class TrouveTaSalle():
    def __init__(self,listeID:dict,refresh_on_init:bool=True):
        if type(listeID) != dict:
            raise TypeError("listeID doit etre un dictionnaire")
        if len(listeID) == 0:
            raise ValueError("listeID doit contenir au moins un element")
        self.listeID=listeID
        self.listeSallesPC=["15","17","21","22","23","24","25","25","26","130","128"]
        self.listeSallesTD=["124","125","126","127","129","138"]
        self.refresh_on_init=refresh_on_init
        self.lock=False #lock pour les requetes
        self.salles={}
        for salle in self.listeSallesPC+self.listeSallesTD:
            self.salles[salle]=[]
        if refresh_on_init:
            self.active=self.refresh()
        else:
            self.active=True

    '''
    Recupere le fichier ics de l'emplois du temps de L'ID dans l'url
    '''
    def get_TD_ics(self,id:str,TD:str)-> str:
        url="https://www.iutbayonne.univ-pau.fr/outils/edt/default/export?ID="+id
        return (requests.get(url).text, id, TD)
        
    
    '''
    Recupere les salles, les cours et les profs de l'emplois du temps
    On le fait en parallèle pour gagner du temps (On fait les requetes en thread)
    '''
    def refresh(self):
  
        self.date = datetime.datetime.now()
        # self.date=self.date+datetime.timedelta(days=1)
        # self.date=self.date.replace(hour=14,minute=0,second=0,microsecond=0)
        #Si il est avant 7h et apres 18h30, ou qu'on est le week end, on renvoie pas de donnees
        if self.date.weekday() >= 5:
            return "weekend"
        if (self.date.hour> 19 or (self.date.hour> 19 and  self.date.minute > 30)) :
            return "hour"
        #On clear les salles pour les remplir avec les nouvelles et en meme temps on supprime les evenements qui sont finis
        tempsalle={}
        for salle in self.salles:
            tempsalle[salle]=[]
        # #On met la date de demain à 8h
        print("[Salles] Refresh des emplois du temps...: ", self.date.astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S"))
        self.lock=True
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #On fait les requetes en parallèle (Parce que c'est long)
            futures = [executor.submit(self.get_TD_ics,self.listeID[TD],TD) for TD in self.listeID]
            for future in concurrent.futures.as_completed(futures):
                TD = future.result()
                res_TD=self.get_TD_salle(TD)
                #print("refresh",res_TD)
                for salle in res_TD:
                    if salle in tempsalle:
                        tempsalle[salle]+=res_TD[salle]
                    else:
                        tempsalle[salle]=res_TD[salle]
        

        #On trie les events de chaque salle par date de debut et on les evenement qui commencent et se terminent au meme moment (doublons)
        for salle in tempsalle:
            tempsalle[salle].sort(key=lambda x: x.begin.timestamp())
        
            i = 0
            #On supprime les doublons
            while i < len(tempsalle[salle])-1:
                #Si l'evenement commence et se termine au meme moment que l'evenement suivant on supprime l'evenement suivant (doublon)
                if tempsalle[salle][i].begin.timestamp() == tempsalle[salle][i+1].begin.timestamp() and tempsalle[salle][i].end.timestamp() == tempsalle[salle][i+1].end.timestamp():
                    #Avant de le supprimé on ajoute cette évenement au deux TP du TD (pour l'emplois du temps)
                    tempsalle[salle][i+1].url[0].append(tempsalle[salle][i].url[0][0])
                    tempsalle[salle][i+1].url[1].append(tempsalle[salle][i].url[1][0])
                    #print(tempsalle[salle][i+1].url,tempsalle[salle][i+1].name)
                    tempsalle[salle].pop(i)

                else:
                    i+=1
        self.salles=tempsalle
        self.lock=False
        return "ok"
        

    def get_TD_salle(self,TD:list)-> dict: 
        # On recupere les evenements du calendrier
        events = list(Calendar(TD[0]).events)
        #On les trie par date et heure de debut
        events.sort(key=lambda x: x.begin.timestamp())
        salles_TD = {}
        for event in events:
            #Je ne sais pas pourquoi mais les evenements sont en UTC donc on ajoute une heure
            # event.end = event.end + datetime.timedelta(hours=1)
            # event.begin = event.begin + datetime.timedelta(hours=1)

            #On ne garde que les évènements du jour et si l'evenement est le jour d'après, on quitte (On fait gaffe au changement de mois et d'année)
            if event.begin.date().day > self.date.day or event.begin.date().month > self.date.month or event.begin.date().year > self.date.year:
                break
            
            #On ne traite que les évènements du jour qui ne sont pas finis
            if event.end.timestamp() > self.date.timestamp():

                if event.location:
                    #On stock le TD dans url même si c'est pas vraiment une url
                    event.url = [[TD[1]],[TD[2]]]
                    nds= event.location
                    #On enleve les S.
                    nds = nds.replace("S.","")
                    #Je sais pas qui a fait merde mais l'option espagnol c'est Salle 138 et pas S.138
                    nds = nds.replace("Salle ","")
                    event.location = nds

              
                    #on split à la virgule si il y en a une
                    nds = nds.split(",")
                    for i in range(len(nds)):
                        #Si le premier caractere est un 0 on le supprime
                        if len(nds[i])>0 and nds[i][0] == "0":
                            nds[i] = nds[i][1:]

                        #On regarde si la salle est deja dans le dictionnaire
                        if nds[i] in salles_TD:
                            #Si oui on ajoute l'evenement a la liste
                            salles_TD[nds[i]].append(event)
                        else:
                            #Si non on cree la salle avec l'evenement
                            salles_TD[nds[i]] = [event]

            
        #print(salles_TD)
        return(salles_TD)
    


    #Si la derniere date de refresh est superieur a 5 minutes on refresh pour avoir les nouvelles données si il y en a
    def need_refresh(self):
        if datetime.datetime.now()-self.date > datetime.timedelta(minutes=10) and self.refresh_on_init:
            print("[Salles] On refresh")
            self.refresh()


    #On verifie que la salle existe et qu'il y a des donnees
    def check_salle(self,salle:str):
        if salle not in self.listeSallesTD+self.listeSallesPC:
            return "NOT FOUND"
        if salle not in self.salles:
            return "NO DATA"
        return True


    def get_prof(self,prof:str):
        self.need_refresh()
        #On met le prof en majuscule car les noms sont en majuscule dans les descriptions
        prof=prof.upper()
        prof_info={"checked":self.date.timestamp()}
        prof_info["name"]=prof
        prof_info["now"]=None
        prof_info["cours"]=[]
        checker = {}
        for salle in self.salles:
            for event in self.salles[salle]:
                if event.description != None and prof in event.description:
                    #Si le cours est deja dans la liste on ne l'ajoute pas
                    #On ajoute le timestamp pour eviter les doublons si deux cours ont le meme nom mais ne sont pas au meme moment
                    if event.name+str(event.begin.timestamp()) in checker:
                        #Le cours est deja dans le checker donc le prochain doit juste avoir l'autre salle
                        checker[event.name+str(event.begin.timestamp())]["salle"]+="-"+salle
                    else:
                        event_info={"name":event.name}
                        event_info["begin"]=event.begin.timestamp()
                        event_info["end"]=event.end.timestamp()
                        # event_info["begin"]=event.begin.time().strftime("%H:%M")
                        # event_info["end"]=event.end.time().strftime("%H:%M")
                        event_info["salle"]=salle
                        checker[event.name+str(event.begin.timestamp())]=event_info


                        # # #On regarde si le prof est en cours au moment actuel et on met la salle dans la variable now 
                        # if event.begin.timestamp() <= self.date.timestamp() and event.end.timestamp() >= self.date.timestamp():
                        #     prof_info["now"]=event_info

        #On peut maintenant recuperer les cours dans le checker et les mettre dans la liste des cours
        for cours in checker:
            prof_info["cours"].append(checker[cours])
                         
        #On trie les cours par heure de debut
        prof_info["cours"].sort(key=lambda x: x["begin"])

        #On regarde si le premier cours est en cours
        # print("UTC TIME IS ",self.date.timestamp())
        if len(prof_info["cours"])>0 and prof_info["cours"][0]["begin"] <= self.date.timestamp() and prof_info["cours"][0]["end"] >= self.date.timestamp():
            prof_info["now"]=prof_info["cours"][0]
            prof_info["cours"].remove(prof_info["now"]) #On enleve le cours de la liste des cours 
        return prof_info

    #Retourne les creneaux libres d'une salle
    def detecter_creneaux_libres_salle(self,salle:str):
        creneaux_libres = []
        #Disons qu'une salle est ouverte de 8h a 18h30
        #On crée une date de debut qui est la date actuelle à 7h45
        debut = self.date.replace(hour=7,minute=45,second=0,microsecond=0)
        #On crée une date de fin qui est la date actuelle à 19h30
        fin = self.date.replace(hour=18,minute=30,second=0,microsecond=0)

        
        #On verifie qu'on est pas plus tard que la fin
        if self.salles[salle] == [] and self.date.timestamp() < fin.timestamp():
            creneaux_libres.append([self.date.timestamp(), fin.timestamp()])
        else:
            for i in range(len(self.salles[salle])):
                if i == 0 and self.salles[salle][i].begin.timestamp() > self.date.timestamp():
                    if self.date.hour<7:
                        creneaux_libres.append([debut.timestamp(), self.salles[salle][i].begin.timestamp()])
                    else:
                        #Si il est trop tôt on met l'heure d'ouverture de l'iut
                        creneaux_libres.append([self.date.timestamp(), self.salles[salle][i].begin.timestamp()])

                elif i != 0 and self.salles[salle][i].begin.timestamp() > self.salles[salle][i-1].end.timestamp():
                    creneaux_libres.append([self.salles[salle][i-1].end.timestamp(), self.salles[salle][i].begin.timestamp()])

                if i == (len(self.salles[salle])-1):
                    #On rajoute un creneau de fin du dernier evenement a 18h30 si il n'y a pas d'evenement apres
                    creneaux_libres.append([self.salles[salle][i].end.timestamp(), fin.timestamp()])
        return creneaux_libres

    #Retourne les creneaux libres de toutes les salles
    def detecter_creneaux_libres(self):
        creneaux_libres = {}
        for salle in self.salles:
            creneaux_libres[salle] = self.detecter_creneaux_libres_salle(salle)
        return creneaux_libres


    #Renvois si la salle est libre ou non et les evenements qui se passent dans la salle aujourdhui
    def get_info_salle(self,salle:str)-> dict:
        self.need_refresh()
        data={"checked":self.date.timestamp()}
        if self.check_salle(salle) == "NOT FOUND":
            data["error"]=self.check_salle(salle)
        else:
            #res = salle + "\n"
            data["salle"]=salle
            data["now"]=None
            cours=[]
            for event in self.salles[salle]:
                if event.end.timestamp() > self.date.timestamp():
                    event_info={"name":event.name}
                    event_info["begin"]=event.begin.timestamp()
                    event_info["end"]=event.end.timestamp()
                    # event_info["begin"]=event.begin.strftime("%H:%M")
                    # event_info["end"]=event.end.strftime("%H:%M")
                    event_info["description"]=event.description
                    #On regarde si l'evenement est en cours et on le met dans now
                    if event.begin.timestamp() <= self.date.timestamp() and event.end.timestamp() >= self.date.timestamp():
                        data["now"]=event_info
                    else:
                        cours.append(event_info)

            
            data["cours"]=cours
            data["free"]=self.detecter_creneaux_libres_salle(salle)


        return data

    #Retourne les salles libres maintenant
    def get_salle_libre(self):
        self.need_refresh()
        salle_libre={}
        for salle in self.salles:
            creneau=self.detecter_creneaux_libres_salle(salle)
            if len(creneau) != 0 and creneau[0][0] <= self.date.timestamp() and creneau[0][1] >= self.date.timestamp():
                salle_libre[salle]=creneau
        #On trie les salles par rapport a la durée la plus grande maintenant et la fin du premier creneau libre
        salle_libre = dict(sorted(salle_libre.items(), key=lambda item: item[1][0][1]-item[1][0][0], reverse=True))
        return salle_libre


    def get_cours_TD(self,anneTDTP:str):
        self.need_refresh()
        data={"checked":self.date.timestamp(),"cours":[]}
        for salle in self.salles:
            for event in self.salles[salle]:
                if anneTDTP in event.url[1]:
                    data["cours"].append({"salle":salle,"name":event.name,"begin":event.begin.timestamp(),"end":event.end.timestamp()})


        #On trie les cours par rapport a la date de debut
        data["cours"] = sorted(data["cours"], key=lambda item: item["begin"])

        #On regarde si il y a des cours qui ont lieu en meme temps si c'est le gars on fusionne leurs salle
        #On pourrait rendre ca plus efficace mais j'ai la flemme parce que il faut d'abord trier les cours par rapport a la date de debut
        for i in range(len(data["cours"])):
            if i<len(data["cours"])-1 and data["cours"][i]["begin"] == data["cours"][i+1]["begin"]:
                data["cours"][i+1]["salle"] = data["cours"][i]["salle"] + "-" + data["cours"][i+1]["salle"]
                del data["cours"][i]
        return data



# t=TrouveTaSalle({
#             "1-TD1-TP1": "368",
#             "1-TD1-TP2": "369",
#             "1-TD2-TP3": "371",
#             "1-TD2-TP4": "372",
#             "1-TD3-TP5": "373",
#             "2-TD1-TP1": "394",
#             "2-TD1-TP2": "395",
#             "2-TD2-TP1": "397",
#             "2-TD2-TP2": "398"}
# ,refresh_on_init=True)
# print(t.get_cours_TD("1-TD1-TP2"))