from enum import Enum, auto
from typing import List, Optional, Union

class TokenType(Enum):    # Keywords
    PROGRAM = auto()
    VAR = auto()
    INTEGER = auto()
    FLOAT = auto()
    ARRAY = auto()
    OF = auto()
    BEGIN = auto()
    END = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    READ = auto()
    WRITE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Operators
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    ASSIGN = ':='
    EQUAL = '='
    NOT_EQUAL = '<>'
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    
    # Delimiters
    SEMI = ';'
    COMMA = ','
    COLON = ':'
    DOT = '.'
    LPAREN = '('
    RPAREN = ')'
    LBRACK = '['
    RBRACK = ']'
    DOTDOT = '..'
    
    # Literals
    ID = auto()
    INT_CONST = auto()
    FLOAT_CONST = auto()
    STRING = auto()
    
    # Special
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: Union[str, int, float] = None, line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)}, position={self.line}:{self.column})'
    
    __repr__ = __str__

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f'{message} at line {line}, column {column}')

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        self.keywords = {
            'PROGRAM': TokenType.PROGRAM,
            'VAR': TokenType.VAR,
            'INTEGER': TokenType.INTEGER,
            'FLOAT': TokenType.FLOAT,
            'ARRAY': TokenType.ARRAY,
            'OF': TokenType.OF,
            'BEGIN': TokenType.BEGIN,
            'END': TokenType.END,
            'IF': TokenType.IF,
            'THEN': TokenType.THEN,
            'ELSE': TokenType.ELSE,
            'WHILE': TokenType.WHILE,
            'DO': TokenType.DO,
            'READ': TokenType.READ,
            'WRITE': TokenType.WRITE,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
        }
    
    def error(self, message: str):
        raise LexerError(message, self.line, self.column)
    
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            self.column += 1
        else:
            self.current_char = None
    
    def peek(self) -> Optional[str]:
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char != '}' and self.current_char is not None:
            self.advance()
        if self.current_char == '}':
            self.advance()  # Skip the closing '}'
        else:
            self.error('Unterminated comment')
    
    def number(self) -> Token:
        result = ''
        is_float = False
        line, col = self.line, self.column
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            is_float = True
            result += self.current_char
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            
            if self.current_char in ('e', 'E'):
                result += self.current_char
                self.advance()
                
                if self.current_char in ('+', '-'):
                    result += self.current_char
                    self.advance()
                
                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()
        
        if is_float:
            return Token(TokenType.FLOAT_CONST, float(result), line, col)
        else:
            return Token(TokenType.INT_CONST, int(result), line, col)
    
    def string(self) -> Token:
        result = ''
        line, col = self.line, self.column
        self.advance()  # Skip the opening quote
        
        while self.current_char is not None and self.current_char != "'":
            result += self.current_char
            self.advance()
        
        if self.current_char != "'":
            self.error('Unterminated string')
        
        self.advance()  # Skip the closing quote
        return Token(TokenType.STRING, result, line, col)
    
    def _id(self) -> Token:
        result = ''
        line, col = self.line, self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        token_type = self.keywords.get(result.upper(), TokenType.ID)
        if token_type != TokenType.ID:
            return Token(token_type, result.upper(), line, col)
        return Token(token_type, result, line, col)
    
    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            
            if self.current_char == "'":
                return self.string()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            
            if self.current_char.isdigit():
                return self.number()
            
            # Multi-character operators
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.ASSIGN, ':=', self.line, self.column - 1)
            
            if self.current_char == '<' and self.peek() == '>':
                self.advance()
                self.advance()
                return Token(TokenType.NOT_EQUAL, '<>', self.line, self.column - 1)
            
            if self.current_char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.LESS_EQUAL, '<=', self.line, self.column - 1)
            
            if self.current_char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column - 1)
            
            if self.current_char == '.' and self.peek() == '.':
                self.advance()
                self.advance()
                return Token(TokenType.DOTDOT, '..', self.line, self.column - 1)
            
            # Single-character tokens
            try:
                token_type = TokenType(self.current_char)
                token = Token(token_type, self.current_char, self.line, self.column)
                self.advance()
                return token
            except ValueError:
                self.error(f'Unexpected character: {self.current_char}')
        
        return Token(TokenType.EOF, None, self.line, self.column)

def lex(text: str) -> List[Token]:
    lexer = Lexer(text)
    tokens = []
    while True:
        token = lexer.get_next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break
    return tokens
