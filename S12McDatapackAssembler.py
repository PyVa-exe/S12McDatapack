import sys, os

xIdGenIndex = 0
def IdGen():
    global xIdGenIndex
    while True:
        yield xIdGenIndex
        xIdGenIndex += 1
xIdGen = IdGen()

def Error(msg):
    print(msg)
    sys.exit(0)


x16IntLimit = 65535
FuncId2Name = lambda x: "div{}".format(x)


#holds one function 'file'
class cFuncDiv:
    def __init__(self, xContent, xBaseName):
        self.xContent       = xContent
        #self.xTargetPath    = xTargetPath
        self.xId            = next(xIdGen)
        self.xName          = FuncId2Name(self.xId)
        self.xFileName      = self.xName + ".mcfunction"
        
        self.xBaseName = xBaseName
        
    def Translate(self, xLabMapper):
        return [self.InstTranslate(xContentIter, xLabMapper) for xContentIter in self.xContent]

    def InstTranslate(self, xInst, xLabMapper):
        #check if label is mapped
        if (xInst.xArg is not None) and not (xInst.xArg.isdigit()) and xInst.xArg not in xLabMapper:
            Error("Unmapped label: {}".format(xInst.xArg))
                
        xArgInt =              int(xInst.xArg) if (xInst.xArg is not None) and     (xInst.xArg.isdigit()) else 0
        xArgLab = xLabMapper[xInst.xArg].xName if (xInst.xArg is not None) and not (xInst.xArg.isdigit()) else ""
        
        try:
            return {
                "set" : "scoreboard players set Reg s1asm {}".format(xArgInt % x16IntLimit),
                "add" : "scoreboard players operation Acc s1asm += Reg s1asm\nscoreboard players operation Acc s1asm %= IntLimit s1asm",
                "sub" : "scoreboard players operation Acc s1asm -= Reg s1asm\nscoreboard players operation Acc s1asm %= IntLimit s1asm",
                "shg" : "scoreboard players operation Acc s1asm *= 2 s1asm  \nscoreboard players operation Acc s1asm %= IntLimit s1asm",
                "shs" : "scoreboard players operation Acc s1asm /= 2 s1asm  \nscoreboard players operation Acc s1asm %= IntLimit s1asm",
                
#lor none - Acc = Acc (logical or) Reg
#and none - Acc = Acc (logical and) Reg
#xor none - Acc = Acc (logical xor) Reg
#not none - Acc = Acc (logical not)
                
                "lda" : "execute store result score Acc s1asm run data get storage minecraft:s1asm Mem[{}]".format(xArgInt),
                "ldr" : "execute store result score Reg s1asm run data get storage minecraft:s1asm Mem[{}]".format(xArgInt),
                "sad" : "execute store result storage minecraft:s1asm Mem[{}] int 1 run scoreboard players get Acc s1asm".format(xArgInt),
                "srd" : "execute store result storage minecraft:s1asm Mem[{}] int 1 run scoreboard players get Reg s1asm".format(xArgInt),

                "lpa" : "execute store result score MemTarget s1asm run data get storage minecraft:s1asm Mem[{}]\n".format(xArgInt) +\
                        "execute unless score MemTarget s1asm matches 0 run function {}:memptrset".format(self.xBaseName) +\
                        "execute store result score Acc s1asm run data get storage minecraft:s1asm Mem[0]\n" +\
                        "execute unless score MemOffset s1asm matches 0 run function {}:memptrzero".format(self.xBaseName),

                "lpa" : "execute store result score MemTarget s1asm run data get storage minecraft:s1asm Mem[{}]\n".format(xArgInt) +\
                        "execute unless score MemTarget s1asm matches 0 run function {}:memptrset\n".format(self.xBaseName) +\
                        "execute store result score Reg s1asm run data get storage minecraft:s1asm Mem[0]\n" +\
                        "execute unless score MemOffset s1asm matches 0 run function {}:memptrzero".format(self.xBaseName),

                "sap" : "execute store result score MemTarget s1asm run data get storage minecraft:s1asm Mem[{}]\n".format(xArgInt) +\
                        "execute unless score MemTarget s1asm matches 0 run function {}:memptrset\n".format(self.xBaseName) +\
                        "execute store result storage minecraft:s1asm Mem[0] int 1 run scoreboard players get Acc s1asm\n" +\
                        "execute unless score MemOffset s1asm matches 0 run function {}:memptrzero".format(self.xBaseName),

                "srp" : "execute store result score MemTarget s1asm run data get storage minecraft:s1asm Mem[{}]\n".format(xArgInt) +\
                        "execute unless score MemTarget s1asm matches 0 run function {}:memptrset\n".format(self.xBaseName) +\
                        "execute store result storage minecraft:s1asm Mem[0] int 1 run scoreboard players get Reg s1asm\n" +\
                        "execute unless score MemOffset s1asm matches 0 run function {}:memptrzero".format(self.xBaseName),
                        
                "out" : 'tellraw @a {{"storage":"minecraft:s1asm","nbt":"Mem[{}]"}}'.format(xArgInt),
#inp attr - inputs  mem at attr

                "lab" : f"schedule function {self.xBaseName}:{FuncId2Name(self.xId + 1)} 1t".format() if xIdGenIndex > self.xId else "",
                "got" : f"schedule function {self.xBaseName}:{xArgLab} 1t".format(),
                "jm0" : f"execute if score Acc s1asm matches 0 run schedule function {self.xBaseName}:{xArgLab} 1t\n".format() +\
                        (f"execute unless score Acc s1asm matches 0 run schedule function {self.xBaseName}:{FuncId2Name(self.xId + 1)} 1t".format() if xIdGenIndex > self.xId else ""),
                "jma" : f"execute if score Acc s1asm = Reg s1asm run schedule function {self.xBaseName}:{xArgLab} 1t\n".format() +\
                        (f"execute unless score Acc s1asm = Reg s1asm run schedule function {self.xBaseName}:{FuncId2Name(self.xId + 1)} 1t".format() if xIdGenIndex > self.xId else ""),

#jmG attr - goto attr if Acc > Reg (jmG for jump great)
#jmL attr - goto atrr if Acc < Reg (jmL for jump less)

                "jms" : f"function {self.xBaseName}:{xArgLab}".format(),
                "ret" : "",


                
                "pha" : "data modify storage s1asm Stack append value 0\nexecute store result storage s1asm Stack[-1] int 1 run scoreboard players get Acc s1asm", 
                "pla" : "execute store result score Acc s1asm run data get storage s1asm Stack[-1]\ndata remove storage s1asm Stack[-1]",


                "brk" : "",
                "clr" : "scoreboard players set Acc s1asm 0\nscoreboard players set Reg s1asm 0",

                "putstr" : f"function {self.xBaseName}:putstr".format(),
                
            }[xInst.xOp.lower()]

        except KeyError:
           Error(f"Invaild instruction: '{xInst.xOp.lower()}'".format())



    
    def __str__(self):
        return "{}\t{}".format(self.xId, [str(x) for x in self.xContent])
    
