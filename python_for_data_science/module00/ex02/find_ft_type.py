def conv_upper(type_name):
    if (type_name):
        first_char = type_name[0]
        if ('a' <= first_char <= 'z'):
            first_char = chr(ord(first_char) - (ord('a') - ord('A')))
        capitalized_type_name = first_char + type_name[1:]
    else:
        capitalized_type_name = type_name
    return capitalized_type_name


def all_thing_is_obj(object: any) -> int:
    type_list = [list, tuple, set, dict]

    if (object.__class__ in type_list):
        print(f'{conv_upper(object.__class__.__name__)}: {object.__class__}')
    elif (object.__class__ == str):
        print(f'{object} is in the kitchen : {object.__class__}')
    else:
        print('Type not found')
    return 42
