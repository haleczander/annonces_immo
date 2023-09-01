import json, csv

# Read the JSON file
with open('db.json', encoding='utf-8') as f:
    data = json.load(f)

l=[]
keys = ["agence"]
keys += list(data['VACHERAND']['AQ010085812'].keys())
for k,v in data.items():
    for vk, vv in list(v.items()):
        a = [k.capitalize(), vk]
        for val  in list(vv.values()):
            if isinstance(val, str):
                a.append(val.replace("\n", " ").replace('"', ""))
            else:
                a.append(val)
        l.append(a)
        
# Write the data to a csv file
with open('db.csv', 'w', encoding='utf-8',newline='') as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(keys)
    writer.writerows(l)