import re as regex
import pokemon_dict as pkdict

listFile = "output.txt"



# E is egg
# M is tm/tr
# T is tutor 
# L(number) is level
# S(number) is event



class Pokemon:
    def __init__(self,name,dex_number,formes,moveset):
        self.name = name
        self.pokedex_number = dex_number
        self.forms = formes
        self.moveset = moveset

class NewSuperCobblemonMovesetImporter:
    def __init__(self):
        self.national_pokedex = {}

        self.findPokemonData()
    
    def findPokemonData(self):
        for i in pkdict.colonThree.keys():
            print(i)
            print("\n\n")
            pass

importer = NewSuperCobblemonMovesetImporter()
