from modules import *
import json
import os
import threading
import time, datetime
import winsound

def printTab(str, n = 1)->None:
    print('\t'*n, str)

def printDash(n=20)->None:
    print('-'*n)

def update_annonces(site, villes, prix, surface, classe, db, nouvelles_annonces):
    try:
        start = time.time()
        historique = db[site] if site in db else {}
        nouveautes = classe(villes, prix, surface).get_new_annonces(historique)
        nouvelles_annonces += [annonce for annonce in nouveautes.values()]
        for annonce in nouveautes.values():
            annonce["detection"]= datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        historique.update(nouveautes)    
        db[site]=historique
        printTab(f'{site} : OK, {len(nouveautes)} nv., {time.time()-start:.2f}s')
    except Exception as e:
        printTab(f'{site} : {str(e)}')
    
def clear_old_new(new):
    l = len(new)
    new_new = []
    curr_date = datetime.datetime.now()
    for annonce in new :
        date = datetime.datetime.strptime(annonce['detection'], "%d/%m/%Y %H:%M:%S")
        if curr_date-date < datetime.timedelta(days=7):
            new_new.append(annonce)
        
    nl = len(new_new)
    if nl < l:
        printTab(f'Nettoyage de {l-nl} anciennes annonces.')
    return new_new

def main(villes, prix, surface, sites):
    printDash()
    db_file = os.path.join(os.path.dirname(__file__), 'database', 'db.json')
    new_file = os.path.join(os.path.dirname(__file__), 'database', 'new.json')
    db = json.load(open(db_file)) if os.path.isfile(db_file) else {}
    new = json.load(open(new_file)) if os.path.isfile(new_file) else {}
    new = clear_old_new(new)
    new_annonces = []   

    threads = [threading.Thread(target=update_annonces, args=(site, villes, prix, surface, classe, db, new_annonces)) for site, classe in sites.items()]
    
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
        
    total = len(new_annonces)
    printDash()
    print(f'Nombre total de nouvelles annonces : {total}')
    [print('\t', f'{annonce["prix"]}€', f'{annonce["surface"]}m²', annonce['url']) for annonce in new_annonces]
    
    [winsound.Beep(300, 250) for i in range(total if total <= 5 else 5)]      
    
    new += new_annonces  
    
    json.dump(new, open(new_file, "w"), indent=4)
    json.dump(db, open(db_file, "w"), indent=4)
    os.system("git add *")
    os.system("git commit -m \"Mise à jour des nouvelles annonces\"")
    os.system("git push")
    

import atexit


if __name__ == "__main__":
    villes = ["Lille", "La Madeleine"]
    surface=20
    prix=850    
    sites : dict[str, Annonces]= {
        "SERGIC": SergicAnnonces,
        "FONCIA": FonciaAnnonces,
        "CITYA": CityaAnnonces,
        "VACHERAND": VacherandAnnonces,
        "LEDOUX": LedouxAnnonces,   
        "LILLE IMMO": LilleImmoAnnonces,    
        "ORPI": OrpiAnnonces,
        "NEXITY": NexityAnnonces,
        "GLV": GLVAnnonces,
        "CAVROIS": CavroisAnnonces,
        "DEFRANCE IMMO": DefranceImmoAnnonces,
        "SEIZE": SeizeAnnonces,
        "FAELENS": FaelensAnnonces,
        "C IMMO": CImmoAnnonces,
        "CHOQUET": ChoquetAnnonces,
        }
    loop = 0
    start = time.time()
    atexit.register(lambda: print(f'Fin du programme ({loop-1} boucle(s), {time.time()-start:.2f}s)'))
    
    print(f'Récupération des annonces depuis {len(sites)} sites :')
    [print('\t', site) for site in sites.keys()]
    while True:
        loop += 1
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] Boucle {loop}')
        t1 = time.time()
        main(villes, prix, surface, sites)
        t = time.time()-t1
        delta = 60*15-t
        next = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] Fin de la boucle {loop} ({t:.2f}s).')
        print(f'[{time.strftime("%d/%m/%Y %H:%M:%S")}] Prochaine boucle à {next.strftime("%H:%M:%S")} ...')
        time.sleep(delta)
        
    
    
    

    
    
    