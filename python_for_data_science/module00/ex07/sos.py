import sys


def contains_only_letters_and_digits(iterable):
    """
        contains_only_letters_and_digits(iterable) --> check if
        contains special characters

        Return a boolean value if the items in iterable
        contains special characters
    """
    for char in iterable:
        if not ('a' <= char <= 'z' or 'A' <= char <= 'Z'
                or '0' <= char <= '9' or char == ' '):
            return False
    return True


def convert_to_uppercase(input):
    """
        convert_to_uppercase(char) -> convert lowercase character
        into uppercase character

        Return uppercase character
    """

    uppercase_string = ""

    for char in input:
        if 'a' <= char <= 'z':
            uppercase_char = chr(ord(char) - 32)
            uppercase_string += uppercase_char
        else:
            uppercase_string += char

    return (uppercase_string)


def main():
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..',

        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',

        ' ': '/ '
    }

    if (len(sys.argv) != 2):
        print('AssertionError: number of argument')
        return 1
    try:
        input_string = str(sys.argv[1])
    except ValueError:
        print('AssertionError: not convertible to string')
        return 1
    if (contains_only_letters_and_digits(input_string) is False):
        print('AssertionError: string does contain special characters')
        return 1

    input_string = convert_to_uppercase(input_string)

    morse_code = ''

    for i, char in enumerate(input_string):
        if (i != 0 and char != ' '):
            morse_code += ' '
        if char in morse_code_dict:
            morse_code += morse_code_dict[char]

    print(morse_code)

    return 0


if __name__ == "__main__":
    main()
