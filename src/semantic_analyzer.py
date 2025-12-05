from typing import Dict, List, Optional, Union, Any
from src.ast import *
from src.lexer import Token, TokenType

class Symbol:
    def __init__(self, name: str, type: Optional[Type] = None):
        self.name = name
        self.type = type
        self.scope_level = 0

class VarSymbol(Symbol):
    def __init__(self, name: str, type: Type, index_start: Optional[int] = None, 
                 index_end: Optional[int] = None):
        super().__init__(name, type)
        self.index_start = index_start
        self.index_end = index_end
    
    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, type={self.type})>'
    
    __repr__ = __str__

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name: str):
        super().__init__(name)
    
    def __str__(self):
        return self.name
    
    __repr__ = __str__

class ScopedSymbolTable:
    def __init__(self, scope_name: str, scope_level: int, enclosing_scope: 'ScopedSymbolTable' = None):
        self._symbols: Dict[str, Symbol] = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
    
    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in [
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope', self.enclosing_scope.scope_name if self.enclosing_scope else None)
        ]:
            lines.append(f'{header_name:15}: {header_value}')
        
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(f'{key:7}: {value}' for key, value in self._symbols.items())
        lines.append('\n')
        return '\n'.join(lines)
    
    __repr__ = __str__
    
    def insert(self, symbol: Symbol) -> None:
        symbol.scope_level = self.scope_level
        self._symbols[symbol.name] = symbol
    
    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        symbol = self._symbols.get(name)
        
        if symbol is not None:
            return symbol
        
        if current_scope_only or self.enclosing_scope is None:
            return None
        
        return self.enclosing_scope.lookup(name)

class SemanticError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f'{message} at line {token.line}, column {token.column}')
        else:
            super().__init__(message)

class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope: Optional[ScopedSymbolTable] = None
        self.builtin_types = {
            'INTEGER': Type.INTEGER,
            'FLOAT': Type.FLOAT,
        }
    
    def error(self, message: str, token: Optional[Token] = None):
        raise SemanticError(message, token)
    
    def visit_Program(self, node: Program):
        print('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )
        
        # Insert built-in types
        for type_name, type_value in self.builtin_types.items():
            global_scope.insert(BuiltinTypeSymbol(type_name))
        
        self.current_scope = global_scope
        
        # Visit subtree
        self.visit(node.block)
        
        print(global_scope)
        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE scope: global')
    
    def visit_Block(self, node: Block):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_VarDecl(self, node: VarDecl):
        type_name = node.type_node.type
        type_symbol = self.current_scope.lookup(type_name.name)
        
        if type_symbol is None:
            self.error(f'Type {type_name} is not declared', node.type_node.token)
        
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol.type)
        
        # Check if variable is already declared in the current scope
        if self.current_scope.lookup(var_name, current_scope_only=True):
            self.error(f'Duplicate identifier {var_name} found', node.var_node.token)
        
        self.current_scope.insert(var_symbol)
    
    def visit_TypeNode(self, node: TypeNode):
        pass
    
    def visit_Compound(self, node: Compound):
        for child in node.children:
            self.visit(child)
    
    def visit_Assign(self, node: Assign):
        self.visit(node.right)  # Type of the right side
        self.visit(node.left)   # Check if variable exists and get its type
    
    def visit_Var(self, node: Var):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol is None:
            self.error(f'Symbol(identifier) not found: {var_name}', node.token)
        
        node.type = var_symbol.type
    
    def visit_NoOp(self, node: NoOp):
        pass
    
    def visit_BinOp(self, node: BinOp):
        self.visit(node.left)
        self.visit(node.right)
        
        # Type checking
        if node.op.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
            if node.left.type != node.right.type:
                self.error(
                    f'Type mismatch in {node.op.type} operation: {node.left.type} and {node.right.type}',
                    node.op
                )
            node.type = node.left.type  # Result has the same type as operands
        
        # Comparison operators always return integer (0 or 1)
        elif node.op.type in (TokenType.EQUAL, TokenType.NOT_EQUAL, 
                             TokenType.LESS, TokenType.LESS_EQUAL,
                             TokenType.GREATER, TokenType.GREATER_EQUAL):
            if node.left.type != node.right.type:
                self.error(
                    f'Cannot compare {node.left.type} and {node.right.type} with {node.op.type}',
                    node.op
                )
            node.type = Type.INTEGER  # Comparisons return integer (0 or 1)
        
        # Logical operators
        elif node.op.type in (TokenType.AND, TokenType.OR):
            if node.left.type != Type.INTEGER or node.right.type != Type.INTEGER:
                self.error(
                    f'Logical operators require integer operands, got {node.left.type} and {node.right.type}',
                    node.op
                )
            node.type = Type.INTEGER  # Logical operations return integer (0 or 1)
    
    def visit_UnaryOp(self, node: UnaryOp):
        self.visit(node.expr)
        
        if node.op.type == TokenType.PLUS or node.op.type == TokenType.MINUS:
            if node.expr.type not in (Type.INTEGER, Type.FLOAT):
                self.error(
                    f'Unary operator {node.op.type} requires numeric operand, got {node.expr.type}',
                    node.op
                )
            node.type = node.expr.type
        
        elif node.op.type == TokenType.NOT:
            if node.expr.type != Type.INTEGER:
                self.error(
                    f'Logical NOT requires integer operand, got {node.expr.type}',
                    node.op
                )
            node.type = Type.INTEGER  # NOT returns integer (0 or 1)
    
    def visit_Num(self, node: Num):
        # Type is already set during parsing
        pass
    
    def visit_String(self, node: String):
        # Strings are only allowed in WRITE statements
        pass
    
    def visit_If(self, node: If):
        self.visit(node.condition)
        if node.condition.type != Type.INTEGER:
            self.error(
                'Condition must be an integer expression (0 for false, non-zero for true)',
                node.condition.token
            )
        
        self.visit(node.true_branch)
        if node.false_branch is not None:
            self.visit(node.false_branch)
    
    def visit_While(self, node: While):
        self.visit(node.condition)
        if node.condition.type != Type.INTEGER:
            self.error(
                'Condition must be an integer expression (0 for false, non-zero for true)',
                node.condition.token
            )
        
        self.visit(node.body)
    
    def visit_Read(self, node: Read):
        # The semantic check for the variable is done in visit_Var
        self.visit(node.var)
    
    def visit_Write(self, node: Write):
        # Can write any expression or string
        self.visit(node.expr)

def analyze(node: ASTNode):
    analyzer = SemanticAnalyzer()
    analyzer.visit(node)
