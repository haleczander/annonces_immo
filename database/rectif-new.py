import json
import datetime

db = json.load(open('database/db.json'))
new = []
curr_date = datetime.datetime.now()
for agence, annonces in db.items():
    for ref, annonce in annonces.items():
        if not 'detection' in annonce:
            continue
        date =  datetime.datetime.strptime(annonce['detection'], "%d/%m/%Y %H:%M:%S")
        if curr_date-date < datetime.timedelta(days=3):
            new.append(annonce)
            
json.dump(new, open('database/new.json', 'w'), indent=4)