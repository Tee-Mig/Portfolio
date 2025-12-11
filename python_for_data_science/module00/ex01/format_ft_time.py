from time import time
from datetime import datetime


def get_number_part(number, number_part):
    for i in range(len(number)):
        if (number[i] == '.'):
            return number[i:] if (number_part == 'fractional') else number[0:i]


def convert_to_number_with_coma(integer_part, fractional_part):
    integer_part = integer_part[::-1]
    time_with_coma = ''
    for i in range(0, len(integer_part), 3):
        if (i > 0):
            time_with_coma += ','
        time_with_coma += integer_part[i:i + 3]
    time_with_coma = time_with_coma[::-1]
    return (time_with_coma + fractional_part)


def ft_round(number):
    scaled_number = number * 100
    truncated_number = int(scaled_number)
    if (scaled_number - truncated_number >= 0.5):
        truncated_number += 1
    return (truncated_number / 100)


def convert_to_scientific_notation(str_time):
    exponent = 0
    float_time = float(str_time)
    while (float_time > 10):
        float_time /= 10
        exponent += 1
    exponent = ('0' + str(exponent)) if (exponent < 10) else str(exponent)
    return (str(ft_round(float_time)) + 'e+' + exponent)


def convert_int_month_to_string(month_number):
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ]

    if (1 <= month_number <= 12):
        return months[month_number]
    else:
        return "Invalid month"


def ft_time():
    str_time = str(time())
    integer_part = get_number_part(str_time, 'integer')
    fractional_part = get_number_part(str_time, 'fractional')
    time_with_coma = convert_to_number_with_coma(integer_part, fractional_part)
    scientific_notation = convert_to_scientific_notation(str_time)

    print(f'Seconds since January 1, 1970: {time_with_coma}', end='')
    print(f' or {scientific_notation} in scientific notation')

    month = convert_int_month_to_string(datetime.now().month - 1)
    print(f'{month} {datetime.now().day} {datetime.now().year}')
    return 0


ft_time()
