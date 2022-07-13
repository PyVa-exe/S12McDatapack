import sys

def IdGen():
    x = 0
    while True:
        yield x
        x += 1
xIdGen = IdGen()

#holds one function 'file'
class cFuncDiv:
    def __init__(self, xContent):
        self.xContent   = xContent
        self.xId        = next(xIdGen)
    
    def __str__(self):
        return "{}\t{}".format(self.xId, [str(x) for x in self.xContent])
    
class cInst:
    def __init__(self, *xTerms):
        (self.xOp, self.xArg) = xTerms + ((None, ) if len(xTerms) < 2 else ())
        
    def __str__(self):
        return "{} {}".format(self.xOp, self.xArg)

def Assemble(xFile):
    xInstList = [cInst(*x.split()) for x in xFile.split("\n") if len(x.strip()) > 0 and x.strip()[0] != '"']
    
    
    #this is probably the worst parser i've ever written
    #don't ask how it works, cuz' i don't know either
    xInstTempBuffer = []
    xDivBuffer      = []
    xLabMapper      = {} #mappes label name to cFuncDiv instance
    xCurrentLabelSecName = None
    for xIndex, xInst in enumerate(xInstList):
        #append to buffer (lab insts are cut, because they have no more meaning after being parsed)
        if xInst.xOp != "lab": 
            xInstTempBuffer += [xInst]
        
        #check for inst to cut at or the end
        if xInst.xOp in ["got", "jm0", "jmA", "jmL", "jmG", "lab"] or len(xInstList) == xIndex + 1:
            xFuncDiv = cFuncDiv(xInstTempBuffer)
            xDivBuffer += [xFuncDiv]
            xInstTempBuffer = []
            
            #if the current section is reachable by a labels, map that label the the xFuncDiv
            #so it can referenced later, when generating the output
            if xCurrentLabelSecName is not None:
                xLabMapper[xCurrentLabelSecName] = xFuncDiv
            
            #update the section tracker if a new label is being scanned over
            xCurrentLabelSecName = xInst.xArg if xInst.xOp == "lab" else None
                
    for xDiv in xDivBuffer:
        print(xDiv)
    print(xLabMapper)
        
    
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
        
    
    with open(str(xInputPath), "r") as xFileHandle:
        Assemble(xFileHandle.read())
    