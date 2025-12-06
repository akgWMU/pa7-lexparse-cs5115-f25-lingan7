from typing import List, Optional, Union, Dict, Any
from src.lexer import Lexer, Token, TokenType
from src.ast import *

class ParserError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f'{message} at line {line}, column {column}')

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.prev_token = None
    
    def error(self, message: str):
        raise ParserError(
            message, 
            self.current_token.line if self.current_token else self.prev_token.line,
            self.current_token.column if self.current_token else self.prev_token.column
        )
    
    def eat(self, token_type: TokenType):
        """Verify the current token type and move to the next token."""
        if self.current_token.type == token_type:
            self.prev_token = self.current_token
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'Expected token {token_type}, got {self.current_token.type}')
    
    def program(self) -> Program:
        """program : PROGRAM variable SEMI block DOT"""
        token = self.current_token
        self.eat(TokenType.PROGRAM)
        
        prog_name = self.variable().value
        self.eat(TokenType.SEMI)
        
        block_node = self.block()
        program_node = Program(token, prog_name, block_node)
        self.eat(TokenType.DOT)
        
        return program_node
    
    def block(self) -> Block:
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(None, declaration_nodes, compound_statement_node)
        return node
    
    def declarations(self) -> List[VarDecl]:
        """declarations : VAR (variable_declaration SEMI)+ | empty"""
        declarations = []
        
        if self.current_token.type == TokenType.VAR:
            self.eat(TokenType.VAR)
            
            while self.current_token.type == TokenType.ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(TokenType.SEMI)
        
        return declarations
    
    def variable_declaration(self) -> List[VarDecl]:
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token, self.current_token.value)]
        self.eat(TokenType.ID)
        
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token, self.current_token.value))
            self.eat(TokenType.ID)
        
        self.eat(TokenType.COLON)
        
        type_node = self.type_spec()
        
        # Create a VarDecl node for each variable
        var_declarations = [
            VarDecl(
                token=var.token,
                var_node=var,
                type_node=type_node,
                type=type_node.type
            )
            for var in var_nodes
        ]
        
        return var_declarations
    
    def type_spec(self) -> TypeNode:
        """type_spec : INTEGER | FLOAT | array_type"""
        token = self.current_token
        
        if token.type == TokenType.ARRAY:
            return self.array_type()
        elif token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return TypeNode(token, Type.INTEGER)
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return TypeNode(token, Type.FLOAT)
        else:
            self.error(f'Expected type specifier (INTEGER, FLOAT, or ARRAY), got {token.type}')
    
    def array_type(self) -> TypeNode:
        """array_type : ARRAY LBRACKET NUMBER DOTDOT NUMBER RBRACKET OF type_spec"""
        token = self.current_token
        self.eat(TokenType.ARRAY)
        self.eat(TokenType.LBRACK)
        
        start_index = self.current_token.value
        self.eat(TokenType.INT_CONST)
        
        self.eat(TokenType.DOTDOT)
        
        end_index = self.current_token.value
        self.eat(TokenType.INT_CONST)
        
        self.eat(TokenType.RBRACK)
        self.eat(TokenType.OF)
        
        element_type = self.type_spec()
        
        return TypeNode(
            token=token,
            type=Type.ARRAY,
            start_index=start_index,
            end_index=end_index,
            element_type=element_type
        )
    
    def compound_statement(self) -> Compound:
        """compound_statement : BEGIN statement_list END"""
        token = self.current_token
        self.eat(TokenType.BEGIN)
        
        nodes = self.statement_list()
        
        self.eat(TokenType.END)
        
        root = Compound(token)
        root.children = nodes
        
        return root
    
    def statement_list(self) -> List[ASTNode]:
        """statement_list : statement | statement SEMI statement_list"""
        node = self.statement()
        
        results = [node]
        
        while self.current_token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            results.append(self.statement())
        
        return results
    
    def statement(self) -> ASTNode:
        """
        statement : compound_statement
                 | assignment_statement
                 | if_statement
                 | while_statement
                 | read_statement
                 | write_statement
                 | empty
        """
        if self.current_token.type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == TokenType.READ:
            node = self.read_statement()
        elif self.current_token.type == TokenType.WRITE:
            node = self.write_statement()
        elif self.current_token.type == TokenType.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        
        return node
    
    def assignment_statement(self) -> Assign:
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        node = Assign(left=left, op=token, right=right)
        return node
    
    def if_statement(self) -> If:
        """if_statement : IF expr THEN statement (ELSE statement)?"""
        token = self.current_token
        self.eat(TokenType.IF)
        
        condition = self.expr()
        
        self.eat(TokenType.THEN)
        true_branch = self.statement()
        
        false_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            false_branch = self.statement()
        
        return If(token, condition, true_branch, false_branch)
    
    def while_statement(self) -> While:
        """while_statement : WHILE expr DO statement"""
        token = self.current_token
        self.eat(TokenType.WHILE)
        
        condition = self.expr()
        
        self.eat(TokenType.DO)
        body = self.statement()
        
        return While(token, condition, body)
    
    def read_statement(self) -> Read:
        """read_statement : READ LPAREN variable RPAREN"""
        token = self.current_token
        self.eat(TokenType.READ)
        
        self.eat(TokenType.LPAREN)
        var_node = self.variable()
        self.eat(TokenType.RPAREN)
        
        return Read(token, var_node)
    
    def write_statement(self) -> Write:
        """write_statement : WRITE LPAREN (expr | string) RPAREN"""
        token = self.current_token
        self.eat(TokenType.WRITE)
        
        self.eat(TokenType.LPAREN)
        
        # Check if it's a string literal
        if self.current_token.type == TokenType.STRING:
            node = String(self.current_token, self.current_token.value)
            self.eat(TokenType.STRING)
        else:
            node = self.expr()
        
        self.eat(TokenType.RPAREN)
        
        return Write(token, node)
    
    def variable(self) -> Var:
        """variable : ID (LBRACKET expr RBRACKET)?"""
        node = Var(self.current_token, self.current_token.value)
        self.eat(TokenType.ID)
        
        # Check for array access
        if self.current_token.type == TokenType.LBRACK:
            self.eat(TokenType.LBRACK)
            index = self.expr()
            self.eat(TokenType.RBRACK)
            node.index = index
        
        return node
    
    def empty(self) -> 'NoOp':
        """An empty production"""
        return NoOp(Token(TokenType.EOF, None))
    
    def expr(self) -> ASTNode:
        """
        expr : logical_or_expr
        """
        return self.logical_or_expr()
    
    def logical_or_expr(self) -> ASTNode:
        """logical_or_expr : logical_and_expr (OR logical_and_expr)*"""
        node = self.logical_and_expr()
        
        while self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)
            node = BinOp(left=node, op=token, right=self.logical_and_expr())
        
        return node
    
    def logical_and_expr(self) -> ASTNode:
        """logical_and_expr : equality_expr (AND equality_expr)*"""
        node = self.equality_expr()
        
        while self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)
            node = BinOp(left=node, op=token, right=self.equality_expr())
        
        return node
    
    def equality_expr(self) -> ASTNode:
        """equality_expr : relational_expr ((EQUAL | NOT_EQUAL) relational_expr)*"""
        node = self.relational_expr()
        
        while self.current_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL):
            token = self.current_token
            
            if token.type == TokenType.EQUAL:
                self.eat(TokenType.EQUAL)
            elif token.type == TokenType.NOT_EQUAL:
                self.eat(TokenType.NOT_EQUAL)
            
            node = BinOp(left=node, op=token, right=self.relational_expr())
        
        return node
    
    def relational_expr(self) -> ASTNode:
        """
        relational_expr : add_expr ((LESS | LESS_EQUAL | GREATER | GREATER_EQUAL) add_expr)*
        """
        node = self.add_expr()
        
        while self.current_token.type in (
            TokenType.LESS, 
            TokenType.LESS_EQUAL, 
            TokenType.GREATER, 
            TokenType.GREATER_EQUAL
        ):
            token = self.current_token
            
            if token.type == TokenType.LESS:
                self.eat(TokenType.LESS)
            elif token.type == TokenType.LESS_EQUAL:
                self.eat(TokenType.LESS_EQUAL)
            elif token.type == TokenType.GREATER:
                self.eat(TokenType.GREATER)
            elif token.type == TokenType.GREATER_EQUAL:
                self.eat(TokenType.GREATER_EQUAL)
            
            node = BinOp(left=node, op=token, right=self.add_expr())
        
        return node
    
    def add_expr(self) -> ASTNode:
        """add_expr : mul_expr ((PLUS | MINUS) mul_expr)*"""
        node = self.mul_expr()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            
            node = BinOp(left=node, op=token, right=self.mul_expr())
        
        return node
    
    def mul_expr(self) -> ASTNode:
        """mul_expr : factor ((MULTIPLY | DIVIDE | MOD) factor)*"""
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            token = self.current_token
            
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            elif token.type == TokenType.MOD:
                self.eat(TokenType.MOD)
            
            node = BinOp(left=node, op=token, right=self.factor())
        
        return node
    
    def factor(self) -> ASTNode:
        """
        factor : PLUS factor
              | MINUS factor
              | NOT factor
              | INTEGER_CONST
              | FLOAT_CONST
              | LPAREN expr RPAREN
              | FLOAT LPAREN expr RPAREN
              | INT LPAREN expr RPAREN
              | variable
        """
        token = self.current_token
        
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.INT_CONST:
            self.eat(TokenType.INT_CONST)
            return Num(token, token.value)
        elif token.type == TokenType.FLOAT_CONST:
            self.eat(TokenType.FLOAT_CONST)
            return Num(token, token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.ID and token.value.upper() == 'FLOAT':
            self.eat(TokenType.ID)
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return FloatCast(token, expr)
        elif token.type == TokenType.ID and token.value.upper() == 'INT':
            self.eat(TokenType.ID)
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return IntCast(token, expr)
        else:
            return self.variable()
    
    def parse(self) -> ASTNode:
        """Parse the input program."""
        node = self.program()
        
        if self.current_token.type != TokenType.EOF:
            self.error('Unexpected token after program end')
        
        return node

def parse(text: str) -> ASTNode:
    lexer = Lexer(text)
    parser = Parser(lexer)
    return parser.parse()
