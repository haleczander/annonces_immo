from abc import ABC, abstractmethod
from modules.Annonce import Annonce
import requests
from bs4 import BeautifulSoup


class Annonces(ABC):
    redibitoires = ["colocation", "coloc",
                    "co-location", "rez-de-chaussée", " rdc "]

    slugs = {}

    def __init__(self, site: str, villes: list[str], prix: int, surface: int) -> None:
        self.site = site
        self.villes = villes
        self.prix = prix
        self.surface = surface

    def get_slugs_villes(self) -> list[str]:
        slugs = []
        for ville in self.villes:
            if ville.lower() in self.slugs:
                slugs.append(self.slugs[ville.lower()])
            else:
                print(
                    f"La ville {ville} n'est pas associée à un slug {self.site}")
        return slugs

    @abstractmethod
    def query_url(self) -> str:
        pass

    @abstractmethod
    def get_raw_response(self) -> dict:
        pass

    def get_api_response(self, url: str) -> dict:
        return requests.get(url).json()

    def post_api_response(self, url: str) -> dict:
        return requests.post(url, headers=self.request_headers(), json=self.request_body()).json()

    def get_html_response(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(requests.get(url).text, 'html.parser')

    def request_body(self) -> dict:
        return None
    
    def html_to_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    def request_headers(self) -> dict:
        return None

    @abstractmethod
    def format_raw_response(self, raw_response: dict) -> dict:
        pass

    def is_redibitoire(self, description):
        for redibitoire in self.redibitoires:
            if redibitoire in description.lower():
                return True
        return False

    def extract_new_annonces(self, formatted_response: dict, old_annonces: dict) -> dict:
        new_annonces = {ref: annonce for ref, annonce in formatted_response.items(
        ) if ref not in old_annonces}
        return new_annonces

    def merge_annonces(self, new_annonces: dict, old_annonces: dict) -> dict:
        return old_annonces.update(new_annonces)

    def get_new_annonces(self, old_annonces: dict) -> dict:
        raw_response = self.get_raw_response()
        formatted_response = self.format_raw_response(raw_response)
        new_annonces = self.extract_new_annonces(
            formatted_response, old_annonces)
        return new_annonces


class SergicAnnonces(Annonces):
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        return super().__init__("Sergic", villes, prix, surface)

    def query_url(self, ville: str) -> str:
        return f'https://www.sergic.com/wp-json/sergic/v1/post?params[contract_type]=location&params[place_types][]=appartement&params[dispo]=all&params[localisation_srch]=false&params[professional_announcement]=false&params[expanse_srch]=0&params[appt_min_area]={self.surface}&params[price_min]=0&params[price_max]={self.prix}&params[ref]=&params[isRef]=false&params[zoomed]=&params[citySearch]={ville}&params[place]=&params[lat_move_map]=&params[lng_move_map]=&params[zoom_move_map]=&params[agency_siret]='

    def get_raw_response(self) -> dict:
        response = []
        for ville in self.villes:
            target_url = self.query_url(ville)
            api_resp = self.get_api_response(target_url)
            if isinstance(api_resp, bool):
                print(f"La ville {ville} n'a pas de résultats")
                continue
            response += self.get_api_response(target_url)
        return response

    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            annonce_html = self.get_html_response(annonce["link"])
            description = annonce_html.find(
                "div", {"class": "appt-desc__description-text-paragraph"}).text
            if self.is_redibitoire(description):
                continue
            images = [image["src"] for image in annonce_html.select(
                ".appt-desc__carousel-container img")]
            annonce_obj: Annonce = Annonce(
                reference=annonce["ref"],
                ville=annonce["city"],
                prix=annonce["price"],
                surface=annonce["area"],
                url=annonce["link"],
                description=description,
                images=images,
                coordonnees=(annonce["lat"], annonce["lng"]),
                disponibilite=annonce["disponibility"]
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response


class FonciaAnnonces(Annonces):
    slugs = {
        'lille': 'lille-59',
        'la madeleine': 'la-madeleine-59110'
    }

    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Foncia', villes, prix, surface)

    def query_url(self) -> str:
        return "https://fnc-api.prod.fonciatech.net/annonces/annonces/search"

    def request_body(self) -> dict:
        slugs = self.get_slugs_villes()
        return {
            "type": "location",
            "filters": {
                "localities": {
                    "slugs": slugs
                },
                "surface": {
                    "min": self.surface
                },
                "prix": {
                    "max": self.prix
                }
            },
            "expandNearby": False,
            "size": 100
        }

    def get_raw_response(self) -> dict:
        resp = self.post_api_response(self.query_url())
        return resp

    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response["annonces"]:
            description = annonce["description"]
            if self.is_redibitoire(description):
                continue
            images = annonce["medias"] if "medias" in annonce else []
            annonce_obj: Annonce = Annonce(
                reference=annonce["reference"],
                ville=annonce["localisation"]["locality"]["libelle"],
                prix=annonce["loyer"],
                surface=annonce["surface"]["totale"],
                url=f'https://fr.foncia.com{annonce["canonicalUrl"]}',
                description=description,
                images=images,
                publication=annonce["datePublication"],
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response


class CityaAnnonces(Annonces):
    slugs = {
        'lille': 'lille-59350',
        'la madeleine': 'la-madeleine-59110'
    }

    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Citya', villes, prix, surface)

    def query_url(self, page) -> str:
        slugs = self.get_slugs_villes()
        villes = ','.join(slugs)
        return f"https://www.citya.com/annonces/location/{villes}?l&prixMax={self.prix}&surfaceMin={self.surface}&page={page}"

    def get_raw_response(self) -> list:
        response = []
        page = 1
        while True:
            page_resp = self.get_html_response(self.query_url(page))
            annonces = page_resp.select("ul.list-biens > li > article")
            if not annonces:
                break
            response += annonces
            page += 1
        return response

    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            description = annonce.find("p", class_="description-start").text
            if self.is_redibitoire(description):
                continue
            url = annonce.find("a").get("href")
            ref = url.split("/")[-1]
            prix = annonce.find("p", class_="prix").text.split(" ")[0][:-2]
            surface = annonce.select_one(
                "h3 > strong").text.split(" ")[-1][:-2]
            ville = " ".join(annonce.find(
                "p", class_="ville").text.split(" ")[:-1])
            annonce_obj: Annonce = Annonce(
                reference=ref,
                ville=ville,
                prix=prix,
                surface=surface,
                url=f'https://www.citya.com{url}',
                description=description,
                images=[],
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response


class VacherandAnnonces(Annonces):
    slugs = {
        'lille': 6,
        'la madeleine': 19
    }

    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Vacherand', villes, prix, surface)

    def query_url(self, page) -> str:
        return f'https://www.vacherand.fr/achat-location-biens-immobiliers-page-{page}'

    def request_body(self) -> dict:
        return {
            "rech": "ok", 
            "transaction": "location", 
            "id_type[]": 2, 
            "prix_max": self.prix, 
            "id_ville[]": self.get_slugs_villes(), 
            "surface_min": self.surface}
        
    def request_headers(self) -> dict:
        return  {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
        }

    def get_raw_response(self) -> list:
        response = []
        page = 1
        per_page = 8
         
        while True: 
            page_resp = requests.post(self.query_url(page), data=self.request_body()).text
            soup = self.html_to_soup(page_resp)
            nb = int(soup.find("span", class_="nb").text.split(" ")[-2])
            annonces = soup.select(".liste_biens article") 
            response += annonces
            if nb <= page * per_page:
                break
            page += 1
        return response
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            description = annonce.find("div", class_="description").text
            if self.is_redibitoire(description):
                continue
            url = annonce.select_one("a.detail").get("href")
            ref = url.split("/ref-")[-1]
            prix = annonce.find("span", class_="prix").text.split(" ")[0]
            ti18 = annonce.find("h3", class_="ti18").text
            surface = ti18.split("m²")[0].split(" ")[-1]
            ville = ti18.split("m²")[1].strip()
            images = [image.get("src") for image in annonce.select(".bien img")]
            annonce_obj: Annonce = Annonce(
                reference=ref,
                ville=ville,
                prix=prix,
                surface=surface,
                url=f'https://www.vacherand.fr/{url}',
                description=description,
                images=images,
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response
   
 
class LedouxAnnonces(Annonces):
    slugs = {
        'lille': 59350,
        'la madeleine': 59368
    }
    
    
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Cabinet Ledoux', villes, prix, surface)   
        

    def query_url(self, page) -> str:
        insee = "&".join([f"insee[]={slug}" for slug in self.get_slugs_villes()])
        
        return f"https://www.ledoux.fr/fr/data_listing_formrecherche.html?{insee}&prixmax={self.prix}&surfacemin={self.surface}?page={page}"
    
    def get_raw_response(self) -> dict:
        response = []
        page = 1
        while True:
            page_resp = requests.get(self.query_url(page)).json()
            last_page = page_resp["data"]["resultats"]["last_page"]
            response += page_resp["data"]["resultats"]["data"]
            page += 1
            if page > last_page:
                break
        return response
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            description = annonce["descriptif"]
            if self.is_redibitoire(description):
                continue
            url = f'{annonce["type"]}-{annonce["loc"]}-{annonce["ville"]}-{annonce["cpdep"]}-{annonce["idhabit"]}.html'.replace(" ","-")
            annonce_obj: Annonce = Annonce(
                reference=str(annonce["idhabit"]),
                ville = annonce["ville"],
                prix=annonce["prix"],
                surface=annonce["surface"],
                url=f'https://www.ledoux.fr/{url}',
                description=description,
                images=[],
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response

class ImmoDeFranceAnnonces(Annonces):
    slugs = {
        'lille': 24453,
        'la madeleine': 24471
    }
    
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Immo de France', villes, prix, surface)
        
    def query_url(self, page) -> str:
        return "https://www.immodefrance.com/fr/locations"
    
    def request_body(self, ville) -> dict:
        slug = self.slugs[ville.lower()]
        return {
            "location_search[commune]": slug,
            "location_search[rayonCommune]": 0,
            "location_search[typeBien][]": 1,
            "location_search[surface_min]": self.surface,
            "location_search[loyer_max]": self.prix
        }
        
    def get_raw_response(self) -> dict:
        response = []
        
class LilleImmoAnnonces(Annonces):
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Lille Immo', villes, prix, surface)
        
    def query_url(self) -> str:
        return f"https://www.lille-immo.fr/produits.php?ff=hab&transaction_hab=L&type_hab[]=A&type_hab[]=S&type_hab[]=T1&type_hab[]=T2&type_hab[]=T3&type_hab[]=T4&type_hab[]=T5&type_hab[]=D&ville_hab=LILLE&min_price_loc_hab=0&max_price_loc_hab={self.prix}"
    
    def get_raw_response(self) -> dict:
        page_resp = requests.get(self.query_url()).text
        soup = self.html_to_soup(page_resp)
        annonces = soup.select(".annonce")
        return annonces
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            description = annonce.find("div", class_="desc_hover_wrap").text
            if self.is_redibitoire(description):
                continue
            url = annonce.select_one("a.cursor").get("href")
            ref = annonce.get("id")
            prix = annonce.find("p", class_="price").text.split(" ")[0]
            surface = annonce.select_one('ul li').text.split("m²")[0].split(" ")[-1]
            if int(surface) < self.surface:
                continue
            ville = annonce.select_one(".desc h2 strong").text.split("à")[1].strip()
            images = []
            annonce_obj: Annonce = Annonce(
                reference=ref,
                ville=ville,
                prix=prix,
                surface=surface,
                url=url,
                description=description,
                images=images,
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response
    
class OrpiAnnonces(Annonces):
    def  __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Orpi', villes, prix, surface)
        
    def query_url(self) -> str:
        return f'https://www.orpi.com/recherche/ajax/rent?realEstateTypes[]=appartement&locations[0][value]=lille&locations[0][label]=Lille (59000)&locations[1][value]=la-madeleine&locations[1][label]=La Madeleine (59110)&minSurface={self.surface}&maxPrice={self.prix}&sort=date-down&layoutType=mixte&recentlySold=false'
    
    def get_raw_response(self) -> dict:
        return self.get_api_response(self.query_url())
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response["items"]:
            description = annonce["longAd"]
            if self.is_redibitoire(description):
                continue

            annonce_obj: Annonce = Annonce(
                reference=annonce['reference'],
                ville=annonce['location'],
                prix=annonce['price'],
                surface=annonce['surface'],
                url=f'https://www.orpi.com/annonce-location-{annonce["slug"]}',
                description=description,
                images=annonce['images'],
                coordonnees=(annonce['latitude'], annonce['longitude']),
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response
    
class NexityAnnonces(Annonces):
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__('Nexity', villes, prix, surface)
        
    def query_url(self) -> str:
        return f"https://www.nexity.fr/annonces-immobilieres/location/immobilier/tout/france?budget_max={self.prix}&locationsId%5B0%5D=29397&locationsId%5B1%5D=29399&surface_min={self.surface}&types_bien%5B0%5D=appartement"

    def get_raw_response(self) -> dict:
        page_resp = requests.get(self.query_url()).text
        soup = self.html_to_soup(page_resp)
        annonces = soup.select(".product")
        return annonces
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            link = annonce.select_one("a").get("href")
            ref = link.split("/")[-1]
            card = annonce.select_one(".product-card-content")
            if not card : continue
            prix = card.select_one(".pricing").text.split("€")[0].strip()
            ville = annonce.select_one(".location").text.split(" ")[0]
            surface = annonce.select_one(".details").text.split(" | ")[-1].split("m")[0]
            annonce_obj = Annonce(
                reference=ref,
                ville=ville,
                prix=prix,
                surface=surface,
                url=f'https://www.nexity.fr{link}',
                description="",
                images=[],
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response
    
class GLVAnnonces(Annonces):
    def __init__(self, villes: list[str], prix: int, surface: int) -> None:
        super().__init__("GLV Immobilier", villes, prix, surface)
        
    def query_url(self) -> str:
        return f"https://www.glv-immobilier.fr/catalog/advanced_search_result.php?action=update_search&search_id=1775915508437856&C_28_search=EGAL&C_28_type=UNIQUE&C_28=Location&C_28_tmp=Location&C_65_search=CONTIENT&C_65_type=TEXT&C_65=59110+LA-MADELEINE%2C59000+LILLE&C_65_tmp=59110+LA-MADELEINE&C_65_tmp=59000+LILLE&C_27_search=EGAL&C_27_type=TEXT&C_27=1&C_27_tmp=1&C_34_MIN={self.surface}&C_34_search=COMPRIS&C_34_type=NUMBER&C_30_MAX={self.prix}&keywords=&C_34_MAX=&C_30_MIN=&C_30_search=COMPRIS&C_30_type=NUMBER&C_36_MIN=&C_36_search=COMPRIS&C_36_type=NUMBER&C_36_MAX="
    
    def get_raw_response(self) -> dict:
        page_resp = requests.get(self.query_url()).text
        soup = self.html_to_soup(page_resp)
        annonces = soup.select(".item-card")
        return annonces
    
    def format_raw_response(self, raw_response: dict) -> dict:
        formatted_response = {}
        for annonce in raw_response:
            description = annonce.select_one(".products-description").text
            if self.is_redibitoire(description):
                continue
            link = annonce.select("a")[1].get("href")[2:]
            ref = annonce.select_one(".products-ref").text.split(" : ")[-1].strip()
            prix = annonce.select_one(".price-bold").text.split(" ")[0]
            ville = annonce.select_one(".products-city").text
            surface = None
            annonce_obj = Annonce(
                reference=ref,
                ville=ville,
                prix=prix,
                surface=surface,
                url=f'https://www.glv-immobilier.fr{link}',
                description="",
                images=[],
            )
            formatted_response.update(annonce_obj.dict())
        return formatted_response
        