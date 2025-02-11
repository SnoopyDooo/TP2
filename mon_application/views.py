from django.shortcuts import render
from .models import Pays
import re
import requests
import sys
from bs4 import BeautifulSoup
from django.http import HttpResponse

sys.stdout.reconfigure(encoding='utf-8')

def liste_pays(request):
    pays = Pays.objects.all()
    return render(request, 'pays.html', {'pays': pays})

def dms_to_decimal(coord):
    match = re.match(r"(\d+)° (\d+)′ (\d+)″ ([nNsSoO])", coord)
    if match:
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        direction = match.group(4).upper()

        decimal = degrees + (minutes / 60) + (seconds / 3600)
        if direction in ['S', 'O']:  # Sud ou Ouest doivent être négatifs
            decimal *= -1
        return decimal
    return None  # Si le format ne correspond pas

def afficher_pays(request):
    if request.method == 'POST':
        pays = request.POST.get('selected')
        pays2 = pays.replace(" ","_")
        #URL1
        url1 = "https://fr.wikipedia.org/wiki/Liste_des_pays_par_population"
        response = requests.get(url1)
        soup1 = BeautifulSoup(response.content, 'html.parser')

        table = soup1.find('table')
        tr = table.find_all("tr") 
        i = 0
        found = False
        for row in tr:
            td = row.find_all("td")
            j = 0
            for cell in td :
                if cell.text.strip().lower() == pays.lower(): 
                    found = True
                    break
                else : 
                    j += 1
            if found :
                break
            i += 1
        print(f"VOICI {i}")
        row = tr[i] 
        td = row.find_all("td")
        nb_population = td[j+1].text.strip().replace(" ","")

        #URL2
        url2 = f"https://fr.wikipedia.org/wiki/{pays2}"
        response = requests.get(url2)
        soup2 = BeautifulSoup(response.content, 'html.parser')

        table2 = soup2.find_all('table')
        tr = table2[2].find_all("tr")
        i = 0
        found = False

        for row in tr:
            th = row.find("th")
            if th and th.find('a') and 'title' in th.find('a').attrs:  # Vérifie que th, <a>, et l'attribut 'title' existent
                if th.find('a')['title'] == "Langue officielle":
                    found = True
                    break
            i += 1

        if found:
            langue_off = tr[i].find("td").text.strip()
        else:
            langue_off = "Langue officielle non trouvée" 
            
        i = 0
        found = False
        for row in tr:
            th = row.find("th")
            if th.text == "Capitale": 
                found = True
                break
            i += 1
        nom_capitale = tr[i].find("td").find("a").text.strip()
        i = 0
        found = False
        tr = table2[3].find_all("tr")
        for row in tr:
            th = row.find("th")
            if th.text == "Superficie totale": 
                found = True
                break
            i += 1
        superficie = tr[i].find("td").text.strip() 

        #URL3    
        url3 = f"https://fr.wikipedia.org/wiki/{nom_capitale}"
        response = requests.get(url3)
        soup3 = BeautifulSoup(response.content, 'html.parser')

        table3 = soup3.find("table")
        tr = table3.find_all("tr")
        i = 0
        found = False
        for row in tr:
            th = row.find("th")
            if th and th.find('a'):  # Vérifie si th n'est pas None et contient un <a>
                if th.find('a').text.strip() == "Population":
                    found = True
                    break
            i += 1

        habitant_capitale = tr[i].find("td").text
        i = 0
        found = False
        for row in tr:
            th = row.find("th")
            if th and th.find('a'):  # Vérifie si th n'est pas None et contient un <a>
                if th.find('a').text.strip() == "Coordonnées":
                    found = True
                    break
            i += 1

        coordonnee = tr[i].find("td").get_text(separator=' ', strip=True)
        coordonnee = coordonnee.split(", ")
        longitude = coordonnee[1]
        latitude = coordonnee[0]
        
        latitude_decimal = dms_to_decimal(latitude)
        longitude_decimal = dms_to_decimal(longitude)

        return render(request, 'info.html', {
            'pays': pays,
            'nb_population': nb_population,
            'langue_off': langue_off,
            'nom_capitale': nom_capitale,
            'superficie': superficie,
            'habitant_capitale': habitant_capitale,
            'latitude': latitude,
            'longitude': longitude,
            'latitude_decimal': latitude_decimal,
            'longitude_decimal': longitude_decimal
            })
    else:
        return HttpResponse("Méthode non autorisée.", status=405)
