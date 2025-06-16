import re as regex
import json

import full_dict as pkdict

import pokedex as dex

listFile = "output.txt"

# move will be added to [key] if it is learned via [value]
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
    '''A class dedicated to Pokemon objects, storing all relevant information within itself.'''
    def __init__(self,name,dex_number,preevo,evos):
        self.name = name
        self.pokedex_number = dex_number
        self.forms = []
        self.moveset = {}
        self.preevo = preevo
        self.evos = evos


    def build_moveset(self,showdownset):
        '''Compiles passed data in `showdownset` into a Pythonic dictionary and returns it.'''
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
            levelfoundingen = 0

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
                    # if the move is levelup (L) AND this is the latest generation this move has been found in, set level as found and register the method
                    # (this is to prioritize latest levelup setting-- if a move is learned at a certain level in newer gens, older ones won't override it!)
                    if method[letterpos] == 'L' and (gen >= levelfoundingen):
                        finalmoveset['level'].append((int(param),move))
                        levelfoundingen = gen

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
    
    def mergeFormMoveset(self, basemoveset):
        if self.moveset == {}:
            return {}
        if self.moveset['level'] != []:
            return self.moveset
        newmoveset = {}
        for method in self.moveset.keys():
            newmoveset[method] = list(set(self.moveset[method] + basemoveset[method])).sort()
        return newmoveset
    
    def mergePreevoMoveset(self, preevomoveset):
        newmoveset = self.moveset
        for method in ['tm', 'tutor', 'egg']:
            newmoveset[method] = list(set(self.moveset[method] + preevomoveset[method]))
            newmoveset[method].sort()
        return newmoveset
    
    def __str__(self):
        outputstr = "NAME: %s\tNUM: %d\nMOVESET: " % (self.name, self.pokedex_number)
        outputstr += json.dumps(self.moveset,indent=4,sort_keys=True) + "\n"
        if self.forms != []:
            outputstr += "\nFORMS:\n"
            for form in self.forms:
                outputstr += "--------------------------------\n"
                outputstr += str(form) + "\n"
            outputstr += "--------------------------------\n"
        return outputstr


class NewSuperCobblemonMovesetImporter:
    def __init__(self):
        self.national_pokedex = {}

        self.findPokemonData()
    
    def get_baseform(self, formname):
        '''Takes a real name (eg. `"Slowbro"`) and finds the Pokemon that it belongs to.'''
        searchingname = dex.SpeciesDataTable[formname]["baseSpecies"]
        for i in dex.SpeciesDataTable.keys():
            if dex.SpeciesDataTable[i]["name"] == searchingname:
                return i
            
    def getIdFromProperName(self, name):
        for i in dex.SpeciesDataTable.keys():
            if dex.SpeciesDataTable[i]["name"] == name:
                return i
    
    def getPokemonById(self, id):
        if id in self.national_pokedex.keys():
            return self.national_pokedex[id]
        else:
            base = self.get_baseform(id)
            for form in self.national_pokedex[base].forms:
                if form.name == id:
                    return form
            
    def carryMovesForward(self,pokemonid):
        mon = self.getPokemonById(pokemonid)
        for evo in mon.evos:
            currentevo = self.getPokemonById(evo)
            if currentevo != None:
                currentevo.moveset = currentevo.mergePreevoMoveset(mon.moveset)
                self.carryMovesForward(evo)
            

    def findPokemonData(self):
        for i in dex.SpeciesDataTable.keys():
            if i in pkdict.colonThree.keys():
                currentmondex = dex.SpeciesDataTable[i]
                if "prevo" in currentmondex.keys():
                    preevo = self.getIdFromProperName(currentmondex["prevo"])
                else:
                    preevo = ""
                evos = []
                if "evos" in currentmondex.keys():
                    for evo in currentmondex["evos"]:
                        evos.append(self.getIdFromProperName(evo))
                newmon = Pokemon(i, currentmondex["num"], preevo, evos)

                if "learnset" in pkdict.colonThree[i].keys():
                    # this form has a moveset
                    newmon.moveset = newmon.build_moveset(pkdict.colonThree[i]["learnset"])

                if "baseSpecies" in currentmondex.keys():
                    # this pokemon is an altform
                    baseform = self.get_baseform(i)
                    newmon.moveset = newmon.mergeFormMoveset(self.national_pokedex[baseform].moveset)
                    self.national_pokedex[baseform].forms.append(newmon)
                else: 
                    #baseform
                    self.national_pokedex[i] = newmon

                #print(i)
                
        for i in dex.SpeciesDataTable.keys():
            if i in pkdict.colonThree.keys() and self.getPokemonById(i).preevo == "":
                self.carryMovesForward(i)

        for i in self.national_pokedex.keys():
            print(f"\n\n\n==={i.upper()}===\n")
            print(self.national_pokedex[i])

importer = NewSuperCobblemonMovesetImporter()
