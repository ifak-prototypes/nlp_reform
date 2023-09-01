import pprint
from modules import util#, pre_process_req, decompose_req, get_signal, get_parameter, translate_to_logical_structure
import pandas as pd
import json
import re
import math

pp = pprint.PrettyPrinter(indent=4)

# get the requirements
#req_list = util.load_req_gt()
path=r'ground_truth_output_list.csv'
req_file = pd.read_csv(path, encoding='ISO-8859-1')
req_list = []
for _, row in req_file.iterrows():
    if math.isnan(row['Req ID']):
        continue
    req = dict()
    req['req_id'] = row['Req ID']
    req['req_desc'] = row['Requirement']
    req['linked_item'] = row['Linked Item']
    req['output'] = row['Formalized Requirement']
    req_list.append(req)


results = []
for req in req_list:
    output = req['output']
    if_text = None
    then_text = None
    until_text = None
    #print(output)
    result_if = re.search(r"if\((.*?)\)", output)
    result_then = re.search(r"then\((.*?)\)", output)
    result_until = re.search(r"until\((.*?)\)", output)
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
    code = json.dumps(code)
    print(req['req_id'])
    print(code)
    results.append([req['req_id'], req['linked_item'], req['req_desc'], req['output'], code])
    print('-----------------')
    #break

column = ['Req Id', 'Linked Item', 'Requirement', 'Output', 'Output Json']
df = pd.DataFrame(results, columns=column)
df.to_csv('ground_truth_output_list_json.csv', index=False)