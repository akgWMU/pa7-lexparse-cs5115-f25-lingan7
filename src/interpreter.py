from typing import Dict, List, Optional, Union, Any
from src.ast import *
from src.lexer import Token, TokenType

class InterpreterError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f'{message} at line {token.line}, column {token.column}')
        else:
            super().__init__(message)

class Interpreter(NodeVisitor):
    def __init__(self):
        self.GLOBAL_MEMORY: Dict[str, Any] = {}
        self.call_stack: List[Dict[str, Any]] = [self.GLOBAL_MEMORY]
        self.current_scope = self.GLOBAL_MEMORY
    
    def error(self, message: str, token: Optional[Token] = None):
        raise InterpreterError(message, token)
    
    def visit_Program(self, node: Program):
        self.visit(node.block)
    
    def visit_Block(self, node: Block):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_VarDecl(self, node: VarDecl):
        # Variable declarations are handled during semantic analysis
        pass
    
    def visit_TypeNode(self, node: TypeNode):
        # Type nodes are only used during semantic analysis
        pass
    
    def visit_Compound(self, node: Compound):
        for child in node.children:
            self.visit(child)
    
    def visit_Assign(self, node: Assign):
        var_name = node.left.value
        value = self.visit(node.right)
        
        # Check if variable exists in current or any enclosing scope
        for scope in reversed(self.call_stack):
            if var_name in scope:
                scope[var_name] = value
                return
        
        # If we get here, the variable wasn't found in any scope
        self.error(f'Variable {var_name} not declared', node.left.token)
    
    def visit_Var(self, node: Var):
        var_name = node.value
        
        # Check if variable exists in current or any enclosing scope
        for scope in reversed(self.call_stack):
            if var_name in scope:
                return scope[var_name]
        
        self.error(f'Variable {var_name} not found', node.token)
    
    def visit_NoOp(self, node: NoOp):
        pass
    
    def visit_BinOp(self, node: BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.op.type == TokenType.PLUS:
            return left + right
        elif node.op.type == TokenType.MINUS:
            return left - right
        elif node.op.type == TokenType.MULTIPLY:
            return left * right
        elif node.op.type == TokenType.DIVIDE:
            if right == 0:
                self.error('Division by zero', node.op)
            return left / right
        elif node.op.type == TokenType.EQUAL:
            return 1 if left == right else 0
        elif node.op.type == TokenType.NOT_EQUAL:
            return 1 if left != right else 0
        elif node.op.type == TokenType.LESS:
            return 1 if left < right else 0
        elif node.op.type == TokenType.LESS_EQUAL:
            return 1 if left <= right else 0
        elif node.op.type == TokenType.GREATER:
            return 1 if left > right else 0
        elif node.op.type == TokenType.GREATER_EQUAL:
            return 1 if left >= right else 0
        elif node.op.type == TokenType.AND:
            return 1 if left and right else 0
        elif node.op.type == TokenType.OR:
            return 1 if left or right else 0
        else:
            self.error(f'Unknown operator: {node.op.type}', node.op)
    
    def visit_UnaryOp(self, node: UnaryOp):
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)
        elif node.op.type == TokenType.NOT:
            value = self.visit(node.expr)
            return 0 if value else 1
        else:
            self.error(f'Unknown unary operator: {node.op.type}', node.op)
    
    def visit_Num(self, node: Num):
        return node.value
    
    def visit_String(self, node: String):
        return node.value
    
    def visit_If(self, node: If):
        condition = self.visit(node.condition)
        if condition != 0:  # Non-zero is true
            self.visit(node.true_branch)
        elif node.false_branch is not None:
            self.visit(node.false_branch)
    
    def visit_While(self, node: While):
        while self.visit(node.condition) != 0:  # While condition is true (non-zero)
            self.visit(node.body)
    
    def visit_Read(self, node: Read):
        var_name = node.var.value
        try:
            value = input(f'Enter value for {var_name}: ')
            
            # Try to convert to int first, then float if that fails
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    self.error(f'Invalid number: {value}', node.token)
            
            # Update the variable in the current scope
            for scope in reversed(self.call_stack):
                if var_name in scope:
                    scope[var_name] = value
                    return
            
            # If we get here, the variable wasn't found in any scope
            self.error(f'Variable {var_name} not declared', node.token)
            
        except EOFError:
            self.error('Unexpected end of input', node.token)
    
    def visit_Write(self, node: Write):
        if isinstance(node.expr, String):
            print(node.expr.value, end='')
        else:
            value = self.visit(node.expr)
            print(value, end='')

def interpret(ast: ASTNode):
    interpreter = Interpreter()
    interpreter.visit(ast)
    return interpreter.GLOBAL_MEMORY
