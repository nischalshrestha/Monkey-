from monkey import ast

"""
Evaluator stuff
"""

# takes in ast.Node
def Eval(node):
    if type(node) is ast.Program:
        return eval_statements(node.statements)
    if type(node) is ast.ExpressionStatement:
        return Eval(node.expression)
    if type(node) is ast.IntegerLiteral:
        return Integer(node.value)
    return None

def eval_statements(statements):
    result = Object()
    for s in statements:
        result = Eval(s)
    return result

"""
Object stuff
"""

NULL_OBJ = 'NULL'
INTEGER_OBJ = 'INTEGER'
BOOLEAN_OBJ = 'BOOLEAN'

# object "interface"
class Object:
    def object_type(self): pass # ObjectType (str)
    def inspect(self): pass # str
    
class Null(Object):
    def object_type(self):
        return NULL_OBJ
    def inspect(self):
        return "null"

class Integer(Object):
    value = 0
    def __init__(self, value=0):
        self.value = value
    def object_type(self):
        return INTEGER_OBJ
    def inspect(self):
        return str(self.value)

class Boolean(Object):
    value = False
    def __init__(self, value=False):
        self.value = value
    def object_type(self):
        return BOOLEAN_OBJ
    def inspect(self):
        return str(self.value)


"""
Enviroment stuff
"""