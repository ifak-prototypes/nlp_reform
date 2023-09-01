import math
import pandas as pd
import configparser
import pickle
import json


def load_req(path=r'data/input/req_Bombardier_temp.csv'):
    """
    reads the input file and populate a list of requirements with necessary details.
    """
    # TODO: update this function to consider the input json file instead of the csv file.
    req_file = pd.read_csv(path, encoding='ISO-8859-1')
    req_list = []
    for _, row in req_file.iterrows():
        if row['reqType'] == 'Informational':
            continue
        if math.isnan(row['reqId']):
            continue
        req = dict()
        req['req_id'] = row['reqId']
        req['req_desc'] = row['reqDesc']
        req['linked_item'] = row['linkedItem']
        req['sut'] = row['sut']
        req_list.append(req)
    return req_list


def load_req_gt(path=r'ground_truth_output_list_json.csv'):
    """
    reads the input file and populate a list of requirements with necessary details.
    """
    # TODO: update this function to consider the input json file instead of the csv file.
    req_file = pd.read_csv(path, encoding='ISO-8859-1')
    req_list = []
    for _, row in req_file.iterrows():
        if math.isnan(row['Req Id']):
            continue
        req = dict()
        req['req_id'] = row['Req Id']
        req['req_desc'] = row['Requirement']
        req['linked_item'] = row['Linked Item']
        req['output'] = json.loads(row['Output Json'])
        req_list.append(req)
    return req_list


def read_config(path='config.ini'):
    """
    reads the config file and populates values for different detection techniques.
    """
    config = configparser.ConfigParser()
    config.read(path)
    params = {
        'signal_detection': config['config']['signal_detection'],
        'param_detection': config['config']['param_detection'],
    }

    return params


def load_req_model():
    """
    Load the saved requirements model
    """
    file = open('data/pickle_files/pre_loaded_req_model.pkl', 'rb')
    return pickle.load(file)


def load_reqs(path='data/input/req.txt'):
    with open(path, 'r', encoding='utf-8') as f:
        reqs = f.readlines()
    return reqs
