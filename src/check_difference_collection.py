# just to check if every skin is included in collections.txt

from main import TradeUpCalculator

def search_string_file(lines, string):
    for x in lines:
        if string in x:
            return True
        
    print(string)
    return False

items = TradeUpCalculator()

not_found = []

f = open("collections.txt", "r", encoding='utf-8')
lines = f.readlines()
f.close()

print(len(lines))

for x in items.prices:
    if(not search_string_file(lines, x.Name[:x.Name.find("(")].replace('StatTrak™ ', ''))):
        not_found.append(x)

print(not_found)