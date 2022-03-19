import re
import json


def translate(clauses):
    structure = {
        'if': None,
        'then': None,
        'until': None,
    }
    str_if = ''
    str_then = ''
    str_until = ''

    conj_iteration = 0
    conj = clauses['conjunctions']
    for clause, cond, signal, comp_symbol, param in zip(clauses['clauses'], clauses['conditions'],
                                                            clauses['signals'],
                                                            clauses['comp_symbol'], clauses['parameters']):

        if cond == 'until':
            if conj_iteration != 0:
                c = conj[conj_iteration - 1]
                if c != '':
                    str_until += ' ' + c + ' '

            str_until += signal['name'] + ' ' + comp_symbol + ' ' + param

        elif cond != '':
            if conj_iteration != 0:
                c = conj[conj_iteration - 1]
                if c != '':
                    str_if += ' ' + c + ' '

            str_if += signal['name'] + ' ' + comp_symbol + ' ' + param

        else:
            if conj_iteration != 0:
                c = conj[conj_iteration - 1]
                if c != '':
                    str_then += ' ' + c + ' '
            str_then += signal['name'] + ' ' + comp_symbol + ' ' + param

        conj_iteration += 1

    if str_if != '':
        str_if = str_if.lstrip(' ')
        str_if = str_if.rstrip(' ')
        structure['if'] = str_if
    if str_then != '':
        str_then = str_then.lstrip(' ')
        str_then = str_then.rstrip(' ')
        structure['then'] = str_then
    if str_until != '':
        str_until = str_until.lstrip(' ')
        str_until = str_until.rstrip(' ')
        structure['until'] = str_until

    return structure
