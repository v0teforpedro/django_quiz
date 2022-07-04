from django import template

register = template.Library()


# filter
def negative_value(value):
    return -value


# filter
def multiply(value, arg):
    return value * arg


# filter
def divide(value, arg):
    return value // arg


# tag
def expression(value, *args):
    for idx, arg in enumerate(args, 1):
        value = value.replace(f'%{idx}', str(arg))
    return eval(value)

# {% expression '(%1 - 1) * 100 // %2' 23 56 as progress_level %}


"""
    args = (23, 56)
    1 23
    2 56
    '(23 - 1) * 100 // 56'
"""

register.filter('negative', negative_value)
register.filter('multiply', multiply)
register.filter('divide', divide)
register.simple_tag(func=expression, name='expression')