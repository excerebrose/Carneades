"""
Reader
=========
Class reader is used to load up custom syntax config file for using the CAES System model.
First things first, this class depends on an external library called PyYAML for parsing. So you can do either 
From your virtual environment

>>> pip install -r Requirements.txt

or

>>> pip install PyYAML

To load up a text file written in the specified format:
Note however the file should be opened only in read mode.

>>> r = Reader()
>>> file = open("file.text")
>>> r.load(file)

Syntax rules for class Reader:
Every command is written in the following manner ::

    9: 
        func_name: Argument
        type: construct
        var_name: arg2
        args:
            conclusion: intent
            premises: [witness1]
            exceptions: [unreliable1]

    10: 
        func_name: add_argument
        var_name: argset
        type: func
        args:
            argument: arg2

Lets walk through the syntax elements:
Every command precedes with a command number (can start either from 0 or 1).
Every command number must be unique and in-order the order you want them to be executed.

We use indentation to seperate heirchy just like python.
Comments are written with like ::

    #This is a comment. just like python. Life is great yeah?

The bare required 'keys' for every command are ::

    func_name: # can be any of the function names that are approved (check misc for data)
    type: # construct / func - depends on the type of function
    var_name: #easy enough to understand
    args: #indented args. see test1.txt for example


All functions have the same name while calling them from the api, so make sure that's taken care of. The arguments take names
as parameters, so just go over the Reader class to see what's allowed or not. 
Check the test1.txt to see examples in case of confusion.

To run tests on the Reader class use ::

    python reader_tests.py

"""

import os
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from carneades.caes import PropLiteral, Argument, ArgumentSet, Audience, ProofStandard, CAES

