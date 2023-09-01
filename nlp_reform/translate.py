from typing import List

from nlp_reform.dto import Relation, Structure, Block


def translate(relations: List[Relation], conjunctions: List[str]):
    if_block_relations = []
    then_block_relations = []
    until_block_relations = []

    for idx, relation in enumerate(relations):
        if relation.condition in ['when', 'if']:
            if_block_relations.append(relation)
        elif relation.condition in ['until']:
            until_block_relations.append(relation)
        else:
            then_block_relations.append(relation)

    if_block_conjunctions = []
    then_block_conjunctions = []
    until_block_conjunctions = []
    for idx, conjunction in enumerate(conjunctions):
        if relations[idx].condition in ['when', 'if'] and relations[idx+1].condition in ['when', 'if']:
            if_block_conjunctions.append(conjunction)
        elif relations[idx].condition in ['until']:
            until_block_conjunctions.append(conjunction)
        else:
            then_block_conjunctions.append(conjunction)

    return Structure(if_block=Block(relations=if_block_relations,
                                    conjunctions=if_block_conjunctions),
                     then_block=Block(relations=then_block_relations,
                                      conjunctions=then_block_conjunctions),
                     until_block=Block(relations=until_block_relations,
                                       conjunctions=until_block_conjunctions)
                     )
