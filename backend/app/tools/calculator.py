"""StartupOS AI — Calculator Tool (Safe Math Eval for Finance Agent)"""

import ast
import operator
import logging

logger = logging.getLogger(__name__)

# Safe operators for mathematical evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(expression: str) -> float:
    """Safely evaluate a mathematical expression.

    Only supports: +, -, *, /, ** and numbers.
    No access to builtins, imports, or dangerous operations.

    Args:
        expression: Math expression like "1499 * 12 * 0.37"

    Returns:
        Computed result as float
    """
    try:
        tree = ast.parse(expression, mode='eval')
        result = _eval_node(tree.body)
        logger.info(f"Calculator: {expression} = {result}")
        return float(result)
    except Exception as e:
        logger.error(f"Calculator error for '{expression}': {e}")
        raise ValueError(f"Cannot evaluate: {expression}")


def _eval_node(node):
    """Recursively evaluate an AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value}")
    elif isinstance(node, ast.BinOp):
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval_node(node.left), _eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    else:
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")
