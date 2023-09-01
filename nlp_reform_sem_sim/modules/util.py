import math
import pandas as pd
import configparser
import pickle
import spacy
import json
import re
import spacy


def load_req_signals(path=r'data/input.xlsx'):
    """
    reads the input file and populate a list of requirements with necessary details.
    """

    file = pd.read_excel(path, sheet_name=[0, 1, 2])
    req_file = file[0]
    signals_file = file[1]
    parameters_file = file[2]
    signals_in = []
    signals_out = []
    for _, sig in signals_file.iterrows():
        try:
            s = {'name': sig['Signal Name'], 'data_type': sig['Data type'], 'desc': sig['Signal Desc']}
            if sig['Direction'] == 'incoming':
                signals_in.append(s)
            else:
                signals_out.append(s)
        except:
            raise Exception("Please check if the 'Signals' sheet have the "
                            "correct headers.")

    parameters = []
    for _, param in parameters_file.iterrows():
        try:
            p = {'name': param['Parameter Name'], 'data_type': param['Data Type'], 'value': param['Value'], 'desc': param['Parameter Description']}
            parameters.append(p)
        except:
            raise Exception("Please check if the 'Parameters' sheet have the "
                            "correct headers.")

    req_list = []
    for _, row in req_file.iterrows():
        if math.isnan(row['Req ID']):
            continue
        try:
            req = {'req_id': row['Req ID'], 'linked_item': row['Linked Item'], 'req_desc': row['Requirement'],
                   'output': row['Formalized Requirement']}
            req_list.append(req)
        except:
            req = {'req_id': row['Req ID'], 'linked_item': row['Linked Item'], 'req_desc': row['Requirement']}
            req_list.append(req)
        else:
            raise Exception("Please check if the 'Requirements' sheet have the "
                            "correct headers.")

    return req_list, signals_in, signals_out, parameters


def read_config(path='data/config.ini'):
    """
    reads the config file and populates values for different detection techniques.
    """
    config = configparser.ConfigParser()
    config.read(path)
    params = {
        'signal_detection': config['config']['signal_detection'],
        'param_detection': config['config']['param_detection'],
        'method': config['config']['method'],
    }

    return params


def convert_text_to_json(text):
    if_text = None
    then_text = None
    until_text = None
    result_if = re.search(r"if\((.*)\)", text)
    result_then = re.search(r"then\((.*?)\)", text)
    result_until = re.search(r"until\((.*?)\)", text)
    if result_if:
        if_text = result_if.group(1)
        if_text = if_text.lstrip(' ')
        if_text = if_text.rstrip(' ')
    if result_then:
        then_text = result_then.group(1)
        then_text = then_text.lstrip(' ')
        then_text = then_text.rstrip(' ')
    if result_until:
        until_text = result_until.group(1)
        until_text = until_text.lstrip(' ')
        until_text = until_text.rstrip(' ')
    code = {
        'if': if_text,
        'then': then_text,
        'until': until_text
    }
    return code


def convert_json_to_text(code):
    text = ''
    if code['if']:
        text += 'if(' + code['if'] + ')\n'
    if code['then']:
        text += 'then(' + code['then'] + ')\n'
    if code['until']:
        text += 'until(' + code['until'] + ')'

    return text


def save_results(req_results, method, file_name='data/output.xlsx'):
    result_sht1 = []
    result_sht2 = []
    for req in req_results:
        result_sht1.append([req['req_id'], req['req_desc'], convert_json_to_text(req['output'])])
        if method == 'Pipeline' or method == 'Parameter':
            columns2 = ['Req ID', 'Clause', 'Signal Name', 'Signal Desc', 'Comparison Symbol',
                        'Parameter']
            for clause, signal, cs, param in zip(req['clauses'], req['signals'], req['comp_symbol'], req['parameters']):
                if cs == '=':
                    cs = "'="
                result_sht2.append([req['req_id'], clause, signal['name'], signal['desc'], cs, param])
        elif method == 'Decomposition':
            columns2 = ['Req ID', 'Clause']
            for clause in req['clauses']:
                result_sht2.append([req['req_id'], clause])
        elif method == 'Signal':
            columns2 = ['Req ID', 'Clause', 'Signal Name', 'Signal Desc']
            for clause, signal in zip(req['clauses'], req['signals']):
                result_sht2.append([req['req_id'], clause, signal['name'], signal['desc']])

    df_1 = pd.DataFrame(result_sht1, columns=['Req ID', 'Req Desc', 'Generated Output'])
    df_2 = pd.DataFrame(result_sht2, columns=columns2)

    with pd.ExcelWriter(file_name) as writer1:
        df_1.to_excel(writer1, sheet_name='Requirements-Output', index=False, columns=['Req ID', 'Req Desc',
                                                                                       'Generated Output'])
        df_2.to_excel(writer1, sheet_name='Step-By-Step', index=False, columns=columns2)
