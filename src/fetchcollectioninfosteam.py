import requests
from time import sleep


# empty text file
f = open("collections.txt", "w", encoding='utf-8')
f.write("")
f.close()

items = set()

steam_item_count = 1
i = 0
while i < steam_item_count:
    qurl = f'https://steamcommunity.com/market/search/render?norender=1&start={i}&count={i+99}&appid=730'
    try:
        r = requests.get(url=qurl)
        r = r.json()

        steam_item_count = int(r['total_count']) if steam_item_count<int(r['total_count']) else steam_item_count
        r = r['results']

        for x in r:
            try:
                if(len(x['asset_description']['descriptions'])<5):
                    continue

                if('Collection' in x['asset_description']['descriptions'][4]['value']):
                    new_elem = (x['name'],x['asset_description']['descriptions'][4]['value'])
                    items.add(new_elem)
                    print(new_elem)
            except Exception as e:
                continue

        print(f'{i+100} / {steam_item_count}')

        i = i + 100
        sleep(12)

    except Exception as e:
        print("cannot access steam")
        sleep(60)


# write to file
f = open("collections.txt", "a", encoding='utf-8')
for x in items:
    f.write(f'{(x[0])[:x[0].find("(")]}:{x[1]}\n')
f.close()