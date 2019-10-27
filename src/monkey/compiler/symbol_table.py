from typing import NamedTuple
from typing import Dict

from monkey.compiler import *
# from compiler import *

GLOBAL_SCOPE = "GLOBAL"

class Symbol(NamedTuple):
    name: str
    scope: str
    index: int

class SymbolTable:
    store: Dict[str, Symbol]
    num_definitions: int

    def __init__(self, store, num_definitions=0):
        self.store = store
        self.num_definitions = num_definitions

    def define(self, name):
        symbol = Symbol(name=name, index=self.num_definitions, scope=GLOBAL_SCOPE)
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol
    
    def resolve(self, name):
        symbol = self.store[name] if name in self.store else None
        return symbol

def new_symbol_table():
    return SymbolTable({})

# print(Symbol(name='a', scope=GLOBAL_SCOPE, index=0) == Symbol(name='b', index=0, scope=GLOBAL_SCOPE))