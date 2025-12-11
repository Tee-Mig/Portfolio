def NULL_not_found(object: any) -> int:
    type_list = {
        'None': 'Nothing',
        'nan': 'Cheese',
        '0': 'Zero',
        '': 'Empty',
        'False': 'Fake'
    }

    key = str(object)
    if (key in type_list):
        print(f'{type_list[key]} : {object} {object.__class__}')
    else:
        print('Type not found')
        return 1
    return 0
