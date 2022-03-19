import pprint

from modules import util, pre_process_req, decompose_req, get_signal, get_parameter, get_comparison, \
    translate_to_logical_structure, load_models
import re

pp = pprint.PrettyPrinter(indent=4)


def main():
    # read the config file
    config = util.read_config()
    models = load_models.Models(config)
    # get the requirements
    req_list, signals_in, signals_out = util.load_req_signals(path=r'data/ground_truth.xlsx')

    count = 0
    accuracy = 0
    accuracy_if = 0
    accuracy_then = 0
    accuracy_until = 0
    accuracy_logic = 0
    accuracy_full_model = 0
    for req in req_list:
        # load req model linked with its linked item
        count += 1
        gt_output = util.convert_text_to_json(req['output'])

        # pre-process the requirement
        req_ = req['req_desc']
        req_ = pre_process_req.clean_newlines(req_)
        req_, events = pre_process_req.process_events_in_quotes(req_)
        # decompose newlines as clauses
        decomp_nl = decompose_req.decompose_newlines(req_)
        # decompose conditions
        decomp_cond = []
        for decomp in decomp_nl:
            decomp_cond.extend(decompose_req.decompose_conditions(decomp, models))
        # decompose conjunctions
        decomp_conj = []
        for decomp in decomp_cond:
            decomp_conj.extend(decompose_req.decompose_conjunctions(decomp, models))

        # replace XX back to event name
        decomp_conj_ = []
        for clause in decomp_conj:
            if 'XX' in clause:
                clause = clause.replace('XX', events[0])
            decomp_conj_.append(clause)
        if 'XX' in req_:
            req_ = req_.replace('XX', events[0])
        # attach details of conditions and conjunctions of clauses
        results = decompose_req.add_conditions_conjunctions(req_, decomp_conj_)

        results['req_id'] = str(int(req['req_id']))
        results['req_desc'] = req['req_desc']
        results['signals'] = []
        results['comp_symbol'] = []
        results['parameters'] = []
        results['output'] = ''

        for clause, cond in zip(results['clauses'], results['conditions']):
            if clause == '':
                continue

            if cond in decompose_req.CONDITIONS:
                signal_list = signals_in
            else:
                signal_list = signals_out

            # get signals for each clause
            signal, score = get_signal.get_signal(clause, signal_list, models=models)
            results['signals'].append(signal)

            # get parameter for each clause wrt to their signal
            parameter = get_parameter.get_parameter_value(clause, signal, score, models=models)
            comp_symbol = get_comparison.get_comp_symbol(clause, signal, models=models)
            results['comp_symbol'].append(comp_symbol)
            results['parameters'].append(parameter)

        structure = translate_to_logical_structure.translate(results)
        results['output'] = structure
        pp.pprint(results)
        print('Expected Output ', gt_output)
        print('Generated Output ', structure)
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
