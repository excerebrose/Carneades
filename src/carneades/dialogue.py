"""
Dialogue
=========
class Dialogue which requires just a text file with your commands and evaluates the
dialogue based scenario using an intelligent agent - ie, using depth first search.
To run it :
>>> d = Dialogue("textfilename")
>>> d.evaluateDialogue()
"""

import os
import sys
from copy import deepcopy
from itertools import combinations
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from carneades.caes import CAES, ArgumentSet, ProofStandard, Audience 
from carneades.reader import Reader

class Dialogue(object):
    """
    Class Designed to evaluate a dialogue based trial system. 
    Trains the AI using search method to pick best possible arguments to support a side.

    """
    def __init__(self, textFile):
        """
        Constructor for Dialogue class.
        Loads up text file and parses it using the :class:`.Reader` class

        """
        file = open(textFile,"r")
        readerObject = Reader()
        readerObject.load(file)
        self.commandStack = readerObject.getCommandStack() #Dictionary of different types of vars
    
    def burdenOfProofLocation(self, burdenOfProof, caes):
        """
        Function to check where a burden of proof lies.

        :param burdenOfProof: The current burden of proof - either Defense or Prosecution.

        :type burdenOfProof: str

        :param caes: The modified CAES system

        :type caes: :class:`.CAES`

        :rtype: str

        """
        if (burdenOfProof == "Defense") and caes.acceptable(self.argumentsDefense[0].conclusion):
            return "Prosecution"
        elif burdenOfProof == "Prosecution" and caes.acceptable(self.argumentsProsecution[0].conclusion):
            return "Defense"
        else:
            return burdenOfProof

    def findBestArgument(self, availArgs, argset, burdenOfProof, depth) :
        """
        Function that performs a depth first search to evaluate whether a possible set of arguments shift the burden of proof or not.

        :param availArgs: List of available args for the side.

        :type availArgs: [:class:`.Argument`]

        :param argset: The current Argument Set

        :type argset: :class:`.ArgumentSet`

        :param burdenOfProof: The current burden of proof - either Defense or Prosecution.

        :type burdenOfProof: str

        :param depth: depth to search until - becomes a threshold of sorts.

        :type depth: int
        :return: Return an array of modified caes, modified argumentse and leftover arguments for the side
        :rtype: [:class:`.CAES`,  :class:`.ArgumentSet`, [:class:`Argument`]]

        """
        argsetSearch = deepcopy(argset) 
        if (len(availArgs) >= depth):
            pass
        else:
            depth = len(availArgs)

        if burdenOfProof == "Defense":
            conclusion = self.argumentsDefense[0].conclusion
        else:
            conclusion = self.argumentsProsecution[0].conclusion

        combos = combinations(availArgs,depth)
        for c in combos:
            usedArguments = []
            for arg in c:
                argsetSearch.add_argument(arg)
                usedArguments.append(arg)

                caesSearch = CAES(argsetSearch,self.audience,self.ps)

                acceptable = caesSearch.acceptable(conclusion)
                if(acceptable):
                    print('Side added argument(s):')
                    for argument in added_arguments:
                        print(argument.__str__())
                        availArgs = {k: v for k, v in usedArguments.items() if v != argument}

                    return [caesSearch , argsetSearch, availArgs]
        return []

    def evaluateDialogue(self):
        """
        Evaluates the dialogue from text file
        """

        self.propositions = self.commandStack['PropLiteral']
        self.argumentsDefense = self.commandStack['ArgumentsDefense']
        self.argumentsProsecution = self.commandStack['ArgumentsProsecution']
        self.ps = ProofStandard(self.commandStack['proofStandardList'])
        weights = self.commandStack['Weights']
        assumptions = self.commandStack['Assumptions']
        self.audience = Audience(assumptions,weights)
        argumentsDefenseUsing = deepcopy(self.argumentsDefense)
        argumentsProsecutionUsing = deepcopy(self.argumentsProsecution)
        
        argset = ArgumentSet()
        argset.add_argument(self.argumentsProsecution[0])
        argset.add_argument(self.argumentsDefense[0])
        burdenOfProof = "Defense" 
        while(True):

            caes = CAES(argset,self.audience,self.ps)
            burdenOfProof = self.burdenOfProofLocation(burdenOfProof,caes)

            if (burdenOfProof == "Defense"):
                print('\n ***** Burden of Proof on Defense *****')
                res = self.findBestArgument(argumentsDefenseUsing, argset,burdenOfProof, depth = 4)
                if len(res)==3:
                    caes, argset, argumentDefenseUsing = res[0], res[1], res[2]
                else:
                    print('AI cannot come up with a valid solution for Defense. Prosecution Wins')
                    break

            elif(burdenOfProof=="Prosecution"):
                print('\n ***** Burden of proof on Prosecution *****')
                res = self.findBestArgument(argumentsProsecutionUsing,argset, burdenOfProof, depth = 4)
                if len(res)==3:
                    caes, argset, argumentDefenseUsing = res[0], res[1], res[2]
                else:
                    print('AI cannot come up with a valid solution for Prosecution. Defense Wins')
                    break

            else: raise Exception('Burden of Proof Invalid : {}'.format(burdenOfProof)) 

def dialogue_demo():
    r = Dialogue('test2.txt')
    r.evaluateDialogue()



if __name__ == '__main__':
    dialogue_demo()