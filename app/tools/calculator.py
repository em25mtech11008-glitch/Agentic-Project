from langchain_core.tools import tool

# CONCEPT:
# The @tool decorator converts a normal Python function into a LangChain Tool object.
# The tool's docstring and argument type hints are CRITICAL:
# LangChain extracts them and sends them to the LLM as the tool's description and schema.
# This is how the LLM understands:
# 1. What the tool does (from the docstring)
# 2. When to call it
# 3. What arguments it expects (from the type hints and docstring)

@tool
def add(a: float, b: float) -> float:
    """
    Adds two numbers together.
    Use this tool when the user asks to add or sum numbers.
    """
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """
    Subtracts number b from number a (returns a - b).
    Use this tool when the user asks to subtract or find the difference between numbers.
    """
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers.
    Use this tool when the user asks to multiply or find the product of numbers.
    """
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """
    Divides number a by number b (returns a / b).
    Use this tool when the user asks to divide or find the ratio of numbers.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