class Reader(object):
    """
    Class Designed to read data from a *.txt file.
    Loads data into CAES system for evaluation.

    """

    def __init__ (self):
        """
        Constructor for Reader class.
        To load up a text file use load()

        """
        self.fileObject = None;
        self. initialised_variables = {}

    def load(self,fileObject):
        """
        Function to initialise the reader class with a *.txt file object
        If class is already initialised with fileObject, replaces it.

        :param fileObject: A text file object containing the CAES defined input sequences
                        Mode should be r - ie. read only. No writing is done to the file.
        :type fileObject: file object

        """
        if fileObject.mode != 'r':
            raise Exception('{} not opened in \'r\' mode. Retry again.'.format(fileObject.name))
        if self.fileObject is not None:
            print('Updating instance of class. Closing {}'.format(self.fileObject.name))
            self.fileObject.close()
        print('Loading text file {}'.format(fileObject.name))
        self.fileObject = fileObject
        self.deserialise()

    def is_initialized(self, var_name, var_type):
        """
        Function to check whether a variable has been initialised.

        :param var_name: The variable name to check.

        :type var_name: str

        :param var_type: The type to check against type of var_name

        :type var_type: Any

        :rtype: var_type
        :raises TypeError: if the var_name type doesnot match var_type
        :raises NameError: if the var_name isn't initialised

        """
        if var_name in self.initialised_variables :
            if var_type == type(self.initialised_variables[var_name]):
                return self.initialised_variables[var_name]
            else:
                raise TypeError("{} doesn't match required type {}".format(type(self.initialised_variables[var_name]),var_type))
        else:
            raise NameError("{} is not defined".format(var_name))

    def check_command_structure(self, c):
        """
        Checks validty of a command sequence.
        This checks syntactic validity of the command in terms of whta's allowed in the specific type of function call -
        which ones are allowed and which ones aren't.
        Take a look at the source and the valid_functions dict to see what's happening.

        :param c: command 
        :type c: dict

        :raises ValueError: if the key in command is invalid in args/ main
        :raises IOError: if a required key is missing in main / args
        :raises NameError: Invalid function name

        """
        must_have_keys = ['type','func_name','var_name','args']
        optional_keys = ['return_var']
        valid_functions = {
        'PropLiteral':{'valid_args':['polarity','proofStandard'],'req_args':[]},
        'Argument':{'valid_args':['conclusion','premises','exceptions'],'req_args':['conclusion']},
        'ArgumentSet':{'valid_args':[],'req_args':[]},
        'Audience': {'valid_args':['assumptions','weight'],'req_args':['assumptions','weight']}, 
        'ProofStandard': {'valid_args':['propstandards'],'req_args':['propstandards']},
        'CAES':{'valid_args':['argset','audience','proofstandard','alpha','beta','gamma'],'req_args':['argset','audience','proofstandard']},
        'negate':{'valid_args':['return_var'],'req_args':[]},
        'add_argument':{'valid_args':['argument','arg_id'],'req_args':['argument']},
        'add_proposition': {'valid_args':['proposition','return_var'],'req_args':['proposition','return_var']},
        'get_arguments': {'valid_args':['proposition','return_var'],'req_args':['proposition','return_var']},   
        'draw':{'valid_args':['debug'],'req_args':[]},
        'write_to_graphviz': {'valid_args':['fname'],'req_args':[]},
        'get_proofstandard': {'valid_args':['proposition','return_var'],'req_args':['proposition','return_var']},
        'acceptable': {'valid_args':['proposition','return_var'],'req_args':['proposition']},
        'applicable': {'valid_args':['proposition','return_var'],'req_args':['proposition']},
        'get_all_arguments': {'valid_args':[],'req_args':[]},
        'max_weight_applicable': {'valid_args':['arguments','return_var'],'req_args':['arguments']},
        'max_weight_con': {'valid_args':['proposition','return_var'],'req_args':['proposition']},
        'max_weight_pro': {'valid_args':['proposition','return_var'],'req_args':['proposition']},
        'meets_proof_standard': {'valid_args':['proposition','standard','return_var'],'req_args':['proposition','standard']},
        'weight_of': {'valid_args':['argument','return_var'],'req_args':['argument']}
        }
        for k in c:
            if k not in must_have_keys and k not in optional_keys:
                raise ValueError('Key:{} invalid. Refer to documentation on correct syntax'.format(k))
        for k in must_have_keys:
            if k not in c:
                raise IOError("Required key {} missing".format(k))
        func_name = c['func_name']
        if func_name in valid_functions:
            #Check for valid Arguments alowed
            valid_args = valid_functions[func_name]['valid_args']
            req_args = valid_functions[func_name]['req_args']
            if c['args'] != "None":
                for arg in c['args']:
                    if arg not in valid_args:
                        raise ValueError("Arg: {} invalid for constructor {}".format(arg,func_name))
                for arg in req_args:
                    if arg not in c['args']:
                        raise IOError("Required argument(s) {} missing in {}".format(arg,func_name))
                    elif c['args'][arg] == "None":
                        raise IOError("Required argument(s) {} cannot be None".format(arg))
            if c['args'] == "None" and len(req_args) > 0:
                raise IOError("Required arguments missing in {}".format(func_name))
        else:
            raise NameError("Not a valid function {}".format(func_name))

    def deserialise(self):
        """
        Function to deserialise the given file, validate it and creates and executes a command stack.

        :raises ValueError: if the return_var is added when not required
        """
        command_stack = yaml.load(self.fileObject)
        self.initialised_variables = {}
        print("Deserialising file {}".format(self.fileObject.name))
        for k,command in command_stack.items():
            print("Processing command {}...".format(k))
            self.check_command_structure(command)
            var_name = command['var_name']
            func_name = command['func_name']
            args = command['args']
            if (command['type'] == "construct"):
                if func_name == "PropLiteral":
                    if args != "None":
                        self.initialised_variables[var_name] = PropLiteral(var_name,polarity=args['polarity'])
                    else:
                        self.initialised_variables[var_name] = PropLiteral(var_name)
                if func_name == "Argument":
                    premises = []
                    exceptions = []
                    conclusion = self.is_initialized(args['conclusion'],PropLiteral)
                    if 'premises' in args and args["premises"] != "None":
                        premises = [self.is_initialized(x,PropLiteral) for x in args['premises']]
                    if 'exceptions' in args and args["exceptions"] != "None":
                        exceptions = [self.is_initialized(x,PropLiteral) for x in args['exceptions']]
                    self.initialised_variables[var_name] = Argument(conclusion,premises=set(premises),exceptions=set(exceptions))
                if func_name == "ArgumentSet":
                    self.initialised_variables[var_name] = ArgumentSet()
                if func_name == "Audience":
                    assumptions = [self.is_initialized(x,PropLiteral) for x in args['assumptions']]
                    self.initialised_variables[var_name] = Audience(set(assumptions),args['weight'])
                if func_name == "ProofStandard":
                    prop_standards = [(self.is_initialized(k,PropLiteral),v) for k,v in args['propstandards'].items()]
                    self.initialised_variables[var_name] = ProofStandard(prop_standards)
                if func_name == "CAES":
                    argset = self.is_initialized(args['argset'],ArgumentSet)
                    audience = self.is_initialized(args['audience'],Audience)
                    proofStandard = self.is_initialized(args['proofstandard'],ProofStandard)
                    alpha = 0.4
                    beta = 0.3
                    gamma = 0.2
                    if 'alpha' in args and args['alpha'] != "None":
                        alpha = args['alpha']
                    if 'beta' in args and args['beta'] != "None":
                        alpha = args['beta']
                    if 'gamma' in args and args['gamma'] != "gamma":
                        alpha = args['gamma']
                    self.initialised_variables[var_name] = CAES(argset,audience,proofStandard,alpha,beta,gamma)
            elif (command['type'] == "func"):
                return_var = None
                if 'return_var' in args and args['return_var'] != "None":
                    return_var = args['return_var']
                if func_name == 'negate':
                    var = self.is_initialized(var_name, PropLiteral)
                    if return_var is not None:
                        self.initialised_variables[return_var] = var.negate()
                    else:
                        print(var.negate())
                if func_name == 'add_argument':
                    var = self.is_initialized(var_name, ArgumentSet)
                    arg = self.is_initialized(args['argument'], Argument)
                    arg_id = None
                    if 'arg_id' in args and args['arg_id'] != "None":
                        arg_id = args['arg_id']
                    if return_var is not None:
                        raise ValueError("{} does not take a return variable".format(func_name))
                    else:
                        var.add_argument(arg,arg_id)
                if func_name == "draw":
                    var = self.is_initialized(var_name, ArgumentSet)
                    debug = False
                    if 'debug' in args and args['debug'] != "None":
                        debug = args['debug']
                    var.draw(debug)
                if func_name == "add_proposition":
                    var = self.is_initialized(var_name, ArgumentSet)
                    proposition = self.is_initialized(args['proposition'],PropLiteral)
                    return_var = args['return_var']
                    self.initialised_variables[return_var] = var.add_proposiion(proposition)
                if func_name == "get_arguments":
                    var = self.is_initialized(var_name, ArgumentSet)
                    proposition = self.is_initialized(args['proposition'],PropLiteral)
                    return_var = args['return_var']
                    self.initialised_variables[return_var] = var.get_arguments(proposition)
                if func_name == "write_to_graphviz":
                    var = self.is_initialized(var_name, ArgumentSet)
                    fname = None
                    if 'fname' in args and args['fname'] != "None":
                        fname = args['fname']
                    var.write_to_graphviz(fname)
                if func_name == "get_proofstandard":
                    var = self.is_initialized(var_name,ProofStandard)
                    prop = self.is_initialized(args['proposition'],PropLiteral)
                    return_var = args['return_var']
                    self.initialised_variables[return_var] = var.get_proofstandard(prop)
                if func_name == "acceptable":
                    var = self.is_initialized(var_name,CAES)
                    prop = self.is_initialized(args['proposition'],PropLiteral)
                    if return_var is not None:
                        self.initialised_variables[return_var] = var.acceptable(prop)
                    else:
                        var.acceptable(prop)
                if func_name == "applicable":
                    var = self.is_initialized(var_name,CAES)
                    prop = self.is_initialized(args['proposition'],PropLiteral)
                    if return_var is not None:
                        self.initialised_variables[return_var] = var.applicable(prop)
                    else:
                        var.applicable(prop)
                if func_name == "get_all_arguments":
                    var = self.is_initialized(var_name,CAES)
                    var.get_all_arguments()
                if func_name == "max_weight_applicable":
                    var = self.is_initialized(var_name,CAES)
                    arguments = [self.is_initialized(argument, Argument) for argument in args['arguments']]
                    if return_var is None:
                        print(var.max_weight_applicable(arguments))
                    else:
                        self.initialised_variables[return_var] = var.max_weight_applicable(arguments)
                if func_name == "max_weight_con":
                    var = self.is_initialized(var_name,CAES)
                    prop =  self.is_initialized(args['proposition'],PropLiteral)
                    if return_var is None:
                        print(var.max_weight_con(prop))
                    else:
                        self.initialised_variables[return_var] = var.max_weight_con(prop)
                if func_name == "max_weight_pro":
                    var = self.is_initialized(var_name,CAES)
                    prop =  self.is_initialized(args['proposition'],PropLiteral)
                    if return_var is None:
                        print(var.max_weight_pro(prop))
                    else:
                        self.initialised_variables[return_var] = var.max_weight_pro(prop)
                if func_name == "meets_proof_standard":
                    var = self.is_initialized(var_name,CAES)
                    prop =  self.is_initialized(args['proposition'],PropLiteral)
                    standard = args['standard']
                    if return_var is None:
                        print(var.meets_proof_standard(prop,standard))
                    else:
                        self.initialised_variables[return_var] = var.meets_proof_standard(prop,standard)
                if func_name == "weight_of":
                    var = self.is_initialized(var_name,CAES)
                    argument =  self.is_initialized(args['argument'],Argument)
                    if return_var is None:
                        print(var.weight_of(argument))
                    else:
                        self.initialised_variables[return_var] = var.weight_of(argument)
            else:
                raise ValueError("{} - invalid argument for key \'type\'")        
            print("..Done")


def reader_demo():
    r = Reader()
    f = open('test1.txt','r')
    r.load(f)

DOCTEST = False

if __name__ == '__main__':

    if DOCTEST:
        import doctest
        doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
    else:
       reader_demo()
