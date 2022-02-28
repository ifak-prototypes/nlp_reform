from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union
from lib.variant import BooleanVariant, Variant
from datetime import datetime

class Operator(Enum):
    EqualTo = '='
    GreaterThan = '>'
    GreaterThanEqualTo = '>='
    LessThan = '<'
    LessThanEqualTo = '<='


@dataclass
class PipelineResult:

    @dataclass
    class Clause:
        clause: "Clause"
        signal: Optional["Signal"]
        parameter: Union[None, "Parameter", str]
        operator: Operator

    clauses: List["PipelineResult.Clause"] = field(default_factory=list)
    conjunctions: List[str] = field(default_factory=list)

@dataclass
class SoftwareComponent:
    id: str = ''
    description: str = ''


@dataclass
class Requirement:
    components: List[SoftwareComponent]
    id: str = ''
    description: str = ''
    section: str = ''
    checked: bool = False
    last_import = datetime.now()
    result: "PipelineResult" = PipelineResult()

    def update_from(self, new_requirement):
        if new_requirement.description != self.description:
            self.checked = False
            self.last_import = datetime.now()
        self.components = new_requirement.components
        self.id = new_requirement.id
        self.description = new_requirement.description
        self.section = new_requirement.section

    def remove_invalid_components(self, comps: Dict[str, SoftwareComponent]):
        for i in self.components:
            if i not in comps:
                self.checked = False
                self.components.remove(i)


@dataclass
class Clause:
    text: str = ''
    start: int = 0  # start is inclusive
    end: int = -1  # end is exclusive
    condition: Optional[str] = None

    def __post_init__(self):
        if self.end < 0: self.end = len(self.text)

    def lookup(self, text: str) -> str:
        return text[self.start:self.end]


@dataclass
class Signal:
    components: List[SoftwareComponent]
    id: str = ''
    description: str = ''
    type: str = ''


@dataclass
class Parameter:
    component: SoftwareComponent
    value: Variant
    id: str = ''
    description: str = ''

TrueParameter = Parameter(SoftwareComponent('all'), BooleanVariant(True), 'TRUE', '')
FalseParameter = Parameter(SoftwareComponent('all'), BooleanVariant(True), 'FALSE', '')


@dataclass
class Architecture:
    def __init__(self) -> None:
        self.components = {}
        self.signals_by_component = {}
        self.signals = {}
        self.parameters_by_component = {}
        self.parameters = {}
    components: Dict[str, SoftwareComponent]
    signals_by_component: Dict[str, List[Signal]]
    signals: Dict[str, Signal]
    parameters_by_component: Dict[str, List[Parameter]]
    parameters: Dict[str, Parameter]


@dataclass
class DecompositionResult:
    clauses: List[Clause]
    conjunctions: List[str]


@dataclass
class SignalDetectionResult:
    signal: Signal
    score: float


@dataclass
class Project:
    requirements: List[Requirement] = field(default_factory=list)
    architecture: Architecture = Architecture()
    
    def import_requirements(self, requirements: List[Requirement]) -> None:
        # TODO: improve performance
        for i in self.requirements:
            found = False
            for j in requirements:
                if i.id == j.id:
                    i.update_from(j)
                    found = True
                    break
            if not found:
                self.requirements.remove(i)
        for j in requirements:
            found = False
            for i in self.requirements:
                if i.id == j.id:
                    found = True
            if not found:
                self.requirements.append(j)

    def import_architecture(self, architecture: Architecture) -> None:
        self.architecture = architecture
        for i in self.requirements:
            i.remove_invalid_components(self.architecture.components)
