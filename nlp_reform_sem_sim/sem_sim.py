from nlp_reform.dto import Relation, Clause, DecompResult, Syntax
from nlp_reform.reform import Reform
from nlp_reform_sem_sim.modules import pre_process_req, \
    get_signal, get_parameter, util, load_models, get_comparison
from util import decompose_req

req_list, signals_in, signals_out, parameters = util.load_req_signals()
config = util.read_config()
models = load_models.Models(config)


class SemSimReform(Reform):

    def parse_relation(self, clause: Clause) -> Relation:
        if clause.condition in decompose_req.CONDITIONS:
            signal_list = signals_in
        else:
            signal_list = signals_out

        # get signals for each clause
        signal, score = get_signal.get_signal(clause.text, signal_list,
                                              models=models)

        # get parameter for each clause wrt to their signal
        parameter = get_parameter.get_parameter_value(clause.text, signal,
                                                      score,
                                                      models=models)

        comp_symbol = get_comparison.get_comp_symbol(clause.text, signal,
                                                     models=models)

        if clause.condition:
            return Relation(left=signal['name'], right=parameter,
                            clause=clause.text,
                            condition=clause.condition, symbol=comp_symbol,
                            syntax=Syntax(subj=signal, obj=parameter,
                                          action=''))
        else:
            return Relation(left=signal['name'], right=parameter,
                            clause=clause.text,
                            symbol=comp_symbol,
                            syntax=Syntax(subj=signal, obj=parameter,
                                          action=''))
