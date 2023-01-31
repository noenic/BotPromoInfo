from ics  import *
import time
import requests
import datetime
import concurrent 
import concurrent.futures
# #On créer une date et une heure pour tester , ici le 5 janvier 2023 a 8h24
# #date = datetime.datetime(2023, 2, 2, 1, 24, 1)
# date = datetime.datetime.now()
# #Si la date est en week-end on arrete
# if date.weekday() == 5 or date.weekday() == 6:
#     print("L'iut est fermé le week-end")
#     exit()

# #on le met en UTC IMPORTANT 
# date = date.replace(tzinfo=datetime.timezone.utc)
# salles={}

# #Fonction qui recupere le calendrier de l'URL et est threadé pour etre appeler en parallèle
# def get_TD_ics(url:str)-> str:
#     return requests.get(url).text




# def get_TD_salle(c:Calendar)-> dict: 

#     # On recupere les evenements du calendrier
#     events = list(c.events)
#     #On les trie par date et heure de debut
#     events.sort(key=lambda x: x.begin.timestamp())


#     salles_TD = {}
#     for event in events:
#         #Je ne sais pas pourquoi mais les evenements sont en UTC donc on ajoute une heure
#         event.end = event.end + datetime.timedelta(hours=1)
#         event.begin = event.begin + datetime.timedelta(hours=1)


#         #On ne garde que les évènements du jour et si l'evenement est le jour d'après, on quitte
#         if event.begin.timestamp() > date.timestamp() and event.begin.date().day != date.day:
#             break
        

        
#         #On ne traite que les évènements du jour qui ne sont pas passés
#         if event.end.timestamp() > date.timestamp():
#             if event.location != None:
#                 nds= event.location
#                 #On enleve les S.
#                 nds = nds.replace("S.","")
#                 #on split à la virgule si il y en a une
#                 nds = nds.split(",")
#                 for i in range(len(nds)):
#                     #Si le premier caractere est un 0 on le supprime
#                     if len(nds[i])>0 and nds[i][0] == "0":
#                         nds[i] = nds[i][1:]

#                     #On regarde si la salle est deja dans le dictionnaire
#                     if nds[i] in salles_TD:
#                         #Si oui on ajoute l'evenement a la liste
#                         salles_TD[nds[i]].append(event)
#                     else:
#                         #Si non on cree la salle avec l'evenement
#                         salles_TD[nds[i]] = [event]


#     return(salles_TD)


# #Retourne les creneaux libres d'une salle
# def detecter_creneaux_libres_salle(salle:str):
#     if salle not in salles:
#         raise ValueError("La salle n'existe pas")
#     creneaux_libres = []
#     #Disons qu'une salle est ouverte de 8h a 18h30
#     fin = datetime.datetime(date.year, date.month, date.day, 18, 30, 0,tzinfo=datetime.timezone.utc)
#     for i in range(len(salles[salle])):
#         if i == 0 and salles[salle][i].begin.timestamp() > date.timestamp():
#             creneaux_libres.append([date.timestamp(), salles[salle][i].begin.timestamp()])
#         elif i != 0 and salles[salle][i].begin.timestamp() > salles[salle][i-1].end.timestamp():
#             creneaux_libres.append([salles[salle][i-1].end.timestamp(), salles[salle][i].begin.timestamp()])

#         if i == len(salles[salle])-1 and (salles[salle][i].end.strftime("%H:%M:%S") < fin.strftime("%H:%M:%S")):
#             #On rajoute un creneau de fin du dernier evenement a 18h30 si il n'y a pas d'evenement apres
#             creneaux_libres.append([salles[salle][i].end.timestamp(), fin.timestamp()])
#     return creneaux_libres

# #Retourne les creneaux libres de toutes les salles
# def detecter_creneaux_libres(salles: dict):
#     creneaux_libres = {}
#     for salle in salles:
#         creneaux_libres[salle] = detecter_creneaux_libres_salle(salle)
#     return creneaux_libres







