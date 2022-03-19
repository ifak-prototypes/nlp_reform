import pprint
import pandas as pd
from modules import util, pre_process_req, decompose_req, get_signal, get_parameter, get_comparison, \
    translate_to_logical_structure, load_models

pp = pprint.PrettyPrinter(indent=4, width=150)


def main():
    """
    1. get requirements and signals from input file
    2. for each requirement
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
    models = load_models.Models(config)
    method = config['method']
    # get the requirements
    req_list, signals_in, signals_out = util.load_req_signals()
    req_results = []
    outputs = []
    for req in req_list:
        print('Requirement:')
        pp.pprint(req)
        print('Result:')

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
        result = decompose_req.add_conditions_conjunctions(req_, decomp_conj_)

        result['req_id'] = str(int(req['req_id']))
        result['req_desc'] = req['req_desc']
        result['signals'] = []
        result['comp_symbol'] = []
        result['parameters'] = []
        result['output'] = ''

        if method == 'Decomposition':
            pp.pprint(result)
            req_results.append(result)
            continue

        for clause, cond in zip(result['clauses'], result['conditions']):

            if cond in decompose_req.CONDITIONS:
                signal_list = signals_in
            else:
                signal_list = signals_out

            # get signals for each clause
            signal, score = get_signal.get_signal(clause, signal_list, models=models)
            result['signals'].append(signal)
            if method == 'Signal':
                continue

            # get parameter for each clause wrt to their signal
            parameter = get_parameter.get_parameter_value(clause, signal, score, models=models)
            comp_symbol = get_comparison.get_comp_symbol(clause, signal, models=models)
            result['comp_symbol'].append(comp_symbol)
            result['parameters'].append(parameter)

        if method == 'Pipeline':
            structure = translate_to_logical_structure.translate(result)
            result['output'] = structure

        pp.pprint(result)
        req_results.append(result)

    util.save_results(req_results, method)
    print('---------------------')


if __name__ == '__main__':
    main()
