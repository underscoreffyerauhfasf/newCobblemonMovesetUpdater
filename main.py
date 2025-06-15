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
vcwhitelist = ['nightmare']
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

        self.moveset = self.build_moveset(showdownset)


    def build_moveset(self,showdownset):
        # if the passed dict is empty, then doing anything is useless. immediately return
        if showdownset == {}:
            return {}

        # otherwise, set up the list to be eventually returned
        finalmoveset = {
            'level': [],
            'tm': [],
            'tutor': [],
            'egg': [],
            'form_change': []
        }

        # loop through every move in passed list showdownset
        for move in showdownset.keys():
            levelfound = False

            # ...then loop through every learn method in the current move
            for method in showdownset[move]:
                letterpos = regex.search("[A-Z]", method).span()[0]

                gen = int(method[:letterpos])
                param = method[letterpos+1:]

                # do a bit of cleanup before registering a method, if applicable:

                # if the move is from virtual console (V) AND
                # either virtual console moves are enabled OR that specific move is whitelisted,
                # interpret as TM
                if method[letterpos] == 'V' and (allvcmoves or (move in vcwhitelist)):
                    method = method[:letterpos] + 'M'

                # if the move is from the dream world (D), interpret it as from an event
                if method[letterpos] == 'D':
                    method = method[:letterpos] + 'E'

                # if the move is special-case (R) AND it is either volt tackle or from shedinja, interpret as TM. fuck you shedinja
                if method[letterpos] == 'R' and (move == 'volttackle' or self.name == 'shedinja'):
                    method = method[:letterpos] + 'M'

                # if the move is special-case (R) AND the move isn't already accounted AND this is a gen we care about, register the method
                if method[letterpos] == 'R' and move not in finalmoveset['form_change'] and (gen >= mingen):
                    finalmoveset['form_change'].append(move)

                # otherwise if the move is NOT virtual console or special-case AND this is a gen we care about, proceed to method registration
                elif method[letterpos] not in ['V', 'R'] and (gen >= mingen):
                    # if the move is levelup (L) AND the level has not yet been found, set level as found and register the method
                    # (this is to prioritize latest levelup setting-- if a move is learned at a certain level in newer gens, older ones won't override it!)
                    if method[letterpos] == 'L' and not levelfound:
                        finalmoveset['level'].append((int(param),move))
                        levelfound = True        

                    # loop through the configured options;
                    for cobblemonmethod in (learnsetoptions.keys() - ['form_change']):
                        # if the current method is configured to be registered AND the current method has not already been registered, register it
                        if learnsetoptions[cobblemonmethod][showdowntoname[method[letterpos]]] and (move not in finalmoveset[cobblemonmethod]):
                            finalmoveset[cobblemonmethod].append(move)

        # finally, sort...
        for method in finalmoveset.keys():
            finalmoveset[method].sort()

        # ...and we're done!
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

            print("\n",i)
            print(thismon.moveset,"\n")

importer = NewSuperCobblemonMovesetImporter()
