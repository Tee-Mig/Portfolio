from NULL_not_found import NULL_not_found


def ft_tester():
    Nothing = None
    Garlic = float("NaN")
    Zero = 0
    Empty = ''
    Fake = False

    NULL_not_found(Nothing)
    NULL_not_found(Garlic)
    NULL_not_found(Zero)
    NULL_not_found(Empty)
    NULL_not_found(Fake)
    print(NULL_not_found("Brian"))
    return 0


ft_tester()
