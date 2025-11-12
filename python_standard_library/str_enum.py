from enum import StrEnum
from typing import Any


# 1. Define a StrEnum
class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# 2. A function that expects a Color (not just any string)
def paint(color: Color) -> str:
    return f"Painting the wall {color.upper()}!"


# 3. Parsing strings safely to Color
def parse_color(value: str) -> Color:
    try:
        # This will automatically validate and return the Color member
        return Color(value)
    except ValueError:
        raise ValueError(f"Invalid color '{value}'. Must be one of: {[c.value for c in Color]}")


# 4. Example usage
if __name__ == "__main__":
    # ✅ Works with valid strings
    c1 = parse_color("red")
    print(paint(c1))  # → Painting the wall RED!

    # ✅ Works directly with enum members
    print(paint(Color.BLUE))  # → Painting the wall BLUE!

    # ❌ Raises an error for invalid strings
    try:
        c2 = parse_color("yellow")
        print(paint(c2))
    except ValueError as e:
        print(e)
