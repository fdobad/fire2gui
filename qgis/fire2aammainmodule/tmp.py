from C2FSB.Cell2Fire import ParseInputs

parser = ParseInputs.Parser()
opac = parser._get_optional_actions()
'''
pars = { sa.dest : { 'optstr' : sa.option_strings[0], 'type': sa.type, 'default': sa.default, 'help':sa.help} for sa in opac[1:] }
assert parser.__dict__['_actions'] == parser._get_optional_actions()
'''
pars = { a.dest : a.__dict__ for a in parser._get_optional_actions() }

