from ft_filter import ft_filter
import sys


def get_words_list(iterable):
    """
        get_words_list(iterable) --> separate iterable into list of words

        Return a list of words
    """
    word_list = []
    word = ''
    for char in iterable:
        if (char != ' '):
            word += char
        else:
            if (word):
                word_list.append(word)
                word = ''
    if word:
        word_list.append(word)
    return (word_list)


def contains_only_letters_and_digits(iterable):
    """
        contains_only_letters_and_digits(iterable) --> check if
        contains special characters

        Return a boolean value if the items in iterable contains
        special characters
    """
    for char in iterable:
        if not ('a' <= char <= 'z' or 'A' <= char <= 'Z'
                or '0' <= char <= '9' or char == ' '):
            return False
    return True


def main():

    if (len(sys.argv) == 1):
        return 0
    if (len(sys.argv) != 3):
        print('AssertionError: the arguments are bad')
        return 1
    else:
        try:
            iterable = str(sys.argv[1])
            if (contains_only_letters_and_digits(iterable) is False):
                raise ValueError('')
            condition = int(sys.argv[2])
        except ValueError:
            print('AssertionError: the arguments are bad')
            return

    worlds_arr = get_words_list(iterable)
    print(ft_filter(lambda world: len(world) > condition, worlds_arr))

    return 0


if __name__ == "__main__":
    main()
