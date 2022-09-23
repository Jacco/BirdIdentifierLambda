import csv
from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

with open("./model/aiy_birds_V1_labelmap.csv", 'r') as f:
    contents = csv.DictReader(f)
    count = 0
    new_rows = []
    for bird_record in contents:
        latin_name = bird_record['name'].lower().replace(' ', '%20')
        if latin_name == "background":
            continue
        try:
            url = f"https://nl.wikipedia.org/wiki/{latin_name}"
            page = request.urlopen(url)
            soup = BeautifulSoup(page, "lxml")
            dutch_name = soup.title.contents[0].replace(' - Wikipedia', '')
            print(dutch_name)
            bird_record.update({'dutch_name': dutch_name})
            print(bird_record)
        except HTTPError as e:
            if e.getcode() == 404:
                bird_record.update({'dutch_name': '404'})
            else:
                bird_record.update({'dutch_name': 'ERROR: ' + str(e)})
        except Exception as e:
            bird_record.update({'dutch_name': 'ERROR: ' + str(e)})
        new_rows.append(bird_record)
        count += 1
        #if count >= 10:
        #    break
    with open("./model/nederland.csv", 'w') as f:
        w = csv.DictWriter(f, ["id", "name", "dutch_name"])
        w.writeheader()
        w.writerows(new_rows)


