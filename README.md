# Pascal-like Language Interpreter

A complete implementation of a Pascal-like programming language with lexical analysis, parsing, and interpretation capabilities.

## Features

- **Lexical Analysis**: Tokenizes source code into meaningful tokens
- **Syntax Parsing**: Builds an Abstract Syntax Tree (AST) from tokens
- **Semantic Analysis**: Validates program structure and types
- **Interpreter**: Executes the parsed program
- **Standard Library**: Built-in functions for I/O and basic operations
- **Example Programs**: Collection of example programs in the `examples/` directory

## Language Features

- **Data Types**: Integer, Float, String, Boolean, Arrays
- **Control Flow**: If-Else, While loops
- **Functions**: User-defined functions with parameters and return values
- **I/O Operations**: Read from stdin, Write to stdout
- **Type Conversion**: Implicit and explicit type conversion
- **Arithmetic Operations**: Standard arithmetic with proper type promotion

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LexicalAnalyzer_Parser.git
   cd LexicalAnalyzer_Parser/pa7-lexparse-cs5115-f25-lingan7
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Programs

### Running the Interpreter

```bash
# Run a program
python -m src.interpreter examples/01_arithmetic.wm

# Run with unbuffered output (useful for debugging)
python -u -m src.interpreter examples/02_type_conversion.wm
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run a specific test file
python -m pytest tests/test_lexer.py -v
```

## Example Programs

The `examples/` directory contains several example programs that demonstrate the language's features:

1. **`01_arithmetic.wm`** - Demonstrates basic arithmetic operations:
   - Integer and float arithmetic
   - Operator precedence with parentheses
   - MOD operator usage
   - Comparison operations

2. **`02_type_conversion.wm`** - Shows type conversion between INTEGER and FLOAT:
   - Explicit type casting with `FLOAT()` and `INT()`
   - Mixed-type arithmetic
   - Implicit type promotion
   - Division behavior with different types

3. **`03_control_flow.wm`** - Implements control structures:
   - WHILE loops for iteration
   - Nested loops
   - IF-THEN-ELSE conditions
   - Prime number generation
   - Factorial calculation

4. **`04_arrays.wm`** - Covers array operations:
   - 1D array initialization and manipulation
   - Array reversal algorithm
   - 2D matrix operations
   - Nested loops for multi-dimensional arrays
   - Element-wise operations

5. **`05_functions.wm`** - Demonstrates function capabilities:
   - Function definition and invocation
   - Parameter passing
   - Return values
   - Local variables
   - Nested function calls
   - Array parameters
   - Recursive function calls (factorial)
   - Prime number checking function
   - Array maximum finding function

### Example: Hello World

```pascal
PROGRAM Hello;
BEGIN
    WRITE('Hello, World!');
END.
```

## Project Structure

```
.
├── examples/           # Example programs
├── src/                # Source code
│   ├── __init__.py
│   ├── ast.py          # Abstract Syntax Tree nodes
│   ├── interpreter.py  # Interpreter implementation
│   ├── lexer.py        # Lexical analyzer
│   └── parser.py       # Parser implementation
└── tests/              # Test files
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
