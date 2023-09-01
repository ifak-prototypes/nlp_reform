import pprint
from modules import util, pre_process_req, decompose_req, get_signal, get_parameter, translate_to_logical_structure
import pandas as pd
import re

pp = pprint.PrettyPrinter(indent=4)


def main():
    """
    1. get requirements from input file
    2. for each requirement
        a. get model for the requirement
        b. preprocess requirement
            i. clean the requirement text
            ii. decompose the requirement (newlines, conditions, conjunctions)
            iii. infer the type of requirement -- if, then, until
            iv. infer the condition between clauses -- and, or
        c. for each clause in sub-requirements
            i. get signal
            ii. get parameter
            iii. get comparison symbol
        d. get the logical structure (if..then..until)
        e. get the sequence diagram (opt..break)
    """
    # read the config file

    config = util.read_config()

    # get the requirements
    req_list = util.load_req_gt()
    req_dict = util.load_req_model()
    results = []
    count = 0
    accuracy = 0
    accuracy_if = 0
    accuracy_then = 0
    accuracy_until = 0
    accuracy_logic = 0
    accuracy_full_model = 0
    for req in req_list:
        # load req model linked with its linked item
        req_model = None
        inp_model = None
        out_model = None
        if req['linked_item'] in req_dict:
            req_model, inp_model, out_model = req_dict[req['linked_item']]
        if req_model is None:
            # logging.error(f'{linkedItem} : Linked item not found')
            continue
        count += 1
        # pp.pprint(req)
        # print('')
        gt_output = req['output']

        # pre-process the requirement
        # TODO: do we still need removing [] and replacing events with XX?
        req_ = req['req_desc']
        req_ = pre_process_req.clean_newlines(req_)
        #req_ = pre_process_req.remove_square_brackets(req_)
        req_, events = pre_process_req.process_events_in_quotes(req_)
        # decompose newlines as clauses
        decomp_nl = decompose_req.decompose_newlines(req_)
        # decompose conditions
        decomp_cond = []
        for decomp in decomp_nl:
            decomp_cond.extend(decompose_req.decompose_conditions(decomp))
        # decompose conjunctions
        decomp_conj = []
        for decomp in decomp_cond:
            decomp_conj.extend(decompose_req.decompose_conjunctions(decomp))

        # replace XX back to event name
        decomp_conj_ = []
        for clause in decomp_conj:
            if 'XX' in clause:
                clause = clause.replace('XX', events[0])
            decomp_conj_.append(clause)
        if 'XX' in req_:
            req_ = req_.replace('XX', events[0])
        # attach details of conditions and conjunctions of clauses
        clauses = decompose_req.add_conditions_conjunctions(req_, decomp_conj_)

        print(req['req_id'])
        pp.pprint(clauses)

        clauses['signals'] = []
        clauses['comp_symbol'] = []
        clauses['parameters'] = []

        for clause, cond in zip(clauses['clauses'], clauses['conditions']):
            if clause == '':
                continue

            if cond in decompose_req.CONDITIONS:
                model = inp_model
            else:
                model = out_model

            # get signals for each clause
            signals, scores = get_signal.get_signal(clause, model, signal_detection=config['signal_detection'])
            clauses['signals'].append(signals)

            # get parameter for each clause wrt to their signal
            parameter, comp_symbol = get_parameter.get_parameter_value(clause, signals, scores, param_detection=config['param_detection'])
            clauses['comp_symbol'].append(comp_symbol)
            clauses['parameters'].append(parameter)
        # pp.pprint(clauses)

        structure = translate_to_logical_structure.translate(clauses)
        print(gt_output)
        print(structure)
        print('---------------------')
        acc_l = 0
        if structure == gt_output:
            accuracy += 1
        if structure['if'] == gt_output['if']:
            accuracy_if += 1
            acc_l += 1
        if structure['then'] == gt_output['then']:
            accuracy_then += 1
            acc_l += 1
        if structure['until'] == gt_output['until']:
            accuracy_until += 1
            acc_l += 1

        accuracy_logic += acc_l/3
        # results.append([req['req_id'], req['linked_item'], req['req_desc'], req['output'], structure])
        acc_fm = 0
        fm_count = 0
        if gt_output['if']:
            gt_text_ = gt_output['if'].replace('(', '')
            gt_text_ = gt_text_.replace(')', '')
            text_ = structure['if'].replace('(', '')
            text_ = text_.replace(')', '')
            gt_text = re.split('([=|<|>|\-|]|and|or)', gt_text_)
            text = re.split('([=|<|>|\-|]|and|or)', text_)
            print(gt_text, text)
            fm_count += len(gt_text)
            for t1, t2 in zip(gt_text, text):
                if t1 == t2:
                    acc_fm += 1

        if gt_output['then']:
            gt_text_ = gt_output['then'].replace('(', '')
            gt_text_ = gt_text_.replace(')', '')
            text_ = structure['then'].replace('(', '')
            text_ = text_.replace(')', '')
            gt_text = re.split('([=|<|>|\-|]|and|or)', gt_text_)
            text = re.split('([=|<|>|\-|]|and|or)', text_)
            print(gt_text, text)
            fm_count += len(gt_text)
            for t1, t2 in zip(gt_text, text):
                if t1 == t2:
                    acc_fm += 1

        if gt_output['until']:
            gt_text_ = gt_output['until'].replace('(', '')
            gt_text_ = gt_text_.replace(')', '')
            text_ = structure['until'].replace('(', '')
            text_ = text_.replace(')', '')
            gt_text = re.split('([=|<|>|\-|]|and|or)', gt_text_)
            text = re.split('([=|<|>|\-|]|and|or)', text_)
            print(gt_text, text)
            fm_count += len(gt_text)
            for t1, t2 in zip(gt_text, text):
                if t1 == t2:
                    acc_fm += 1
        print(acc_fm, fm_count)
        accuracy_full_model += acc_fm/fm_count
        #if count == 5:
        #    break

    #column = ['Req Id', 'Linked Item', 'Requirement', 'Output', 'Generated Output']
    #df = pd.DataFrame(results, columns=column)
    #df.to_csv('generated_output.csv', index=False)

    print('Count ', count)
    print('IF Accuracy Count', accuracy_if)
    print('THEN Accuracy Count', accuracy_then)
    print('UNTIL Accuracy Count', accuracy_until)
    print('Full Req Accuracy Count', accuracy)
    print('Accuracy(if) ', accuracy_if / count)
    print('Accuracy(then) ', accuracy_then / count)
    print('Accuracy(until) ', accuracy_until / count)
    a = accuracy_if / count
    a += accuracy_then / count
    a += accuracy_until / count
    print('Logic Accuracy ', a/3)
    print('Macro Logic Accuracy ', accuracy_logic / count)
    print('Full Model Accuracy ', accuracy_full_model / count)
    print('Accuracy ', accuracy/count)


if __name__ == '__main__':
    main()