class cInst:
    def __init__(self, *xTerms):
        (self.xOp, self.xArg) = map(lambda x: x if x is None else x.strip(" "), xTerms + ((None, ) if len(xTerms) < 2 else ()))
        
    def __str__(self):
        return "{} {}".format(self.xOp, self.xArg)

def Assemble(xSourcePath, xTargetPath):
    with open(xSourcePath, "r") as xFileHandle:
        xFile = xFileHandle.read()

    xTargetPathLocal = os.path.abspath(xTargetPath)
    xTargetPathAbs = os.path.join(xTargetPathLocal, "functions")
    xBaseName = os.path.basename(xTargetPathLocal)
    xInstList = [cInst(*x.split()) for x in xFile.split("\n") if len(x.strip()) > 0 and x.strip()[0] != '"']

    if not os.path.exists(xTargetPathAbs): os.mkdir(xTargetPathAbs)


    #write starting function
    with open(os.path.join(xTargetPathAbs, "start.mcfunction"), "w") as xFileHandle:
        xFileHandle.write(f"""
scoreboard objectives add s1asm dummy
scoreboard players set Acc s1asm 0
scoreboard players set Reg s1asm 0

scoreboard players set 2 s1asm 2
scoreboard players set IntLimit s1asm {x16IntLimit}

scoreboard players set MemOffset s1asm 0
scoreboard players set MemTarget s1asm 0

data modify storage minecraft:s1asm Mem set value {str([0] * x16IntLimit)}
data modify storage minecraft:s1asm Stack set value []
data modify storage minecraft:s1asm StdOut set value []
schedule function {xBaseName}:div0 1t
        """.format())

    #dynamic memory reading and writing (aka pointers)

    #WARING THIS *WILL* MODIFY THE MAIN MEMORY ARRAY
    #this function moves the MemOffset to the value of MemTarget
    with open(os.path.join(xTargetPathAbs, "memptrset.mcfunction"), "w") as xFileHandle:
        xFileHandle.write(f"""
scoreboard players add MemOffset s1asm 1
data modify storage minecraft:s1asm Mem append from storage s1asm Mem[0]
data remove storage minecraft:s1asm Mem[0]
execute unless score MemTarget s1asm = MemOffset s1asm run function {xBaseName}:memptrset
        """.format())
        
    #this function moves the MemOffset to 0
    with open(os.path.join(xTargetPathAbs, "memptrzero.mcfunction"), "w") as xFileHandle:
        xFileHandle.write(f"""
scoreboard players remove MemOffset s1asm 1
data modify storage minecraft:s1asm Mem prepend from storage s1asm Mem[-1]
data remove storage minecraft:s1asm Mem[-1]
execute unless score MemOffset s1asm matches 0 run function {xBaseName}:memptrzero
        """.format())

    #outputs *arg as ascii
    with open(os.path.join(xTargetPathAbs, "putstr.mcfunction"), "w") as xFileHandle:
        xFileHandle.write("""
execute if score Acc s1asm matches 10 run tellraw @a {"nbt":"StdOut", "storage":"s1asm"}
execute if score Acc s1asm matches 10 run data modify storage minecraft:s1asm StdOut set value []

execute if score Acc s1asm matches 0 run data modify storage minecraft:s1asm StdOut append value "" 
execute if score Acc s1asm matches 1 run data modify storage minecraft:s1asm StdOut append value ""
execute if score Acc s1asm matches 2 run data modify storage minecraft:s1asm StdOut append value ""                  
execute if score Acc s1asm matches 3 run data modify storage minecraft:s1asm StdOut append value ""                  
execute if score Acc s1asm matches 4 run data modify storage minecraft:s1asm StdOut append value ""                  
execute if score Acc s1asm matches 5 run data modify storage minecraft:s1asm StdOut append value ""                  
execute if score Acc s1asm matches 6 run data modify storage minecraft:s1asm StdOut append value ""                  
execute if score Acc s1asm matches 7 run data modify storage minecraft:s1asm StdOut append value ""                   
execute if score Acc s1asm matches 8 run data remove storage minecraft:s1asm StdOut[-1]                
execute if score Acc s1asm matches 9 run data modify storage minecraft:s1asm StdOut append value "    "                
execute if score Acc s1asm matches 11 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 12 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 13 run data modify storage minecraft:s1asm StdOut append value ""
execute if score Acc s1asm matches 14 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 15 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 16 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 17 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 18 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 19 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 20 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 21 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 22 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 23 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 24 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 25 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 26 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 27 run data modify storage minecraft:s1asm StdOut append value ""                   
execute if score Acc s1asm matches 28 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 29 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 30 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 31 run data modify storage minecraft:s1asm StdOut append value ""                 
execute if score Acc s1asm matches 32 run data modify storage minecraft:s1asm StdOut append value " "                 
execute if score Acc s1asm matches 33 run data modify storage minecraft:s1asm StdOut append value "!"                 
execute if score Acc s1asm matches 34 run data modify storage minecraft:s1asm StdOut append value "\""                 
execute if score Acc s1asm matches 35 run data modify storage minecraft:s1asm StdOut append value "#"                 
execute if score Acc s1asm matches 36 run data modify storage minecraft:s1asm StdOut append value "$"                 
execute if score Acc s1asm matches 37 run data modify storage minecraft:s1asm StdOut append value "%"                 
execute if score Acc s1asm matches 38 run data modify storage minecraft:s1asm StdOut append value "&"                 
execute if score Acc s1asm matches 39 run data modify storage minecraft:s1asm StdOut append value "'"                 
execute if score Acc s1asm matches 40 run data modify storage minecraft:s1asm StdOut append value "("                 
execute if score Acc s1asm matches 41 run data modify storage minecraft:s1asm StdOut append value ")"                 
execute if score Acc s1asm matches 42 run data modify storage minecraft:s1asm StdOut append value "*"                 
execute if score Acc s1asm matches 43 run data modify storage minecraft:s1asm StdOut append value "+"                 
execute if score Acc s1asm matches 44 run data modify storage minecraft:s1asm StdOut append value ","                 
execute if score Acc s1asm matches 45 run data modify storage minecraft:s1asm StdOut append value "-"                 
execute if score Acc s1asm matches 46 run data modify storage minecraft:s1asm StdOut append value "."                 
execute if score Acc s1asm matches 47 run data modify storage minecraft:s1asm StdOut append value "/"                 
execute if score Acc s1asm matches 48 run data modify storage minecraft:s1asm StdOut append value "0"                 
execute if score Acc s1asm matches 49 run data modify storage minecraft:s1asm StdOut append value "1"                 
execute if score Acc s1asm matches 50 run data modify storage minecraft:s1asm StdOut append value "2"                 
execute if score Acc s1asm matches 51 run data modify storage minecraft:s1asm StdOut append value "3"                 
execute if score Acc s1asm matches 52 run data modify storage minecraft:s1asm StdOut append value "4"                 
execute if score Acc s1asm matches 53 run data modify storage minecraft:s1asm StdOut append value "5"                 
execute if score Acc s1asm matches 54 run data modify storage minecraft:s1asm StdOut append value "6"                 
execute if score Acc s1asm matches 55 run data modify storage minecraft:s1asm StdOut append value "7"                 
execute if score Acc s1asm matches 56 run data modify storage minecraft:s1asm StdOut append value "8"                 
execute if score Acc s1asm matches 57 run data modify storage minecraft:s1asm StdOut append value "9"                 
execute if score Acc s1asm matches 58 run data modify storage minecraft:s1asm StdOut append value ":"                 
execute if score Acc s1asm matches 59 run data modify storage minecraft:s1asm StdOut append value ";"                 
execute if score Acc s1asm matches 60 run data modify storage minecraft:s1asm StdOut append value "<"                 
execute if score Acc s1asm matches 61 run data modify storage minecraft:s1asm StdOut append value "="                 
execute if score Acc s1asm matches 62 run data modify storage minecraft:s1asm StdOut append value ">"                 
execute if score Acc s1asm matches 63 run data modify storage minecraft:s1asm StdOut append value "?"                 
execute if score Acc s1asm matches 64 run data modify storage minecraft:s1asm StdOut append value "@"                 
execute if score Acc s1asm matches 65 run data modify storage minecraft:s1asm StdOut append value "A"                 
execute if score Acc s1asm matches 66 run data modify storage minecraft:s1asm StdOut append value "B"                 
execute if score Acc s1asm matches 67 run data modify storage minecraft:s1asm StdOut append value "C"                 
execute if score Acc s1asm matches 68 run data modify storage minecraft:s1asm StdOut append value "D"                 
execute if score Acc s1asm matches 69 run data modify storage minecraft:s1asm StdOut append value "E"                 
execute if score Acc s1asm matches 70 run data modify storage minecraft:s1asm StdOut append value "F"                 
execute if score Acc s1asm matches 71 run data modify storage minecraft:s1asm StdOut append value "G"                 
execute if score Acc s1asm matches 72 run data modify storage minecraft:s1asm StdOut append value "H"                 
execute if score Acc s1asm matches 73 run data modify storage minecraft:s1asm StdOut append value "I"                 
execute if score Acc s1asm matches 74 run data modify storage minecraft:s1asm StdOut append value "J"                 
execute if score Acc s1asm matches 75 run data modify storage minecraft:s1asm StdOut append value "K"                 
execute if score Acc s1asm matches 76 run data modify storage minecraft:s1asm StdOut append value "L"                 
execute if score Acc s1asm matches 77 run data modify storage minecraft:s1asm StdOut append value "M"                 
execute if score Acc s1asm matches 78 run data modify storage minecraft:s1asm StdOut append value "N"                 
execute if score Acc s1asm matches 79 run data modify storage minecraft:s1asm StdOut append value "O"                 
execute if score Acc s1asm matches 80 run data modify storage minecraft:s1asm StdOut append value "P"                 
execute if score Acc s1asm matches 81 run data modify storage minecraft:s1asm StdOut append value "Q"                 
execute if score Acc s1asm matches 82 run data modify storage minecraft:s1asm StdOut append value "R"                 
execute if score Acc s1asm matches 83 run data modify storage minecraft:s1asm StdOut append value "S"                 
execute if score Acc s1asm matches 84 run data modify storage minecraft:s1asm StdOut append value "T"                 
execute if score Acc s1asm matches 85 run data modify storage minecraft:s1asm StdOut append value "U"                 
execute if score Acc s1asm matches 86 run data modify storage minecraft:s1asm StdOut append value "V"                 
execute if score Acc s1asm matches 87 run data modify storage minecraft:s1asm StdOut append value "W"                 
execute if score Acc s1asm matches 88 run data modify storage minecraft:s1asm StdOut append value "X"                 
execute if score Acc s1asm matches 89 run data modify storage minecraft:s1asm StdOut append value "Y"                 
execute if score Acc s1asm matches 90 run data modify storage minecraft:s1asm StdOut append value "Z"                 
execute if score Acc s1asm matches 91 run data modify storage minecraft:s1asm StdOut append value "["                 
execute if score Acc s1asm matches 92 run data modify storage minecraft:s1asm StdOut append value "\"                 
execute if score Acc s1asm matches 93 run data modify storage minecraft:s1asm StdOut append value "]"                 
execute if score Acc s1asm matches 94 run data modify storage minecraft:s1asm StdOut append value "^"                 
execute if score Acc s1asm matches 95 run data modify storage minecraft:s1asm StdOut append value "_"                 
execute if score Acc s1asm matches 96 run data modify storage minecraft:s1asm StdOut append value "`"                 
execute if score Acc s1asm matches 97 run data modify storage minecraft:s1asm StdOut append value "a"                 
execute if score Acc s1asm matches 98 run data modify storage minecraft:s1asm StdOut append value "b"                 
execute if score Acc s1asm matches 99 run data modify storage minecraft:s1asm StdOut append value "c"                 
execute if score Acc s1asm matches 100 run data modify storage minecraft:s1asm StdOut append value "d"                
execute if score Acc s1asm matches 101 run data modify storage minecraft:s1asm StdOut append value "e"                
execute if score Acc s1asm matches 102 run data modify storage minecraft:s1asm StdOut append value "f"                
execute if score Acc s1asm matches 103 run data modify storage minecraft:s1asm StdOut append value "g"                
execute if score Acc s1asm matches 104 run data modify storage minecraft:s1asm StdOut append value "h"                
execute if score Acc s1asm matches 105 run data modify storage minecraft:s1asm StdOut append value "i"                
execute if score Acc s1asm matches 106 run data modify storage minecraft:s1asm StdOut append value "j"                
execute if score Acc s1asm matches 107 run data modify storage minecraft:s1asm StdOut append value "k"                
execute if score Acc s1asm matches 108 run data modify storage minecraft:s1asm StdOut append value "l"                
execute if score Acc s1asm matches 109 run data modify storage minecraft:s1asm StdOut append value "m"                
execute if score Acc s1asm matches 110 run data modify storage minecraft:s1asm StdOut append value "n"                
execute if score Acc s1asm matches 111 run data modify storage minecraft:s1asm StdOut append value "o"                
execute if score Acc s1asm matches 112 run data modify storage minecraft:s1asm StdOut append value "p"                
execute if score Acc s1asm matches 113 run data modify storage minecraft:s1asm StdOut append value "q"                
execute if score Acc s1asm matches 114 run data modify storage minecraft:s1asm StdOut append value "r"                
execute if score Acc s1asm matches 115 run data modify storage minecraft:s1asm StdOut append value "s"                
execute if score Acc s1asm matches 116 run data modify storage minecraft:s1asm StdOut append value "t"                
execute if score Acc s1asm matches 117 run data modify storage minecraft:s1asm StdOut append value "u"                
execute if score Acc s1asm matches 118 run data modify storage minecraft:s1asm StdOut append value "v"                
execute if score Acc s1asm matches 119 run data modify storage minecraft:s1asm StdOut append value "w"                
execute if score Acc s1asm matches 120 run data modify storage minecraft:s1asm StdOut append value "x"                
execute if score Acc s1asm matches 121 run data modify storage minecraft:s1asm StdOut append value "y"                
execute if score Acc s1asm matches 122 run data modify storage minecraft:s1asm StdOut append value "z"                
execute if score Acc s1asm matches 123 run data modify storage minecraft:s1asm StdOut append value "{"                
execute if score Acc s1asm matches 124 run data modify storage minecraft:s1asm StdOut append value "|"                
execute if score Acc s1asm matches 125 run data modify storage minecraft:s1asm StdOut append value "}"                
execute if score Acc s1asm matches 126 run data modify storage minecraft:s1asm StdOut append value "~"
        """)




    
    #this is probably the worst parser i've ever written
    #don't ask how it works, cuz' i don't know either
    #ALSO; THIS PARSER !!!WILL!!! BREAK IF YOU GIVE IT TWO LABELS IN SEQUENCE; THE 2ND WILL OVERRIDE THE 1ST
    xInstTempBuffer = []
    xDivBuffer      = []
    xLabMapper      = {} #mappes label name to cFuncDiv instance
    xCurrentLabelSecName = None
    for xIndex, xInst in enumerate(xInstList):
        xInstTempBuffer += [xInst]
        
        #check for inst to cut at or the end
        if xInst.xOp in ["brk", "ret", "got", "jm0", "jmA", "jmL", "jmG", "lab"] or len(xInstList) == xIndex + 1:
            xFuncDiv = cFuncDiv(xInstTempBuffer, xBaseName)
            xDivBuffer += [xFuncDiv]
            xInstTempBuffer = []
            
            #if the current section is reachable by a labels, map that label the the xFuncDiv
            #so it can referenced later, when generating the output
            if xCurrentLabelSecName is not None:
                xLabMapper[xCurrentLabelSecName] = xFuncDiv
            
            #update the section tracker if a new label is being scanned over
            xCurrentLabelSecName = xInst.xArg if xInst.xOp == "lab" else None
    
    
    
     
    for xDiv in xDivBuffer:
        with open(os.path.join(xTargetPathAbs, xDiv.xFileName), "w") as xFileHandle:
            xFileHandle.write("\n".join(xDiv.Translate(xLabMapper)))
        
    
if __name__ == '__main__':
    if "--help" in sys.argv:
        print("""
--help    print help
--input   input file
--output  output file
        """)
        sys.exit(0)
    
    try:
        xInputPath  = sys.argv[sys.argv.index("--input" ) + 1]
        xOutputPath = sys.argv[sys.argv.index("--output") + 1]

    except ValueError:
        Error("Invaild call args")
        
    if os.path.isfile(xOutputPath):
        Error("Output path must point to directory")
        
    Assemble(xInputPath, xOutputPath)
    