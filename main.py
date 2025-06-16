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
    def __init__(self,name,dex_number):
        self.name = name
        self.pokedex_number = dex_number
        self.forms = []
        self.moveset = {}


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
            newmoveset = list(set(self.moveset[method] + basemoveset[method])).sort()
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
        searchingname = dex.SpeciesDataTable[formname]["baseSpecies"]
        for i in dex.SpeciesDataTable.keys():
            if dex.SpeciesDataTable[i]["name"] == searchingname:
                return i


    def findPokemonData(self):
        for i in dex.SpeciesDataTable.keys():
            if i in pkdict.colonThree.keys():
                newmon = Pokemon(i, dex.SpeciesDataTable[i]["num"])
                if "learnset" in pkdict.colonThree[i].keys():
                    #form has a moveset
                    newmon.moveset = newmon.build_moveset(pkdict.colonThree[i]["learnset"])
                if "baseSpecies" in dex.SpeciesDataTable[i].keys():
                    #altform
                    baseform = self.get_baseform(i)
                    newmon.moveset = newmon.mergeFormMoveset(self.national_pokedex[baseform].moveset)
                    self.national_pokedex[baseform].forms.append(newmon)
                else: 
                    #baseform
                    self.national_pokedex[i] = newmon
                print(i)
                #print(f"\n\n\n==={i.upper()}===\n")
                #print(json.dumps(newmon.moveset,indent=4,sort_keys=True))
        for i in self.national_pokedex.keys():
            print(f"\n\n\n==={i.upper()}===\n")
            print(self.national_pokedex[i])

importer = NewSuperCobblemonMovesetImporter()
