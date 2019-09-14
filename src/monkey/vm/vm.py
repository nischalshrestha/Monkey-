"""
Monkey VM
"""

from typing import List

from monkey import code
from monkey import compiler
from monkey import object
from monkey.common import utilities

STACK_SIZE = 2048
# instead of creating new booleans every time we need them, we just create the 
# two instances we will ever need 
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)

class VM:

    constants: List[object.Object] = []
    instructions: code.Instructions = None
    stack: List[object.Object] = []
    sp: int = 0

    def __init__(self, instructions, constants, stack, sp):
        self.instructions = instructions
        self.constants = constants
        self.stack = stack
        self.sp = sp

    def stack_top(self):
        return None if self.sp == 0 else self.stack[self.sp - 1]
    
    def run(self):
        """
        Execute every instruction generated by the compiler
        """
        ip = 0
        while ip < len(self.instructions):
            op = self.instructions[ip]
            if op == code.OpConstant:
                # because we are using bytearray we will need to specify
                # the end range of the instructions bytearray so we don't
                # overshoot the operand and accidentally read next opcode
                const_index = code.bytes_to_int(self.instructions[ip+1:ip+3])
                # we increment the ip offset variables based on the OpCode
                # for e.g. here, we need to increment by 3 since we have an
                # OpCode and two Operands
                ip += 3
                err = self.push(self.constants[const_index])
                if err != None:
                    return err
            elif op == code.OpAdd or op == code.OpSub or op == code.OpMul or op == code.OpDiv:
                err = self.execute_binary_operation(op)
                if err != None:
                    return err
                # only need to move offset by 1 as there are no operands
                ip += 1
            elif op == code.OpEqual or op == code.OpNotEqual or op == code.OpGreaterThan:
                err = self.execute_comparison(op)
                if err != None:
                    return err
                ip += 1
            elif op == code.OpBang:
                err = self.execute_bang_operator()
                if err != None:
                    return err
                ip += 1
            elif op == code.OpMinus:
                err = self.execute_minus_operator()
                if err != None:
                    return err
                ip += 1
            elif op == code.OpTrue:
                err = self.push(TRUE)
                if err != None:
                    return err
                ip += 1
            elif op == code.OpFalse:
                err = self.push(FALSE)
                if err != None:
                    return err
                ip += 1
            elif op == code.OpPop:
                self.pop()
                ip += 1
            elif op == code.OpJump:
                # This one is just like OpConstant, need to jump to 3 places
                pos = code.bytes_to_int(self.instructions[ip+1:ip+3])
                # pos is the final destination, so instruction pointer should
                # point to it
                ip = pos
            elif op == code.OpJumpNotTruthy:
                # pos should be the place where we would jump to. For e.g:
                # VmTestCase(input='if (1 > 2) { 10 } else { 20 }', expected=20)
                # OpJumpNotTruthy ip=7 bytearray(b'\x10\x00\x01') next_ip=17 (jump to 0010)
                pos = code.bytes_to_int(self.instructions[ip+1:ip+4])
                ip += 3
                # In this case we need to actually see if condition was truthy
                condition = self.pop()
                if not self.is_truthy(condition):
                    # if not truthy, instruction points to right before final destination
                    ip = pos - 1
        return None
    
    def is_truthy(self, obj):
        if type(obj) == object.Boolean:
            return obj.value
        return True

    def execute_binary_operation(self, op):
        """
        Pop off the last two elements on the stack and execute a binary operation
        with them else return an error message if not possible.
        """
        right = self.pop()
        left = self.pop()
        left_type = left.object_type()
        right_type = right.object_type()
        if left_type == object.INTEGER_OBJ and right_type == object.INTEGER_OBJ:
            return self.execute_binary_integer_operation(op, left, right)
        return f'unsupported types for binary operation: {left_type} {right_type}'

    def execute_binary_integer_operation(self, op, left, right):
        """
        Unwrap values of Integer objects of a binary operation and return result. 
        Otherwise, return an error if operator is unrecognized.
        """
        left_value = left.value
        right_value = right.value
        result = 0
        if op == code.OpAdd:
            result = left_value + right_value
        elif op == code.OpSub:
            result = left_value - right_value
        elif op == code.OpMul:
            result = left_value * right_value
        elif op == code.OpDiv:
            result = left_value / right_value
        else:
            return f'unknown integer operator {op}'
        self.push(object.Integer(value=result))

    def execute_comparison(self, op):
        """
        Executes comparison of integers or booleans using a compare operator
        """
        right = self.pop()
        left = self.pop()
        left_type = left.object_type()
        right_type = right.object_type()
        if left_type == object.INTEGER_OBJ or right_type == object.INTEGER_OBJ:
            return self.execute_integer_comparison(op, left, right)
        if op == code.OpEqual:
            return self.push(self.native_bool_to_boolean_object(right == left))
        elif op == code.OpNotEqual:
            return self.push(self.native_bool_to_boolean_object(right != left))
        else:
            return f'unknown operator {op} ({left_type} {right_type})'
    
    def execute_integer_comparison(self, op, left, right):
        """
        Executes integer comparison and pushes result on to the stack
        """
        left_value = left.value
        right_value = right.value
        if op == code.OpEqual:
            return self.push(self.native_bool_to_boolean_object(right_value == left_value))
        elif op == code.OpNotEqual:
            return self.push(self.native_bool_to_boolean_object(right_value != left_value))
        elif op == code.OpGreaterThan:
            return self.push(self.native_bool_to_boolean_object(left_value > right_value))
        else:
            return f'unknown operator {op}'
    
    def native_bool_to_boolean_object(self, boolean):
        """Convert Python boolean to Boolean Object."""
        return TRUE if boolean else FALSE

    def execute_bang_operator(self):
        operand = self.pop()
        if operand.value == True:
            return self.push(FALSE)
        elif operand.value == False:
            return self.push(TRUE)
        else:
            return self.push(FALSE)
    
    def execute_minus_operator(self):
        operand = self.pop()
        if operand.object_type() != object.INTEGER_OBJ:
            return f'unsupported type for negation: {operand.object_type()}'
        return self.push(object.Integer(value=-operand.value))

    def push(self, o):
        if self.sp >= STACK_SIZE:
            return "stack overflow"
        self.stack[self.sp] = o
        self.sp += 1
        return None

    def pop(self):
        """
        Pop an element off the stack and decrement stack pointer and return the
        popped off Object.
        """
        o = self.stack[self.sp-1]
        self.sp -= 1
        return o
    
    def last_popped_stack_element(self):
        """
        This is a peek version that doesn't actually pop the item off stack.
        It's used to test the vm.
        """
        return self.stack[self.sp]

def new(bytecode):
    return VM(
        bytecode.instructions, 
        bytecode.constants,
        utilities.make_list(STACK_SIZE), 
        0
    )
