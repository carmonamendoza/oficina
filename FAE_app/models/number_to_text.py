# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

unidades = (
    '',
    'un ',
    'dos ',
    'tres ',
    'cuatro ',
    'cinco ',
    'seis ',
    'siete ',
    'ocho ',
    'nueve ',
    'diez ',
    'once ',
    'doce ',
    'trece ',
    'catorce ',
    'quince ',
    'dieciseis ',
    'diecisiete ',
    'dieciocho ',
    'diecinueve ',
    'veinte '
)

decenas = (
    '',
    '#diez',
    'venti',
    'treinta ',
    'cuarenta ',
    'cincuenta ',
    'sesenta ',
    'setenta ',
    'ochenta ',
    'noventa ',
    'cien ',
)

centenas = (
    '',
    'ciento ',
    'doscientos ',
    'trescientos ',
    'cuatrocientos ',
    'quinientos ',
    'seiscientos ',
    'setecientos ',
    'ochocientos ',
    'novecientos ',
)


def number_to_text(value, decimal_digits=2):
    """ Devuelve el value en letras
    """
    result = ''

    if isinstance(value, str):
        num_value = float(value)
    else:
        num_value = value
    
    if num_value < 0:
        num_value = abs(num_value)

    # separa la parte entera de la parte decimal
    enteros = int(num_value)
    decimales = 0 if decimal_digits <= 0 else int( str(num_value - enteros)[2:2+decimal_digits] )

    # obtiene grupos de valores
    millones = int(enteros / 1000000)
    resto = int(enteros % 1000000)

    # conversion
    if millones == 1:
        result += 'un millón '
    elif millones > 1:
        result += '%s millones ' % _miles(millones, 2).rstrip()

    if resto > 0:
        result += _miles(resto, 1).rstrip()

    if decimal_digits == 0:
        result = '%s' % result.rstrip()
    elif decimales == 0:
        result = '%s exactos' % result.rstrip()
    else:
        result = '%s con %s/100' % (result.rstrip(), str(decimales))
    return result


def _miles(n, grupo):
    result = ''
    if n <= 999:
        result = _cientos(n, grupo)
    else:
        # mil o más 
        m = int(n / 1000)
        c = int(n % 1000)
        if m == 1:
            result = 'un mil' if c == 0 else 'un mil ' + _cientos(c, grupo)
        elif c == 0:
            result = _cientos(m, grupo) + 'mil'
        else:
            result = _cientos(m, grupo) + 'mil ' + _cientos(c, grupo)
    return result


def _cientos(n, grupo):
    result = ''
    if n == 100:
        result = 'cien '
    else:
        result = centenas[int(n/100)]
        d = int(n % 100)
        x = int(d / 10)
        u = int(d % 10)
        if grupo == 1 and d == 1:
            result += 'uno '
        elif d <= 20:
            result += unidades[d]
        elif grupo == 1 and x >= 2 and u == 1:
            result += '%s y uno' % decenas[x].rstrip()
        elif d < 30 or (x >= 3 and u == 0):
            result += '%s%s' % (decenas[x], unidades[u])
        else:
            result += '%s y %s' % (decenas[x].rstrip(), unidades[u])
    return result
