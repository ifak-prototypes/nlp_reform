from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union


@dataclass
class Syntax:
    subj: Union[str, dict]
    obj: Union[str, dict]
    action: Union[str, dict]

    action_type: Optional[str] = ''
    action_symbol: Optional[str] = ''
    action_constraint: List[str] = None
    verb_type: List[str] = None


@dataclass
class Span:
    start: int
    end: int


class Condition(Enum):
    IF = "if"
    WHEN = "when"
    UNTIl = "until"
    THEN = "then"

    def __str__(self):
        return str(self.value)


@dataclass
class Clause:
    text: str
    condition: Condition
    # metadata can be the linked item
    metadata: Optional[str] = None


@dataclass
class DecompResult:
    clauses: List[Clause]
    conjunctions: List[str]


class Version(Enum):
    POS_DEP = "POS and DEP based"
    SRL = "SRL based"
    SEM_SIM = "Semantic similarity based"

    def __str__(self):
        return str(self.value)


@dataclass
class Relation:
    syntax: Optional[Syntax] = None
    left: str = ''
    symbol: str = ''
    right: str = ''
    clause: str = ''
    neg_or_pos: str = 'pos'
    condition: Condition = Condition.THEN.value

    def get_text(self):
        text = f'**{self.condition} (** {self.get_minimal_text()} **)**'
        return text

    def get_minimal_text(self):

        if self.neg_or_pos == 'neg':
            if self.condition == 'then':
                text = f'not {self.left} ( {self.right} )'
            else:
                text = f'{self.left} ! {self.symbol} {self.right}'
        else:
            if self.condition == 'then':
                text = f'{self.left} ( {self.right} )'
            else:
                text = f'{self.left} {self.symbol} {self.right}'

        return text


@dataclass
class Block:
    relations: List[Relation]
    conjunctions: List[str]


@dataclass
class Structure:
    if_block: Block
    then_block: Block
    until_block: Block

    @staticmethod
    def unfold_block(block):
        relation_text = ''
        for idx, relation in enumerate(block.relations):
            try:
                if block.conjunctions[idx]:
                    relation_text += f"{relation.get_minimal_text()} **{block.conjunctions[idx]}** "
                else:
                    relation_text += f"{relation.get_minimal_text()}"
            except:
                relation_text += f"{relation.get_minimal_text()}"
        return relation_text

    def __post_init__(self):
        self.if_text = f"{self.unfold_block(self.if_block)}" \
            if self.if_block.relations else ''
        self.then_text = f"{self.unfold_block(self.then_block)}" \
            if self.then_block.relations else ''
        self.until_text = f"{self.unfold_block(self.until_block)}" \
            if self.until_block.relations else ''
