"""Tokenise, parse, and evaluate mathematical expressions."""

import os


DEFAULT_INPUT_FILE = "input.txt"
OUTPUT_FILE_NAME = "output.txt"
ERROR = "ERROR"


def format_number(value):
    """Format a number using the output rules from the assignment."""

    rounded_value = round(value, 4)

    if rounded_value == int(rounded_value):
        return str(int(rounded_value))

    return str(rounded_value)


def tokenize(expression):
    """Convert an expression into a list of tokens."""

    tokens = []
    position = 0

    while position < len(expression):
        character = expression[position]

        # Spaces and tabs separate values but do not become tokens.
        if character == " " or character == "\t":
            position += 1

        elif character.isdigit():
            number_start = position

            while (
                position < len(expression)
                and expression[position].isdigit()
            ):
                position += 1

            # A decimal point is optional but must have digits after it.
            if (
                position < len(expression)
                and expression[position] == "."
            ):
                position += 1
                decimal_start = position

                while (
                    position < len(expression)
                    and expression[position].isdigit()
                ):
                    position += 1

                if position == decimal_start:
                    return None

            # Reject a second decimal point, such as in 1.2.3.
            if (
                position < len(expression)
                and expression[position] == "."
            ):
                return None

            number = expression[number_start:position]
            tokens.append(("NUM", number))

        elif character in "+-*/%^":
            tokens.append(("OP", character))
            position += 1

        elif character == "(":
            tokens.append(("LPAREN", character))
            position += 1

        elif character == ")":
            tokens.append(("RPAREN", character))
            position += 1

        else:
            return None

    tokens.append(("END", ""))

    return tokens


def format_tokens(tokens):
    """Convert a token list into the required output string."""

    formatted_tokens = []

    for token_type, token_value in tokens:
        if token_type == "END":
            formatted_tokens.append("[END]")
        else:
            formatted_tokens.append(f"[{token_type}:{token_value}]")

    return " ".join(formatted_tokens)


def parse_primary(tokens, position):
    """Parse a number or a parenthesised expression."""

    token_type, token_value = tokens[position]

    if token_type == "NUM":
        value = float(token_value)
        tree = format_number(value)
        return value, tree, position + 1

    if token_type == "LPAREN":
        value, tree, next_position = parse_expression(tokens, position + 1)

        if tree == ERROR or tokens[next_position][0] != "RPAREN":
            return None, ERROR, position

        return value, tree, next_position + 1

    return None, ERROR, position


def parse_power(tokens, position):
    """Parse right-associative exponentiation."""

    left_value, left_tree, next_position = parse_primary(tokens, position)

    if left_tree == ERROR:
        return None, ERROR, position

    if tokens[next_position] == ("OP", "^"):
        right_value, right_tree, final_position = parse_unary(
            tokens,
            next_position + 1,
        )

        if right_tree == ERROR:
            return None, ERROR, position

        tree = f"(^ {left_tree} {right_tree})"

        if left_value is None or right_value is None:
            value = None
        elif left_value == 0 and right_value < 0:
            value = None
        elif left_value < 0 and right_value % 1 != 0:
            value = None
        else:
            value = left_value**right_value

        return value, tree, final_position

    return left_value, left_tree, next_position


def parse_unary(tokens, position):
    """Parse unary negation and reject unary plus."""

    token_type, token_value = tokens[position]

    if token_type == "OP" and token_value == "-":
        value, tree, next_position = parse_unary(tokens, position + 1)

        if tree == ERROR:
            return None, ERROR, position

        if value is not None:
            value = -value

        return value, f"(neg {tree})", next_position

    if token_type == "OP" and token_value == "+":
        return None, ERROR, position

    return parse_power(tokens, position)


