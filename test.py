import requests
from bs4 import BeautifulSoup

from modules.Annonces import *

# url = "https://www.vacherand.fr/achat-location-biens-immobiliers-page-10"

# body = {"rech":"ok", "transaction":"location","id_type":"2"}

# import winsound

# # req = requests.post(url, json=body)
# # soup = BeautifulSoup(req.text, "html.parser")
# # infos = soup.select(".liste_biens article")
# # print(len(infos))
# # # soup = BeautifulSoup(requests.get(url).text, "html.parser")
# # # infos = soup.find_all("div", class_="infos")

# # # print(infos)

# # cityAnnonces = CityaAnnonces(['lille', 'la madeleine'], 850, 20).get_new_annonces({})
# # print(cityAnnonces)

# # vacherandAnnonces = VacherandAnnonces(['lille', 'la madeleine'], 850, 20).get_new_annonces({})
# # print(len(vacherandAnnonces))

# # ledouxAnnonces = LedouxAnnonces(['lille', 'la madeleine'], 850, 20).get_new_annonces({})
# # print(len(ledouxAnnonces)) 

# body = {
#             "location_search[commune]": 24553,
#             "location_search[typeBien][]": "1",
#             "location_search[loyer_max]": "850",
#             "location_search[surface_min]": "20",
#             "location_search[noMandat]": "",
#             "location_search[tri]": "mb.loyerCcTtcMensuel|asc",
#         }

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
#     "Content-Type":"Application/x-www-form-urlencoded; charset=UTF-8"
    
# }

# r2 = "https://www.lille-immo.fr/produits.php?ff=hab&transaction_hab=L&type_hab[]=A&type_hab[]=S&type_hab[]=T1&type_hab[]=T2&type_hab[]=T3&type_hab[]=T4&type_hab[]=T5&type_hab[]=D&ville_hab=LILLE&min_price_loc_hab=0&max_price_loc_hab=880"


# bod = "location_search[commune]=24453&location_search[rayonCommune]=0&location_search[typeBien][]=1&location_search[surface_min]=20&location_search[loyer_max]=850&location_search[noMandat]=&location_search[referenceInterne]=&location_search[secteurByFirstLetterMandat]=&location_search[loyer_min]=&location_search[piece_min]=&location_search[piece_max]=&location_search[tri]=mb.loyerCcTtcMensuel^%^7Casc"
# req = requests.post("https://lille.immodefrance-nord.com/fr/", data=bod, headers=headers)
# # req = requests.get(r2)
# soup = BeautifulSoup(req.text, "html.parser")
# with open("test.html", "w", encoding="utf-8") as f:
#     f.write(req.text)
# infos = soup.select(".article")
# print(len(infos))

annonces = CImmoAnnonces(['lille', 'la madeleine'], 1200, 20)
# print(annonces.get_raw_response())
# print(annonces.query_url())
# text = requests.get(annonces.query_url()).text

found = annonces.get_new_annonces({})

print(len(found))
print(found)