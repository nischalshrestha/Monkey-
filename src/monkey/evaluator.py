from monkey import ast

"""
Object stuff
"""

NULL_OBJ = 'NULL'
INTEGER_OBJ = 'INTEGER'
BOOLEAN_OBJ = 'BOOLEAN'
RETURN_VALUE_OBJ = 'RETURN_VALUE'
ERROR_OBJ = 'ERROR'

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

class ReturnValue(Object):
    value = None # Object
    def __init__(self, value=None):
        self.value = value
    def object_type(self):
        return RETURN_VALUE_OBJ
    def inspect(self):
        return self.value.inspect()

class Error(Object):
    message = None # Object
    def __init__(self, message=None):
        self.message = message
    def object_type(self):
        return ERROR_OBJ
    def inspect(self):
        return 'ERROR: '+ self.message

NULL = Null()
TRUE  = Boolean(True) 
FALSE = Boolean(False)

"""
Evaluator stuff
"""

# takes in ast.Node
def Eval(node):
    if type(node) is ast.Program:
        return eval_program(node)
    elif type(node) is ast.ExpressionStatement:
        return Eval(node.expression)
    elif type(node) is ast.IntegerLiteral:
        return Integer(node.value)
    elif type(node) is ast.Boolean:
        return native_boolean_object(node.value)
    elif type(node) is ast.PrefixExpression:
        right = Eval(node.right)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    elif type(node) is ast.InfixExpression:
        left = Eval(node.left)
        if is_error(left):
            return left
        right = Eval(node.right)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    elif type(node) is ast.BlockStatement:
        return eval_block_statement(node)
    elif type(node) is ast.IfExpression:
        return eval_if_expression(node)
    elif type(node) is ast.ReturnStatement:
        val = Eval(node.return_value)
        if is_error(val):
            return val
        return ReturnValue(val)
    return None

def is_error(obj):
    if obj != None:
        return obj.object_type() == ERROR_OBJ
    return False

def eval_program(program):
    result = Object()
    for s in program.statements:
        result = Eval(s)
        if type(result) is ReturnValue:
            return result.value
        if type(result) is Error:
            return result
    return result

def eval_block_statement(block):
    result = Object()
    for statement in block.statements:
        result = Eval(statement)
        rt = result.object_type()
        if rt == RETURN_VALUE_OBJ or rt == ERROR_OBJ:
            return result
    return result

def eval_prefix_expression(operator, right):
    if operator == "!":
        return eval_bang_operator_expression(right)
    if operator == "-":
        return eval_minus_prefix_operator(right)
    return new_error(f"unknown operator: {operator}{right.object_type()}")

def eval_bang_operator_expression(right):
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE

def eval_minus_prefix_operator(right):
    if right.object_type() != INTEGER_OBJ:
        return new_error(f"unknown operator: -{right.object_type()}")
    value = right.value
    return Integer(-value)

def eval_infix_expression(operator, left, right):
    if left.object_type() == INTEGER_OBJ and right.object_type() == INTEGER_OBJ:
        return eval_integer_infix_expression(operator, left, right)
    elif operator == "==":
        return native_boolean_object(left == right)
    elif operator == "!=":
        return native_boolean_object(left != right)
    elif left.object_type() != right.object_type():
        return new_error(f"type mismatch: {left.object_type()} {operator} {right.object_type()}")
    return new_error(f"unknown operator: {left.object_type()} {operator} {right.object_type()}")
    
def eval_integer_infix_expression(operator, left, right):
    left_val = left.value
    right_val = right.value
    if operator == "+":
        return Integer(left_val + right_val)
    elif operator == "-":
        return Integer(left_val - right_val)
    elif operator == "*":
        return Integer(left_val * right_val)
    elif operator == "/":
        return Integer(left_val / right_val)
    elif operator == "<":
        return native_boolean_object(left_val < right_val)
    elif operator == ">":
        return native_boolean_object(left_val > right_val)
    elif operator == "==":
        return native_boolean_object(left_val == right_val)
    elif operator == "!=":
        return native_boolean_object(left_val != right_val)
    return new_error(f"unknown operator: {left} {operator} {right.object_type()}")

def eval_if_expression(ie):
    condition = Eval(ie.condition)
    if is_truthy(condition):
        return Eval(ie.consequence)
    elif ie.alternative != None:
        return Eval(ie.alternative)
    return NULL

def is_truthy(obj):
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    return True # number is truthy

def native_boolean_object(boolean):
    if boolean:
        return TRUE
    return FALSE

def new_error(string):
    return Error(string)

"""
Environment stuff
"""
