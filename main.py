import re as regex

targetFile = "test.txt"
listFile = "output.txt"



def findListFromLine(line):
    pass

def findStringFromLine(line):
    return regex.sub("[^\\w\\d]","",line)


# E is egg
# M is tm/tr
# T is tutor 
# L(number) is level
# S(number) is event


class Pokemon:
    def __init__(self,name,dex_number,forms,moveset):
        self.name = name
        self.pokedex_number = dex_number
        self.moveset = moveset

class NewSuperCobblemonMovesetImporter:
    def __init__(self,file):
        self.file = file
        self.national_pokedex = {}

        self.findPokemonData(self.file)
    
    def findPokemonData(self,file):
        currentPokemon = ""

        with open(file) as openedFile:
            for i in openedFile:
                # count the number of indentations on the current line
                # (this is very likely not the best way to do this but idc)
                match i.count("\t"):
                    # it's a pokemon, so find which one it is and store it
                    # (but don't add it to the national dex yet!)
                    case 1:
                        currentPokemon = findStringFromLine(i)

                        if currentPokemon == "":
                            continue

                        print(f"Current Pokemon: '{currentPokemon}'")

                    # it's a data container
                    case 2:
                        pass

                    # it's some form of data
                    case 3:
                        pass
            # print(openFile.read())

importer = NewSuperCobblemonMovesetImporter(targetFile)