# #Renvois si la salle est libre ou non et les evenements qui se passent dans la salle aujourdhui
# def get_info_salle(salle:str)-> str:
#     data={}
#     if salle not in salles:
#         data["error"]="La salle n'existe pas"
#         return data
        
#     else:
#         #res = salle + "\n"
#         data["salle"]=salle
#         data["now"]=None
#         cours=[]
#         for event in salles[salle]:
#             if event.end.timestamp() > date.timestamp():
#                 event_info={"name":event.name}
#                 event_info["begin"]=event.begin.timestamp()
#                 event_info["end"]=event.end.timestamp()
#                 # event_info["begin"]=event.begin.strftime("%H:%M")
#                 # event_info["end"]=event.end.strftime("%H:%M")
#                 event_info["description"]=event.description
#                 cours.append(event_info)
#                 #On regarde si l'evenement est en cours et on le met dans now
#                 if event.begin.timestamp() <= date.timestamp() and event.end.timestamp() >= date.timestamp():
#                     data["now"]=event_info
        
#         data["cours"]=cours
#         data["free"]=detecter_creneaux_libres_salle(salle)


#         return data

# def get_prof(prof:str):
#     #On met le prof en majuscule car les noms sont en majuscule dans les descriptions
#     prof=prof.upper()
#     prof_info={"name":prof}
#     prof_info["now"]=None
#     prof_info["cours"]=[]
#     for salle in salles:
#         for event in salles[salle]:
#             if event.description != None and prof in event.description:

#                 #On regarde le cours à pas deja ete ajoute (TD-TP)
#                 for avantcour in prof_info["cours"]:
#                     if avantcour["name"] == event.name and avantcour["begin"] == event.begin.timestamp() and avantcour["end"] == event.end.timestamp():
#                         #On ajoute la salle de l'element a la salle de l'element deja existant
#                         avantcour["salle"]+="-"+salle
#                         break

#                 else: 
#                     event_info={"name":event.name}
#                     event_info["begin"]=event.begin.timestamp()
#                     event_info["end"]=event.end.timestamp()
#                     # event_info["begin"]=event.begin.time().strftime("%H:%M")
#                     # event_info["end"]=event.end.time().strftime("%H:%M")
#                     event_info["salle"]=salle


#                     #On regarde si le prof est en cours au moment actuel et on met la salle dans la variable now 
#                     if event.begin.timestamp() <= date.timestamp() and event.end.timestamp() >= date.timestamp():
#                         prof_info["now"]=event_info
#                     prof_info["cours"].append(event_info)

#     #On trie les cours par heure de debut
#     prof_info["cours"].sort(key=lambda x: x["begin"])
#     return prof_info
                

# #Retourne les salles libres maintenant
# def get_salle_libre():
#     salle_libre={}
#     for salle in salles:
#         creneau=detecter_creneaux_libres_salle(salle)
#         if len(creneau) != 0 and creneau[0][0] <= date.timestamp() and creneau[0][1] >= date.timestamp():
#             salle_libre[salle]=creneau
#     #On trie les salles par rapport a la durée la plus grande maintenant et la fin du premier creneau libre
#     salle_libre = dict(sorted(salle_libre.items(), key=lambda item: item[1][0][1]-item[1][0][0], reverse=True))
#     return salle_libre


# '''
# 1 : Pour les TDs de BUT informatique première année et deuxième année
# 988 : pour les LP-PA 
# 240 : pour les LP-GEN/AV
# 239 : pour les LP-info

