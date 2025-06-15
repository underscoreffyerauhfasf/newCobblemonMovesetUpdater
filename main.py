import re as regex
import pokemon_dict as pkdict

listFile = "output.txt"

learnsetoptions = {
    'tm':       {'level':True,  'tm':True,  'tutor':True,   'egg':True,     'event':True},
    'tutor':    {'level':False, 'tm':False, 'tutor':True,   'egg':False,    'event':False},
    'egg':      {'level':False, 'tm':False, 'tutor':False,  'egg':True,     'event':False},
}

showdowntoname = {
    'L': 'level',
    'M': 'tm',
    'T': 'tutor',
    'E': 'egg',
    'S': 'event'
}

mingen = 3
vcmoves = ['nightmare']
allvcmoves = False
# E is egg
# M is tm/tr
# T is tutor 
# L(number) is level
# S(number) is event



class Pokemon:
    def __init__(self,name,dex_number,formes,showdownset):
        self.name = name
        self.pokedex_number = dex_number
        self.forms = formes
        if showdownset == {}:
            self.moveset = {}
        else:
            self.moveset = self.build_moveset(showdownset)


    def build_moveset(self,showdownset):
        finalmoveset = {
            'level': [],
            'tm': [],
            'tutor': [],
            'egg': [],
            'form_change': []
        }

        for move in showdownset.keys():
            levelfound = False

            for method in showdownset[move]:
                letterpos = regex.search("[A-Z]", method).span()[0]
                gen = int(method[:letterpos])
                param = method[letterpos+1:]

                #add to levelset if applicable
                if method[letterpos] == 'V' and (move in vcmoves or allvcmoves):
                    method = method[:letterpos] + 'M'
                if method[letterpos] == 'D':
                    method = method[:letterpos] + 'S'
                if method[letterpos] == 'R' and (move == 'volttackle' or self.name == 'shedinja'):
                    method = method[:letterpos] + 'M'
                if method[letterpos] == 'R' and move not in finalmoveset['form_change'] and (gen >= mingen):
                    finalmoveset['form_change'].append(move)
                elif method[letterpos] not in ['V', 'R'] and (gen >= mingen):
                    if method[letterpos] == 'L' and not levelfound:
                        finalmoveset['level'].append((int(param),move))
                        levelfound = True        

                    for cobblemonmethod in (learnsetoptions.keys() - ['form_change']):
                        if learnsetoptions[cobblemonmethod][showdowntoname[method[letterpos]]] and move not in finalmoveset[cobblemonmethod]:
                            finalmoveset[cobblemonmethod].append(move)

        for method in finalmoveset.keys():
            finalmoveset[method].sort()

        return finalmoveset


class NewSuperCobblemonMovesetImporter:
    def __init__(self):
        self.national_pokedex = {}

        self.findPokemonData()
    
    def findPokemonData(self):
        for i in pkdict.colonThree.keys():
            if "learnset" in pkdict.colonThree[i].keys():
                currentlearnset = pkdict.colonThree[i]["learnset"]
            else:
                currentlearnset = {}
            thismon = Pokemon(i, 0, [], currentlearnset)
            print(i)
            print(thismon.moveset)
            print("\n\n")
            pass

importer = NewSuperCobblemonMovesetImporter()
