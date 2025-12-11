import sys


def number_is_even_or_odd():
    # assert len(sys.argv) == 2, 'more than one argument is provided'
    # assert int(sys.argv[1]), 'argument is not an integer'
    if (len(sys.argv) == 1):
        return
    if (len(sys.argv) > 2):
        print('AssertionError: more than one argument is provided')
        return
    try:
        int(sys.argv[1])
    except ValueError:
        print('AssertionError: argument is not an integer')
        return

    if (int(sys.argv[1]) % 2 == 0):
        print('I\'m Even.')
    else:
        print('I\'m Odd.')


number_is_even_or_odd()
