import ast
import re

def run_function(function, args):
    return function(*args)

def lambda_eval(node_or_string):
    '''
        Safe evaluation of lambda functions from a file.
    '''
    # Check if method received a string and parse it into a node
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')

    # Check if the nnode is an expression an get its body
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body

    # Inline definition of the function convert
    def _convert(node):
        # Return the number if the node is an ast.Num
        if isinstance(node, ast.Num):
            return node.n

        # Return the name if the node is an ast.Name (limit to 3 chars)
        elif isinstance(node, ast.Name):
            if len(node.id) < 3:
                return node.id
            else:
                raise NameError(f'reduce {node.id} variable name')

        # Parse and return lambda names and body
        elif isinstance(node, ast.Lambda):
            arglist = [arg.arg for arg in node.args.args]
            for arg in arglist:
                if len(arg) > 3:
                    raise NameError(f'reduce {arg} variable name')
            arglist = re.sub('\[|\]|\'', '', str(arglist)) 
            body = _convert(node.body)
            safe_lambda = f'lambda {arglist}: {body}'
            return safe_lambda

        # Return the result of the unary operator
        elif isinstance(node, ast.UnaryOp) and \
             isinstance(node.op, (ast.UAdd, ast.USub)) and \
             isinstance(node.operand, (ast.Num, ast.Name, ast.UnaryOp, ast.BinOp)):
            operand = _convert(node.operand)
            
            # Check if operand is a number
            if isinstance(node.operand, ast.Num):
                number = True
            else:
                number = False

            # Check if the operation is unary add
            if isinstance(node.op, ast.UAdd):
                return + node.operand if number else f'(+ {operand})'
            # Chek if the operation is unary sub
            elif isinstance(node.op, ast.USub):
                return - node.operand if number else f'(- {operand})'

        # Return the result of the binary operator
        elif isinstance(node, ast.BinOp) and \
             isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)) and \
             isinstance(node.left, (ast.Num, ast.Name, ast.UnaryOp, ast.BinOp)) and \
             isinstance(node.right, (ast.Num, ast.Name, ast.UnaryOp, ast.BinOp)):
            # Convert left and right nodes recursively
            left = _convert(node.left)
            right = _convert(node.right)
            
            # Check if left and right nodes are integers
            if isinstance(left, int) and isinstance(right, int):
                numbers = True
            else:
                numbers = False

            # Check if operation is addition
            if isinstance(node.op, ast.Add):
                return left + right if numbers else f'({left} + {right})'
            
            # Check if operation is subtraction
            elif isinstance(node.op, ast.Sub):
                return left - right if numbers else f'({left} - {right})'

            # Check if operation is multiplication
            elif isinstance(node.op, ast.Mult):
                return left * right if numbers else f'({left} * {right})'

            # Check if operation is division
            elif isinstance(node.op, ast.Div):
                return left / right if numbers else f'({left} / {right})'

            # Check if operation is module
            elif isinstance(node.op, ast.Mod):
                return left % right if numbers else f'({left} % {right})'

            # Check if operation is power
            elif isinstance(node.op, ast.Pow):
                return left ** right if numbers else f'({left} ** {right})'
            
        raise ValueError(f'not valid consntruct: {node}')
    safe_lambda_str = _convert(node_or_string)
    return safe_lambda_str
