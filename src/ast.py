from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union, Dict, Any

class Type(Enum):
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    ARRAY = 'ARRAY'
    VOID = 'VOID'

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    token: Any
    line: int = 0
    column: int = 0

@dataclass
class Program(ASTNode):
    """Represents a program."""
    name: str
    block: 'Block'

@dataclass
class Block(ASTNode):
    """Represents a block of declarations and compound statement."""
    declarations: List['VarDecl']
    compound_statement: 'Compound'

@dataclass
class VarDecl(ASTNode):
    """Represents a variable declaration."""
    var_node: 'Var'
    type_node: 'TypeNode'
    type: Optional[Type] = None

@dataclass
class TypeNode(ASTNode):
    """Represents a type (INTEGER, FLOAT, or ARRAY)."""
    token: Any
    type: Type
    start_index: Optional[int] = None  # For arrays
    end_index: Optional[int] = None    # For arrays
    element_type: Optional['TypeNode'] = None  # For arrays

@dataclass
class Param(ASTNode):
    """Represents a formal parameter."""
    var_node: 'Var'
    type_node: 'TypeNode'

@dataclass
class Compound(ASTNode):
    """Represents a compound statement (BEGIN ... END)."""
    children: List[ASTNode]

@dataclass
class Assign(ASTNode):
    """Represents an assignment statement."""
    left: 'Var'
    op: Any
    right: 'ASTNode'

@dataclass
class Var(ASTNode):
    """Represents a variable."""
    value: str
    index: Optional['ASTNode'] = None  # For array access
    type: Optional[Type] = None

@dataclass
class NoOp(ASTNode):
    """Represents an empty statement."""
    pass

@dataclass
class BinOp(ASTNode):
    """Represents a binary operation."""
    left: ASTNode
    op: Any
    right: ASTNode
    type: Optional[Type] = None

@dataclass
class UnaryOp(ASTNode):
    """Represents a unary operation."""
    op: Any
    expr: 'ASTNode'
    type: Optional[Type] = None

@dataclass
class Num(ASTNode):
    """Represents a number (integer or float)."""
    value: Union[int, float]
    type: Type

@dataclass
class String(ASTNode):
    """Represents a string literal."""
    value: str

@dataclass
class If(ASTNode):
    """Represents an IF statement."""
    condition: ASTNode
    true_branch: ASTNode
    false_branch: Optional[ASTNode]

@dataclass
class While(ASTNode):
    """Represents a WHILE loop."""
    condition: ASTNode
    body: ASTNode

@dataclass
class Read(ASTNode):
    """Represents a READ statement."""
    var: Var

@dataclass
class Write(ASTNode):
    """Represents a WRITE statement."""
    expr: ASTNode

class NodeVisitor:
    """Base class for AST visitors."""
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')
