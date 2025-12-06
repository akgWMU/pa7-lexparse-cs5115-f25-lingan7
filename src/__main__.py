import sys
import traceback
from src.interpreter import interpret, InterpreterError
from src.parser import parse
from src.lexer import Lexer, TokenType

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m src.interpreter <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        print(f"Running {input_file}...")
        print("=" * 50)
        
        with open(input_file, 'r') as f:
            text = f.read()
            print("Source code:")
            print(text)
            print("=" * 50)
        
        # Initialize lexer and parser
        lexer = Lexer(text)
        ast = parse(lexer)
        
        # Run the interpreter
        result = interpret(ast)
        
        # Ensure we end with a newline
        print("\n" + "=" * 50)
        print("Program completed successfully")
        return 0
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        return 1
    except InterpreterError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        # Ensure all output is flushed
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == '__main__':
    sys.exit(main())
