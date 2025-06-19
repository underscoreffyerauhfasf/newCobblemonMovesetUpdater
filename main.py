import re as regex
import os
import json

import full_dict as pkdict

import pokedex as dex

cobblemonDatapackFilepath = "./species"
exportFilepath = "./species-export"

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
        self.exportPokemonData(cobblemonDatapackFilepath,exportFilepath,self.national_pokedex)



    def get_baseform(self, formname):
        '''Takes a Pokemon form and finds the Pokemon that it belongs to, eg. `"slowbrogalar"` returning `"slowbro"`.'''
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
    
    def formatMoveset(self,moveset):
        final_moveset = []
        level_moveset = []

        for method in moveset:
            for move in moveset[method]:
                if method == 'level':
                    level_moveset.append(":".join(map(str, move)))
                else:
                    final_moveset.append(f"{method}:{move}")

        level_moveset.sort(key=lambda move: len(regex.sub(":.*","",move)))
        final_moveset.sort()

        final_moveset = level_moveset + final_moveset

        return final_moveset
    


    def exportPokemonData(self,import_directory,export_directory,dex_list):
        print("Exporting...\n\n")

        # loop through all directories within the passed master directory,
        for generation in os.listdir(import_directory):
            print(f"\n\n\n\n\n====={generation}=====\n\n")

            # then loop through the files in each directory,
            for openedFile in os.listdir(f"{import_directory}/{generation}"):
                pokemon_name = regex.sub(f"\\..*","",openedFile)

                print(f"\n\n==={pokemon_name.upper()}===")

                # open the given file currently being looped through,
                with open(f"{import_directory}/{generation}/{openedFile}") as f:
                    j = json.load(f)

                    # and set the pokemon's moveset to be the updated moveset from the pokedex
                    j['moves'] = self.formatMoveset(dex_list[pokemon_name].moveset)

                    # if the given pokemon has any forms, then there's still more work to do:
                    if dex_list[pokemon_name].forms != {}:
                        formes = dex_list[pokemon_name].forms

                        # loop through the forms the pokemon has;
                        for form in formes:
                            # get the suffix of the current form (eg. "slowbrogalar" returns "Galar", through "Slowbro-Galar")
                            formSuffix = regex.sub(".*-","",dex.SpeciesDataTable[form.name]['name'])
                            print(f"\t- {formSuffix}")

                            # if the given form doesn't have any moves at all, we dont have to care about it
                            if all(form.moveset[x] == None for x in form.moveset):
                                continue

                            # cobblemon doesn't care for totems, so if the given form is a totem, skip it
                            if formSuffix == "Totem":
                                continue

                            # otherwise, loop through the open json's forms and attempt to find a match
                            for jsonForm in j['forms']:
                                if jsonForm['name'] != formSuffix:
                                    continue
                                
                                # if a match is found, patch in the new moves!
                                jsonForm['moves'] = self.formatMoveset(form.moveset)



                    # at this point, operations on the given pokemon are finished. it's time to export:

                    # if the path to the export location does not already exist, make it
                    if not os.path.exists(f"{export_directory}/{generation}"):
                        os.makedirs(f"{export_directory}/{generation}")
                    # if not, check if there is already a file where the export is going to be created. if so, delete it
                    elif os.path.exists(f"{export_directory}/{generation}/{openedFile}"):
                        os.remove(f"{export_directory}/{generation}/{openedFile}")

                    # at last, write the file. we're done!
                    with open(f"{export_directory}/{generation}/{openedFile}", 'x') as exportedFile:
                        output = json.dumps(j,indent=2)

                        exportedFile.write(output)



importer = NewSuperCobblemonMovesetImporter()