def parse_term(tokens, position):
    """Parse multiplication, division, modulo, and implicit multiplication."""

    left_value, left_tree, next_position = parse_unary(tokens, position)

    if left_tree == ERROR:
        return None, ERROR, position

    while True:
        token_type, token_value = tokens[next_position]
        operator_symbol = None
        right_position = next_position + 1

        if token_type == "OP" and token_value in "*/%":
            operator_symbol = token_value

        # Examples: 2(3 + 4) and (2 + 3)(4 + 5).
        elif token_type == "LPAREN":
            operator_symbol = "*"
            right_position = next_position

        # Example: (2 + 3)4. Two adjacent numbers remain invalid.
        elif (
            token_type == "NUM"
            and tokens[next_position - 1][0] == "RPAREN"
        ):
            operator_symbol = "*"
            right_position = next_position

        else:
            break

        right_value, right_tree, final_position = parse_unary(
            tokens,
            right_position,
        )

        if right_tree == ERROR:
            return None, ERROR, position

        left_tree = f"({operator_symbol} {left_tree} {right_tree})"

        if left_value is None or right_value is None:
            left_value = None
        elif operator_symbol == "*":
            left_value *= right_value
        elif operator_symbol == "/":
            if right_value == 0:
                left_value = None
            else:
                left_value /= right_value
        elif operator_symbol == "%":
            if right_value == 0:
                left_value = None
            else:
                left_value %= right_value

        next_position = final_position

    return left_value, left_tree, next_position


def parse_expression(tokens, position):
    """Parse left-associative addition and subtraction."""

    left_value, left_tree, next_position = parse_term(tokens, position)

    if left_tree == ERROR:
        return None, ERROR, position

    while (
        tokens[next_position][0] == "OP"
        and tokens[next_position][1] in "+-"
    ):
        operator_symbol = tokens[next_position][1]
        right_value, right_tree, final_position = parse_term(
            tokens,
            next_position + 1,
        )

        if right_tree == ERROR:
            return None, ERROR, position

        left_tree = f"({operator_symbol} {left_tree} {right_tree})"

        if left_value is None or right_value is None:
            left_value = None
        elif operator_symbol == "+":
            left_value += right_value
        else:
            left_value -= right_value

        next_position = final_position

    return left_value, left_tree, next_position


def evaluate_expression(expression):
    """Tokenise, parse, and evaluate one expression."""

    tokens = tokenize(expression)

    if tokens is None:
        return {
            "input": expression,
            "tree": ERROR,
            "tokens": ERROR,
            "result": ERROR,
        }

    token_text = format_tokens(tokens)
    value, tree, next_position = parse_expression(tokens, 0)

    if tree == ERROR or tokens[next_position][0] != "END":
        return {
            "input": expression,
            "tree": ERROR,
            "tokens": token_text,
            "result": ERROR,
        }

    if value is None:
        result = ERROR
    else:
        result = float(value)

    return {
        "input": expression,
        "tree": tree,
        "tokens": token_text,
        "result": result,
    }


def evaluate_file(input_path: str) -> list[dict]:
    """Evaluate each input line and write output.txt beside the input file."""

    results = []

    with open(input_path, "r", encoding="utf-8") as input_file:
        for line in input_file:
            # Remove only the line ending so other spacing remains unchanged.
            expression = line.rstrip("\r\n")
            results.append(evaluate_expression(expression))

    input_directory = os.path.dirname(input_path)
    output_path = os.path.join(input_directory, OUTPUT_FILE_NAME)
    output_blocks = []

    for result_record in results:
        result_value = result_record["result"]

        if result_value == ERROR:
            formatted_result = ERROR
        else:
            formatted_result = format_number(result_value)

        output_block = (
            f"Input: {result_record['input']}\n"
            f"Tree: {result_record['tree']}\n"
            f"Tokens: {result_record['tokens']}\n"
            f"Result: {formatted_result}"
        )
        output_blocks.append(output_block)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n\n".join(output_blocks))

        if output_blocks:
            output_file.write("\n")

    return results


def main():
    """Evaluate expressions from the default input file."""

    evaluate_file(DEFAULT_INPUT_FILE)


if __name__ == "__main__":
    main()