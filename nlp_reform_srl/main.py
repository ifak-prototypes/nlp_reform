from nlp_reform_srl.modules.map_frames_to_relation import *
from nlp_reform_srl.modules.srl_frames import SemFrames
from nlp_reform.translate import translate
from util import pre_process_req, decompose_req


def main():
    """
    1. Load Requirement
    2. Pre-process requirement by replacing text under quotation and removing square brackets
    3. Decompose requirement based on condition first and then based on conjunction
    4. Get SRL frames and map those to signals and parameters and form relation
    5. Form logical structure
    """

    req = {
            'reqId': 1,
            'reqDesc': "The maximum power shall be limited to G_Max and the event 'High device temperature' shall be "
                       "indicated when the device temperature exceeds T_Hi C.",
        }

    req_ = req['reqDesc']
    req_ = pre_process_req.clean_newlines(req_)
    req_ = pre_process_req.remove_square_brackets(req_)
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

    decomp_result = decompose_req.add_conditions_conjunctions(req_, decomp_conj_)

    # instantiate SRL model
    sem_frames = SemFrames()

    relations = []
    for clause in decomp_conj_:
        srl_frames = get_srl_frames(clause, sem_frames)

        is_guard, condition_value = check_if_guard(clause)
        rel = map_frame_to_relation(srl_frames, clause, condition_value, is_guard)
        print(rel)
        relations.append(rel)

    structure = translate(relations=relations,
                          conjunctions=decomp_result.conjunctions
                          )

    text = ""
    if structure.if_text:
        text += f"if ( {structure.if_text.strip()} )"
    if structure.then_text:
        text += f"then ( {structure.then_text.strip()} )"
    if structure.until_text:
        text += f"until ( {structure.until_text.strip()} )"

    print(text)


if __name__ == '__main__':
    main()
