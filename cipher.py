"""Encrypt, decrypt, and verify the contents of a text file."""

ORIGINAL_FILE = "raw_text.txt"
ENCRYPTED_FILE = "encrypted_text.txt"
DECRYPTED_FILE = "decrypted_text.txt"

LOWERCASE_A_TO_N_SIZE = 14
LOWERCASE_O_TO_Z_SIZE = 12
UPPERCASE_GROUP_SIZE = 13
DIGIT_GROUP_SIZE = 10


def shift_within_range(character, range_start, range_size, shift_amount):
    """Shift one character while keeping it within its assigned range."""

    current_position = ord(character) - ord(range_start)
    new_position = (current_position + shift_amount) % range_size

    return chr(ord(range_start) + new_position)


def transform_character(character, shift1, shift2, decrypt=False):
    """Encrypt or decrypt one character using the appropriate rule."""

    direction = 1

    # Decryption reverses the direction of every encryption shift.
    if decrypt:
        direction = -1

    if "a" <= character <= "n":
        shift_amount = shift1 * shift2
        return shift_within_range(
            character,
            "a",
            LOWERCASE_A_TO_N_SIZE,
            direction * shift_amount,
        )

    if "o" <= character <= "z":
        shift_amount = -(shift1 + shift2)
        return shift_within_range(
            character,
            "o",
            LOWERCASE_O_TO_Z_SIZE,
            direction * shift_amount,
        )

    if "A" <= character <= "M":
        shift_amount = -shift1
        return shift_within_range(
            character,
            "A",
            UPPERCASE_GROUP_SIZE,
            direction * shift_amount,
        )

    if "N" <= character <= "Z":
        shift_amount = shift2**2
        return shift_within_range(
            character,
            "N",
            UPPERCASE_GROUP_SIZE,
            direction * shift_amount,
        )

    if "0" <= character <= "9":
        shift_amount = shift1 - shift2
        return shift_within_range(
            character,
            "0",
            DIGIT_GROUP_SIZE,
            direction * shift_amount,
        )

    # Spaces, punctuation, line breaks, and symbols remain unchanged.
    return character


def encrypt_file(
    shift1: int,
    shift2: int,
    input_path: str,
    output_path: str,
) -> None:
    """Read a text file, encrypt its contents, and save the result."""

    with open(input_path, "r", encoding="utf-8") as input_file:
        original_text = input_file.read()

    encrypted_characters = []

    for character in original_text:
        encrypted_character = transform_character(character, shift1, shift2)
        encrypted_characters.append(encrypted_character)

    encrypted_text = "".join(encrypted_characters)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(encrypted_text)


def decrypt_file(
    shift1: int,
    shift2: int,
    input_path: str,
    output_path: str,
) -> None:
    """Read an encrypted file, decrypt it, and save the result."""

    with open(input_path, "r", encoding="utf-8") as input_file:
        encrypted_text = input_file.read()

    decrypted_characters = []

    for character in encrypted_text:
        decrypted_character = transform_character(
            character,
            shift1,
            shift2,
            decrypt=True,
        )
        decrypted_characters.append(decrypted_character)

    decrypted_text = "".join(decrypted_characters)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(decrypted_text)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    """Return True when the original and decrypted files are identical."""

    with open(original_path, "r", encoding="utf-8") as original_file:
        original_text = original_file.read()

    with open(decrypted_path, "r", encoding="utf-8") as decrypted_file:
        decrypted_text = decrypted_file.read()

    return original_text == decrypted_text


def get_non_negative_integer(prompt):
    """Prompt repeatedly until the user enters a non-negative integer."""

    while True:
        entered_value = input(prompt).strip()

        if entered_value.isdigit():
            return int(entered_value)

        print("Invalid input. Please enter a non-negative integer.")


def main():
    """Run the encryption, decryption, and verification process."""

    print("----------------------------------------")
    print("        FILE ENCRYPTION PROGRAM")
    print("----------------------------------------")

    shift1 = get_non_negative_integer("Enter shift 1: ")
    shift2 = get_non_negative_integer("Enter shift 2: ")

    encrypt_file(shift1, shift2, ORIGINAL_FILE, ENCRYPTED_FILE)
    print("\nEncryption completed: encrypted_text.txt created.")

    decrypt_file(shift1, shift2, ENCRYPTED_FILE, DECRYPTED_FILE)
    print("Decryption completed: decrypted_text.txt created.")

    files_are_identical = verify_files(ORIGINAL_FILE, DECRYPTED_FILE)

    if files_are_identical:
        print(
            "Verification successful: the original and decrypted files "
            "are identical."
        )
    else:
        print(
            "Verification failed: the original and decrypted files "
            "are different."
        )

    print("----------------------------------------")


if __name__ == "__main__":
    main()