# --------je save ca juste au cas où----------------
#            1TD1    1TD2    1TD3  2TDA    2TDD    LP-PA   LP-GEN/AV     LP-info
# listeID= ["367" , "370" , "373","394" , "589" , "988",      "240"  ,  "239"]
# listeID= ["366","392", "239","240"]
# --------------------------------------------------
# '''
# def scrap_TD():
#     listeID=["1","988","240","239"]
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         #On fait les requetes en parallèle (Parce que c'est long)
#         futures = [executor.submit(get_TD_ics, "https://www.iutbayonne.univ-pau.fr/outils/edt/default/export?ID="+ID) for ID in listeID]
#         for future in concurrent.futures.as_completed(futures):
#             TD = future.result()
#             res_TD=get_TD_salle(Calendar(TD))
#             for salle in res_TD:
#                 if salle in salles:
#                     salles[salle]+=res_TD[salle]
#                 else:
#                     salles[salle]=res_TD[salle]  



#     #On trie les events de chaque salle par date de debut et on les evenement qui commencent et se terminent au meme moment (doublons)
#     for salle in salles:
#         salles[salle].sort(key=lambda x: x.begin.timestamp())
#         i = 0
#         #On supprime les doublons
#         while i < len(salles[salle])-1:
#             #Si l'evenement commence et se termine au meme moment que l'evenement suivant on supprime l'evenement suivant (doublon)
#             if salles[salle][i].begin.timestamp() == salles[salle][i+1].begin.timestamp() and salles[salle][i].end.timestamp() == salles[salle][i+1].end.timestamp():
#                 salles[salle].pop(i)
#             else:
#                 i+=1



