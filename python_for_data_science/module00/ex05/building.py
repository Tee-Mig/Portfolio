import sys


def count_different_characters_types(input_string):
    """
        count_different_characters_types(input_string) --> count the number
        of caracters, uppercase letter, lowercase letter, punctuation,
        space and digit

        Return the number of caracters, uppercase letter, lowercase letter,
        punctuation, space and digit
    """
    punctuation = '.,!?;:\'"-()[]{}'
    upper_count = 0
    lower_count = 0
    punctuation_count = 0
    space_count = 0
    digit_count = 0

    input_string = input_string.replace('\n', '')
    input_string = input_string.replace('\r', ' ')

    for char in input_string:
        if char.isupper():
            upper_count += 1
        elif char.islower():
            lower_count += 1
        elif char in punctuation:
            punctuation_count += 1
        elif char.isspace():
            space_count += 1
        elif char.isdigit():
            digit_count += 1

    print(f'The text contains {len(input_string)} characters:')
    print(f'Uppercase letters: {upper_count}')
    print(f'Lowercase letters: {lower_count}')
    print(f'Punctuation marks: {punctuation_count}')
    print(f'Spaces: {space_count}')
    print(f'Digits: {digit_count}')


def main():
    if (sys.argv is None or len(sys.argv) == 1):
        print('What is the text to count?')
        user_input = sys.stdin.readline()
        user_input = user_input.replace('\n', ' ')
    else:
        if (len(sys.argv) > 2):
            print('AssertionError: more than one argument is provided')
            return 1
        try:
            user_input = str(sys.argv[1])
        except ValueError:
            print('AssertionError: not convertible to string')
            return 1

    count_different_characters_types(user_input)

    return 0


if __name__ == "__main__":
    main()
