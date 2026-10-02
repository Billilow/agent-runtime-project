import ast
import operator

class ToolExecutionError(Exception):
    pass

def evaluate(node):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left_value = evaluate(node.left)
        right_value = evaluate(node.right)

        if isinstance(node.op, ast.Add):
            return left_value + right_value
        elif isinstance(node.op, ast.Sub):
            return left_value - right_value
        elif isinstance(node.op, ast.Mult):
            return left_value * right_value
        elif isinstance(node.op, ast.Div):
            return left_value / right_value

def calculator(expression: str) -> dict:
    try:
        parsed = ast.parse(expression, mode='eval')
        resul = evaluate(parsed.body)
    except ZeroDivisionError as e:
        raise ToolExecutionError("Can't divide number to 0")
    except TypeError as e:
        raise ToolExecutionError("This type cannot be calculated")
    except SyntaxError as e:
        raise ToolExecutionError("Invalid Syntax")
    except Exception as e:
        raise ToolExecutionError("There is an error.")

    return {'expression': expression, 'result': resul}


# Tool_Schema = {
#     "name": "calculator_tool",
#     "description": "You can use this when calculating "
#                    "addition, subtraction, multiplication and division, including parenthesis.",
#     "input_schema": {
#         "type": "object",
#         "properties": {
#             "expression": {"type": "string", "description": "operations that you want to calculate"}
#         },
#         "required": ["expression"]
#     }
# }

calculator_declaration = {
    "name": "calculator_tool",
    "description": "You can use this when calculating "
                   "addition, subtraction, multiplication and division, including parenthesis.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "operations that you want to calculate"}
        },
        "required": ["expression"]
    }
}


if __name__ == '__main__':
    if __name__ == '__main__':
        print(calculator("2 + 3 * 4"))  # 정상 -> {'expression': ..., 'result': 14}

        try:
            calculator("1/0")
        except ToolExecutionError as e:
            print("ERROR CAUGHT:", e)  # Can't divide number to 0

        try:
            calculator("hello + 1")
        except ToolExecutionError as e:
            print("ERROR CAUGHT:", e)  # This type cannot be calculated

        try:
            calculator("2 + ")
        except ToolExecutionError as e:
            print("ERROR CAUGHT:", e)  # Invalid Syntax