class TrouveTaSalle():
    def __init__(self,listeID:list):
        if type(listeID) != list:
            raise TypeError("listeID doit etre une liste")
        if len(listeID) == 0:
            raise ValueError("listeID doit contenir au moins un element")
        self.listeID=listeID
        self.listeSallesPC=["15","17","21","22","23","24","25","25","26","130","128"]
        self.listeSallesTD=["124","125","126","127","129"]
        self.salles={}
        #On initialise a 0 pour trigger le refresh au premier appel
        self.refresh()

    '''
    Recupere le fichier ics de l'emplois du temps de L'ID dans l'url
    '''
    def get_TD_ics(self,url:str)-> str:
        return requests.get(url).text
        
    
    '''
    Recupere les salles, les cours et les profs de l'emplois du temps
    On le fait en parallèle pour gagner du temps (On fait les requetes en thread)
    '''
    def refresh(self):
        self.date=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        # #On met la date de demain à 8h
        # self.date=self.date+datetime.timedelta(days=1)
        # self.date=self.date.replace(hour=8,minute=0,second=0,microsecond=0)
        print("[Salles] Refresh des emplois du temps...",self.date.strftime("%d/%m/%Y %H:%M:%S"))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #On fait les requetes en parallèle (Parce que c'est long)
            futures = [executor.submit(self.get_TD_ics, "https://www.iutbayonne.univ-pau.fr/outils/edt/default/export?ID="+ID) for ID in self.listeID]
            for future in concurrent.futures.as_completed(futures):
                TD = future.result()
                res_TD=self.get_TD_salle(Calendar(TD))
                #print("refresh",res_TD)
                for salle in res_TD:
                    if salle in self.salles:
                        self.salles[salle]+=res_TD[salle]
                    else:
                        self.salles[salle]=res_TD[salle]

        
        
        #On trie les events de chaque salle par date de debut et on les evenement qui commencent et se terminent au meme moment (doublons)
        for salle in self.salles:
            self.salles[salle].sort(key=lambda x: x.begin.timestamp())
            i = 0
            #On supprime les doublons
            while i < len(self.salles[salle])-1:
                #Si l'evenement commence et se termine au meme moment que l'evenement suivant on supprime l'evenement suivant (doublon)
                if self.salles[salle][i].begin.timestamp() == self.salles[salle][i+1].begin.timestamp() and self.salles[salle][i].end.timestamp() == self.salles[salle][i+1].end.timestamp():
                    self.salles[salle].pop(i)
                else:
                    i+=1
        

    def get_TD_salle(self,c:Calendar)-> dict: 
        # On recupere les evenements du calendrier
        events = list(c.events)
        #On les trie par date et heure de debut
        events.sort(key=lambda x: x.begin.timestamp())
        salles_TD = {}
        for event in events:
            #Je ne sais pas pourquoi mais les evenements sont en UTC donc on ajoute une heure
            event.end = event.end + datetime.timedelta(hours=1)
            event.begin = event.begin + datetime.timedelta(hours=1)

            #On ne garde que les évènements du jour et si l'evenement est le jour d'après, on quitte
            if event.begin.timestamp() > self.date.timestamp() and event.begin.date().day != self.date.day:
                break
            
            #On ne traite que les évènements du jour qui ne sont pas passés
            elif event.end.timestamp() > self.date.timestamp():

                if event.location != None:
                    nds= event.location
                    #On enleve les S.
                    nds = nds.replace("S.","")
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
        if datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)-self.date > datetime.timedelta(minutes=5) or len(self.salles) == 0:
            print("[Salles] On refresh")
            self.refresh()
        else: 
            print("[Salles] Pas besoin de refresh, dernier refresh le",self.date.strftime("%d/%m/%Y %H:%M:%S"))


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
        for salle in self.salles:
            for event in self.salles[salle]:
                if event.description != None and prof in event.description:
                    #On regarde le cours à pas deja ete ajoute (TD-TP)
                    for avantcour in prof_info["cours"]:
                        if avantcour["name"] == event.name and avantcour["begin"] == event.begin.timestamp() and avantcour["end"] == event.end.timestamp():
                            #On ajoute la salle de l'element a la salle de l'element deja existant
                            avantcour["salle"]+="-"+salle
                            break

                    else: 
                        event_info={"name":event.name}
                        event_info["begin"]=event.begin.timestamp()
                        event_info["end"]=event.end.timestamp()
                        # event_info["begin"]=event.begin.time().strftime("%H:%M")
                        # event_info["end"]=event.end.time().strftime("%H:%M")
                        event_info["salle"]=salle


                        #On regarde si le prof est en cours au moment actuel et on met la salle dans la variable now 
                        if event.begin.timestamp() <= self.date.timestamp() and event.end.timestamp() >= self.date.timestamp():
                            prof_info["now"]=event_info
                        prof_info["cours"].append(event_info)

        #On trie les cours par heure de debut
        prof_info["cours"].sort(key=lambda x: x["begin"])
        return prof_info

    #Retourne les creneaux libres d'une salle
    def detecter_creneaux_libres_salle(self,salle:str):
        creneaux_libres = []
        #Disons qu'une salle est ouverte de 8h a 18h30
        fin = datetime.datetime(self.date.year, self.date.month, self.date.day, 18, 30, 0,tzinfo=datetime.timezone.utc)
        for i in range(len(self.salles[salle])):
            if i == 0 and self.salles[salle][i].begin.timestamp() > self.date.timestamp():
                creneaux_libres.append([self.date.timestamp(), self.salles[salle][i].begin.timestamp()])
            elif i != 0 and self.salles[salle][i].begin.timestamp() > self.salles[salle][i-1].end.timestamp():
                creneaux_libres.append([self.salles[salle][i-1].end.timestamp(), self.salles[salle][i].begin.timestamp()])

            if i == len(self.salles[salle])-1 and (self.salles[salle][i].end.strftime("%H:%M:%S") < fin.strftime("%H:%M:%S")):
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
    def get_info_salle(self,salle:str)-> str:
        self.need_refresh()
        data={"checked":self.date.timestamp()}
        if self.check_salle(salle) != True:
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
                    cours.append(event_info)
                    #On regarde si l'evenement est en cours et on le met dans now
                    if event.begin.timestamp() <= self.date.timestamp() and event.end.timestamp() >= self.date.timestamp():
                        data["now"]=event_info
            
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




# t=TrouveTaSalle(["1","988","240","239"])
# print(t.get_info_salle("128"))