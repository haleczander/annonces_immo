from seleniumwire import webdriver
from seleniumwire.utils import decode as decodesw
import json
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
import os


def get_requests_urls(requests):
    urls = [request.url for request in requests if request.response]
    return urls

def get_requests_responses(requests):
    responses = []
    for request in requests:
        try :
            data = decodesw(
                request.response.body,
                request.response.headers.get('Content-Encoding', 'identity')
            )
            resp = json.loads(data.decode('utf-8'))
            responses.append(resp)
        except:
            pass
    return responses




if __name__ == "__main__":  
    
    target_url = "https://www.citya.com/annonces/location/lille-59350,la-madeleine-59110?sort=b.dateMandat&direction=desc&prixMax=850&surfaceMin=20"
    driver  = webdriver.Firefox(seleniumwire_options={'disable_encoding': True})
    driver.get(target_url)
    urls = get_requests_urls(driver.requests)
    responses = get_requests_responses(driver.requests)
    driver.close()
    [print(url) for url in urls]
    json.dump(responses, open('data.json', 'w'))