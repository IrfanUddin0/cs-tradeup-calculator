import requests
from dataclasses import dataclass
from enum import Enum
import urllib.parse
from datetime import datetime

from typing import List


class Rarity(Enum):
    consumergrade = 0
    industrialgrade = 1
    milspecgrade = 2
    restricted = 3
    classified = 4
    covert = 5
    undefined = -1


@dataclass
class Price:
    currency: str
    ammount: int


@dataclass
class Item:
    Name: str
    Rarity: Rarity
    Collection: str
    Price: Price
    Wear: str

class TradeUpCalculator:
    def __init__(self, currency: str = 'GBP') -> None:
        self.currency = currency
        self.prices = self.fetchPrices()

    def findCollectionName(self, ItemName) -> str | None:
        def search_string_file(lines: List[str], string):
            for x in lines:
                if string in x:
                    return (x[x.rfind(":"):].replace(':','')).replace('\n','')
            return False
        
        f = open("collections.txt", "r", encoding='utf-8')
        lines = f.readlines()
        f.close()
        
        return search_string_file(lines, ItemName[:ItemName.rfind("(")].replace('StatTrak™ ', ''))

    def fetchPrices(self) -> List[Item]:
        url = f'http://csgobackpack.net/api/GetItemsList/v2/?currency={self.currency}'
        r = None

        try:
            r = requests.get(url=url)
            r = r.json()['items_list']
        except Exception as e:
            print("cannot access resource")
            return

        out = []
        for x in r:
            i = r[x]

            def select_rarity(rarity: str) -> int:
                match rarity:
                    case 'Consumer Grade':
                        return Rarity.consumergrade
                    case 'Industrial Grade':
                        return Rarity.industrialgrade
                    case 'Mil-Spec Grade':
                        return Rarity.milspecgrade
                    case 'Restricted':
                        return Rarity.restricted
                    case 'Classified':
                        return Rarity.classified
                    case 'Covert':
                        return Rarity.covert
                    case _:
                        return Rarity.undefined
            
            if('Souvenir' in i['name']):
                continue

            if (not ('price' in i)):
                continue

            if (select_rarity(i['rarity']) == Rarity.undefined):
                continue

            if (not (i['type'] == 'Weapon')):
                continue

            if ((i['weapon_type'] == 'Knife')):
                continue

            out.append(Item(urllib.parse.unquote(i['name']), select_rarity(i['rarity']), self.findCollectionName(i['name']),Price(
                self.currency, next(iter(i['price'].values()))['average']), urllib.parse.unquote(i['name'])[urllib.parse.unquote(i['name']).rfind('('):]))
        return out
    
    def wearToInt(self, wear:str):
        if (wear=='(Factory New)'):
            return 0
        if (wear=='(Minimal Wear)'):
            return 1
        if (wear=='(Field-Tested)'):
            return 2
        if (wear=='(Well-Worn)'):
            return 3
        if (wear=='(Battle-Scarred)'):
            return 4
    
    def getItemsFromCollection(self, collection_name: str, stattrack: bool) -> List[Item]:
        out = []
        for x in self.prices:
            if x.Collection == collection_name and ('StatTrak™' in x.Name)==stattrack:
                out.append(x)
        return out
    
    def getPotenialTradeUpItems10x(self, item: Item) -> List[Item]:
        def uniqueItemInList(item: Item, list_to_check: List[Item]):
            for i in range(len(list_to_check)):
                x = list_to_check[i]
                if item.Name[:item.Name.rfind('(')] in x.Name:
                    return (x, i)
            return None
        
        out: List[Item] = []
        if not item.Rarity.value>=0 and item.Rarity.value<=4:
            return out
        
        items = self.getItemsFromCollection(item.Collection, 'StatTrak™' in item.Name)
        for x in items:
            if x.Rarity.value== item.Rarity.value+1:
                out.append(x)

        out2 = []

        for x in out:
            if uniqueItemInList(x, out2) == None:
                out2.append(x)

        for i in range(len(out)):
            x = out[i]
            n2 = uniqueItemInList(x, out2)

            if(self.wearToInt(item.Wear) - self.wearToInt(x.Wear) < self.wearToInt(item.Wear) - self.wearToInt(n2[0].Wear) and self.wearToInt(item.Wear) - self.wearToInt(x.Wear) > 0):
                out2[n2[1]] = x

        return out2
    
    def calculateAverageTradeupValue(self, item: Item):
        potential_items: List[Item] = self.getPotenialTradeUpItems10x(item)
        if (len(potential_items)==0):
            return 0
        avg = 0
        for x in potential_items:
            avg += x.Price.ammount
        avg = avg / len(potential_items)
        return avg
    
a = TradeUpCalculator()

f = open(f'trade-up-calculator-{datetime.now().strftime("%d-%m-%Y-%H%M%S")}.csv', "w", encoding='utf-8')

f.write(f'Item Name, Trade Up Cost ({a.currency}), Expected Value ({a.currency}), Expected Profit ({a.currency}), All Profit Outcomes ({a.currency})\n')
for x in a.prices:
    potential_items = a.getPotenialTradeUpItems10x(x)

    f.write(f'{x.Name}, {x.Price.ammount * 10}, {a.calculateAverageTradeupValue(x)}, {a.calculateAverageTradeupValue(x) - x.Price.ammount * 10}, ')
    for y in potential_items:
        f.write(f'{y.Name}:{y.Price.ammount} - ')
    f.write('\n')

f.close()