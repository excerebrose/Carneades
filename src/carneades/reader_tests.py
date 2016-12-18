import unittest
from caes import PropLiteral, Argument
from reader import Reader

class ReaderTestCase(unittest.TestCase):
    """
    Test cases for Reader class
    """

    def test_invalid_key(self):
        ''' Raises error on invalid key '''
        comd = {"func_name":"PropLiteral","var_name":"prop","args":"None","type":"construct","invalid_key":"key"}
        r = Reader()
        self.assertRaises(ValueError, r.check_command_structure, comd)

    def test_required_key_missing(self):
        ''' Raises error on required key missing key '''
        comd = {"var_name":"prop","args":"None","type":"construct"}
        r = Reader()
        self.assertRaises(IOError, r.check_command_structure, comd)
    
    def test_invalid_function(self):
        ''' Raises error on invalid function call '''
        comd = {"func_name":"PropLiteralssss","var_name":"prop","args":"None","type":"construct"}
        r = Reader()
        self.assertRaises(NameError, r.check_command_structure, comd)
        
    def test_invalid_variable_type(self):
        ''' Raises error on variable type mismatch '''
        r = Reader()
        kill = PropLiteral("kill")
        r.initialised_variables = {'kill':kill}
        var_name = 'kill'
        var_type = Argument
        self.assertRaises(TypeError, r.is_initialized, var_name, var_type)
    
    def test_uninitialised_variable(self):
        ''' Raises error on variable not found '''
        r = Reader()
        kill = PropLiteral("kill")
        r.initialised_variables = {'kill':kill}
        var_name = 'intent'
        var_type = PropLiteral
        self.assertRaises(NameError, r.is_initialized, var_name, var_type)

if __name__ == '__main__':
    unittest.main()