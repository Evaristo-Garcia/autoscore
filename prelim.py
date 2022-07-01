# interact with json
import json

class Team:
    name = 'none'

def readJSON(name):
    with open(name) as file:
        p = json.load(file)
        for key, val in p.items():
            print(key, "<>", val)
        print(p["56"])
        # print(json.load(file))
        print(file.read())

    # with open(name, 'w') as file:
    #     json.dump({"105": "UofM"}, file)

if __name__ == '__prelim__':
    with open('Teams.json') as new:
        z = json.load(new)
        print(z["105"][0])
        print(z["56"][1])

    readJSON('Teams.json')

