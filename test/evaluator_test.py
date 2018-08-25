import unittest
import sys
sys.path.append("../src/")
from monkey import token
from monkey import lexer
from monkey import ast
from monkey import parser
from monkey import evaluator as e

class EvaluatorTest(unittest.TestCase):

    def test_eval_integer_expression(self):
        tests = [
            ("5", 5),
            ("10", 10),
            ("5", 5),         
            ("10", 10),         
            ("-5", -5),         
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),         
            ("2 * 2 * 2 * 2 * 2", 32),         
            ("-50 + 100 + -50", 0),         
            ("5 * 2 + 10", 20),         
            ("5 + 2 * 10", 25),         
            ("20 + 2 * -10", 0),         
            ("50 / 2 * 2 + 10", 60),         
            ("2 * (5 + 10)", 30),         
            ("3 * 3 * 3 + 10", 37),         
            ("3 * (3 * 3) + 10", 37),         
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        ]
        for t in tests:
            evaluated = self.check_eval(t[0])
            self.assertTrue(self.check_integer_object(evaluated, t[1]))
    
    def check_eval(self, source):
        l = lexer.new(source)
        p = parser.new(l)
        program = p.parse_program()
        return e.Eval(program)

    def check_integer_object(self, obj, expected):
        if not type(obj) is e.Integer:
            print('object is not Integer. got={}'.format(type(obj)))
            return False
        if obj.value != expected:
            print('object has wrong value. got={}'.format(obj.value))
            return False
        return True

    def test_eval_boolean_expression(self):
        tests = [
            ("true", True),
            ("false", False)
        ]
        for t in tests:
            evaluated = self.check_eval(t[0])
            self.assertTrue(self.check_boolean_object(evaluated, t[1]))
    
    def check_boolean_object(self, obj, expected):
        if not type(obj) is e.Boolean:
            print('object is not Boolean. got={}'.format(type(obj)))
            return False
        if obj.value != expected:
            print('object has wrong value. got={}'.format(obj.value))
            return False
        return True

    def test_bang_operator(self):
        tests = [
            ("!true", False),
            ("!false", True),         
            ("!5", False),         
            ("!!true", True),         
            ("!!false", False),         
            ("!!5", True),
        ]
        for t in tests:
            evaluated = self.check_eval(t[0])
            self.assertTrue(self.check_boolean_object(evaluated, t[1]))

if __name__ == '__main__':
    unittest.main()