import os
import sys
from copy import deepcopy
from itertools import combinations
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from carneades.caes import CAES, ArgumentSet, ProofStandard, Audience 
from carneades.reader import Reader

class Dialogue(object):
    def __init__(self, textFile):
        file = open(textFile,"r")
        readerObject = Reader()
        readerObject.load(file)
        self.commandStack = readerObject.getCommandStack() #Dictionary of different types of vars
    
    def burdenOfProofLocation(self, burdenOfProof, caes):
        if burdenOfProof == "Defense" and caes.acceptable(self.argumentsDefense.values()[0].conclusion):
            return "Prosecution"
        elif burdenOfProof == "Prosecution" and caes.acceptable(self.argumentsProsecution.values()[0].conclusion)
            return "Defense"
        else:
            return burdenOfProof

    def findBestArgument(self, availArgs, argset, burdenOfProof, depth) :
        argsetSearch = copy.deepcopy(argset) 
        if (len(availArgs.items()) >= depth):
            pass
        else:
            depth = len(availArgs.items())

        if burdenOfProof == "Defense":
            conclusion = self.argumentsDefense.values()[0].conclusion
        else:
            conclusion = self.argumentsProsecution.values()[0].conclusion

        combinations = combinations(availArgs.values(),depth)
        for c in combinations:
            usedArguments = []
            for arg in combination:
                argsetSearch.add_argument(arg)
                usedArguments.append(arg)

                caesSearch = CAES(argsetSearch,self.audience,self.ps)

                acceptable = caesSearch.acceptable(conclusion)
                if(acceptable):
                    print('Side added argument(s):')
                    for argument in added_arguments:
                        print(argument.__str__())
                        availArgs = {k: v for k, v in usedArguments.items() if v != argument}

                    return [argsetSearch, availArgs, caesSearch]
        return []

    def evaluateDialogue(self):
        """
        Evaluates the dialogue from text file
        """

        self.propositions = commandStack['PropLiterals']['propositions']
        self.argumentsDefense = commandStack['Arguments']['Defense']
        self.argumentsProsecution = commandStack['Arguments']['Prosecution']
        self.ps = ProofStandard(commandStack['PropLiterals']['proofstandardList'])
        weights = commandStack['ArgumentWeights']
        assumptions = commandStack['Assumptions']
        self.audience = Audience(assumptions,weights)
        argumentsDefenseUsing = deepcopy(self.argumentsDefense)
        argumentsProsecutionUsing = deepcopy(self.argumentsProsecution)
        
        argset = ArgumentSet()
        argset.add_argument(self.argumentsProsecution.values()[0])
        argset.add_argument(self.argumentsDefense.values()[0])
        burdenOfProof = "Defense" 
        while(True):

            caes = CAES(argset,self.audience,self.ps)
            burdenOfProof = self.burdenOfProofLocation(burdenOfProof,caes)

            if (burdenOfProof == "Defense"):
                print('Burden of Proof on Defense')
                res = self.findBestArgument(argumentsDefenseUsing, argset,burdenOfProof, depth = 4)
                if len(res)==3:
                    argset, argumentDefenseUsing , caes = res[0], res[1], res[2]
                else:
                    print('AI cannot come up with a valid solution for Defense')
                    break

            elif(burdenOfProof=="Prosecution"):
                print('Burden of proof on Prosecution')
                res = self.findBestArgument(argumentsProsecutionUsing,burdenOfProof, depth = 4)
                if len(res)==3:
                    argset, argumentDefenseUsing, caes = res[0], res[1], res[2]
                else:
                    print('AI cannot come up with a valid solution for Prosecution')
                    break

            else: raise Exception('Burden of Proof Invalid : {}'.format(burdenOfProof)) 
