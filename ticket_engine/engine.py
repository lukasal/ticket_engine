# ticket_engine/engine.py

"""Provide several sample math calculations.

This module allows the user to make mathematical calculations.

Examples:
    >>> from calculator import calculations
    >>> calculations.add(2, 4)
    6.0
    >>> calculations.multiply(2.0, 4.0)
    8.0
    >>> from calculator.calculations import divide
    >>> divide(4.0, 2)
    2.0

The module contains the following functions:

- `add(a, b)` - Returns the sum of two numbers.
- `subtract(a, b)` - Returns the difference of two numbers.
- `multiply(a, b)` - Returns the product of two numbers.
- `divide(a, b)` - Returns the quotient of two numbers.
"""

def add(a: float | int, b: float | int) -> float:
    """Compute and return the sum of two numbers.

    Examples:
        >>> add(4.0, 2.0)
        6.0
        >>> add(4, 2)
        6.0

    Args:
        a: A number representing the first addend in the addition.
        b: A number representing the second addend in the addition.

    Returns:
        float: A number representing the arithmetic sum of `a` and `b`.
    """
    return float(a + b)

def subtract(a: float | int, b: float | int) -> float:
    """Compute and return the sum of two numbers.

    Args:
        a: A number representing the first addend.
        b: A number representing the number subtracted from the first.

    Returns:
        float: A number representing the difference of `a` and `b`.
    """
    return float(a - b)

def multiply(a: float | int, b: float | int) -> float:
    """Compute and return the sum of two numbers.

    Args:
        a: A number representing the first addend in the multiplication.
        b: A number representing the second addend in the multiplication.

    Returns:
        float: A number representing the multiplication of `a` and `b`.
    """
    return float(a * b)

def divide(a: float | int, b: float | int) -> float:
    """Compute and return the sum of two numbers.

    Args:
        a: A number to be divided.
        b: A number representing the divisor.

    Returns:
        float: A number representing the multiplication of `a` and `b`.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return float(a / b)