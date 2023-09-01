"""
This script contains the class definitions of the requirements model.
"""
from enum import Enum, unique
import pprint

pp = pprint.PrettyPrinter(indent=4)


def _add_element(element, elements, ElementsClass):
    if not element:
        raise Exception("Input argument '%s' is empty" % element)
    for _ in element:
        if _ not in elements:
            assert isinstance(_, ElementsClass), \
                "Input argument '%s' is not of type '%s'" % (_, ElementsClass)
            elements.append(_)


def _add_steps(step):
    steps = []
    if not step:
        raise Exception("Input argument '%s' is empty" % step)
    for _ in step:
        if _ not in step:
            if not isinstance(_, (Message, Opt, Alt, Loop)):
                raise Exception("Input argument '%s' is not of type 'Message/Opt/Alt/Loop'" % _.__class__)
            steps.append(_)
    return steps


class RequirementModel:
    """
    This class holds the specifications of all requirements in the document.
    """

    def __init__(self, name):
        """

        :param name:
        """
        self.name = name
        self.attributes = []
        self.components = []
        self.states = []
        self.messages = []
        self.requirements = []

    def add_attribute(self, attribute):
        _add_element(attribute, self.attributes, Attribute)

    def add_component(self, component):
        _add_element(component, self.components, Component)

    def add_state(self, state):
        _add_element(state, self.states, State)

    def add_message(self, message):
        _add_element(message, self.messages, Message)

    def add_requirement(self, requirement):
        _add_element(requirement, self.requirements, Requirement)


@unique
class DataTypes(Enum):
    """
    Enumeration
    """
    real = 1
    int = 2
    bool = 3
    string = 4


@unique
class CompTypes(Enum):
    """
    Enumeration
    """
    ACTOR = 1
    SUT = 2


@unique
class MessageDirection(Enum):
    """
    Enumeration
    """
    incoming = 1
    outgoing = 2


class Attribute:
    def __init__(self, name, dataType=DataTypes.real, value=None, description=None):
        """

        :param name:
        :param dataType:
        :param value:
        :param description:
        """
        self.name = name
        self.dataType = dataType
        self.value = value
        self.description = description

        assert isinstance(dataType, DataTypes), \
            "DataType of attribute '%s' is not of the type 'DataTypes'" % self.name

    def __str__(self):
        return str(self.__class__) + '\n' + \
               '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))


class Component:
    def __init__(self, name, compType, description=None):
        """

        :param name:
        :param compType:
        :param value:
        :param description:
        """
        self.name = name  # TODO: if name is not given, add as an empty Component. Distinguish as objects
        self.compType = compType  # TODO: if name is not given, add as an empty Component
        self.description = description

        assert isinstance(self.compType, CompTypes), \
            "CompType of the component '%s' is not of the type 'CompTypes'" % self.name

    def __str__(self):
        return str(self.__class__) + '\n' + \
               '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))


class State:
    def __init__(self, name):
        """

        :param name:
        """
        self.name = name

    def print_values(self):
        print('\tSTATE')
        print('\tname', self.name)


class Message:
    def __init__(self, name, direction=MessageDirection.outgoing, sender=None, receiver=None, inParam=None, outParam=None, desc=None):
        """

        :param name:
        :param sender:
        :param receiver:
        :param inParam:
        :param outParam:
        """
        self.name = name
        self.message_direction = direction

        # Consider input argument if not None, otherwise set to default value
        if sender:
            self.sender = sender
        else:
            self.sender = Component(name='XXX', compType=CompTypes.ACTOR)
        # Consider input argument if not None, otherwise set to default value
        if receiver:
            self.receiver = receiver
        else:
            self.receiver = Component(name='XXX', compType=CompTypes.ACTOR)
        # Consider input argument if not None, otherwise set to default value
        if inParam:
            self.inParam = inParam  # TODO: consider a list of attributes
        else:
            self.inParam = Attribute(name='XXX')
        # Consider input argument if not None, otherwise set to default value
        if outParam:
            self.outParam = outParam
        else:
            self.outParam = Attribute(name='XXX')
        # Consider input argument if not None, otherwise set to default value
        if desc:
            self.desc = desc
        else:
            self.desc = ''

        assert isinstance(self.sender, Component), \
            "Sender of the message '%s' is not of the type 'Component'" % self.name
        assert isinstance(self.receiver, Component), \
            "Receiver of the message '%s' is not of the type 'Component'" % self.name
        assert isinstance(self.inParam, Attribute), \
            "InParam of the message '%s' is not of the type 'Attribute'" % self.name
        assert isinstance(self.outParam, Attribute), \
            "OutParam of the message '%s' is not of the type 'Attribute'" % self.name

    def print_values(self):
        print('\tMESSAGE')
        print("\tname", self.name)
        print("\tsender", self.sender.name)
        print("\treceiver", self.receiver.name)
        print("\tinParam", self.inParam.name)
        print("\toutParam", self.outParam.name)


class Requirement:
    """
    This class holds the specifications of a requirement in the document.
    """

    def __init__(self, text, rId=None, rType=None, section=None, heading=None):
        self.rId = rId
        self.rType = rType
        self.section = section
        self.heading = heading
        self.text = text
        self.sequences = []

    def add_sequences(self, sequences):
        _add_element(sequences, self.sequences, Sequence)

    def print_values(self):
        print('REQUIREMENT')
        print('text', self.text)
        print('SEQUENCES')
        for sequence in self.sequences:
            sequence.print_values()
            print('--------------------')


class Opt:
    """

    """

    def __init__(self):
        self.operands = []

    def add_operands(self, operands):
        _add_element(operands, self.operands, Operand)

    def print_values(self):
        print('\tOPT')
        for operand in self.operands:
            operand.print_values()


class Alt:
    """

    """

    def __init__(self):
        self.operands = []
        self.else_operand =  []

    def add_operands(self, operands):
        _add_element(operands, self.operands, Operand)

    def add_else_operand(self, operand):
        self.else_operand = operand
        assert operand.type == 'else', 'Else operand should be provided'

    def print_values(self):
        print(str(self.__class__) + '\n' + \
              '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__)))


class Loop:
    """

    """

    def __init__(self, max, min=0):
        self.min = min
        self.max = max
        self.operands = []

    def add_operands(self, operands):
        _add_element(operands, self.operands, Operand)

    def print_values(self):
        print('\tLOOP', '(min=', self.min, ', max=', self.max, ')')
        for operand in self.operands:
            operand.print_values()

    def __str__(self):
        return str(self.__class__) + '\n' + \
               '\n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))


class Sequence:
    def __init__(self, iState, fState):
        """

        :param iState:
        :param steps:
        :param fState:
        """
        self.iState = iState
        self.fState = fState
        self.steps = []

        assert isinstance(self.iState, State), \
            "iState of the sequence is not of the type 'State'"
        assert isinstance(self.fState, State), \
            "fState of the sequence is not of the type 'State'"

    def add_steps(self, steps):  # TODO: move as a common function, repeated
        if not steps:
            raise Exception("Input argument '%s' is empty" % steps)
        for _ in steps:
            if _ not in self.steps:
                if not isinstance(_, (Message, Opt, Alt, Loop)):
                    raise Exception("Input argument '%s' is not of type 'Message/Opt/Alt/Loop'" % _.__class__)
                self.steps.append(_)

    def print_values(self):
        print('\tSEQUENCE')
        print('\tiState', self.iState.name)
        print('\tfState', self.fState.name)
        for step in self.steps:
            step.print_values()


@unique
class Operators(Enum):
    """
    Enumeration
    """
    AND = "&&"
    OR = "||"
    NONE = ''  # to correct the dimensions of operators and expressions


@unique
class CompSymbols(Enum):
    """
    Enumeration
    """
    LESSER_THAN = "<"
    LESSER_THAN_EQ = "<="
    EQUAL_TO = "=="
    NOT_EQUAL_TO = "!="
    GREATER_THAN = ">"
    GREATER_THAN_EQ = ">="


class Guard:
    def __init__(self):
        self.expressions = []
        self.operators = [Operators.NONE]

    def add_expression(self, expressions):
        _add_element(expressions, self.expressions, Expression)

    def add_operators(self, operator):
        _add_element(operator, self.operators, Operators)

    def __repr__(self):
        guard = ''
        for operator, expression in zip(self.operators, self.expressions):
            guard += operator.value + ' ' + str(expression) + ' '
        return guard


class Expression:
    def __init__(self, leftValue, compSymbol, rightValue):
        self.leftValue = leftValue
        self.compSymbol = compSymbol
        self.rightValue = rightValue

        assert isinstance(self.leftValue, Attribute), \
            "leftValue of the expression is not of the type 'Attribute'"
        assert isinstance(self.rightValue, Attribute), \
            "rightValue of the expression is not of the type 'Attribute'"
        assert isinstance(self.compSymbol, CompSymbols), \
            "compSymbol of the expression is not of the type 'CompSymbols'"

    def __repr__(self):
        return self.leftValue.name + " " + self.compSymbol.value + " " + self.rightValue.name


class Operand:
    def __init__(self, fState, type='if'):
        self.type = type  # can be 'if' or 'else'. if, else if -> if
        self.fState = fState
        self.steps = []
        self.guards = []  # TODO: check type and then allow adding guards

    def add_steps(self, steps):  # TODO: move as a common function, repeated
        if not steps:
            raise Exception("Input argument '%s' is empty" % steps)
        for _ in steps:
            if _ not in self.steps:
                if not isinstance(_, (Message, Opt, Alt, Loop)):
                    raise Exception("Input argument '%s' is not of type 'Message/Opt/Alt/Loop'" % _.__class__)
                self.steps.append(_)

    def add_guard(self, guards):
        _add_element(guards, self.guards, Guard)

    def print_values(self):
        print('\tOPERAND')
        print("\ttype", self.type)
        print("\tfState", self.fState.name)
        for step in self.steps:
            step.print_values()
        for guard in self.guards:
            print('\tGUARD')
            print('\t', guard)


if __name__ == '__main__':
    reqModel = RequirementModel(name="Bombardier use cases")

    att1 = Attribute(name='t_batt_min', dataType=DataTypes.real, value='0', description='Defines the minimum of t_batt')
    att2 = Attribute(name='t_batt_max', dataType=DataTypes.real, value='75',
                     description='Defines the maximum of t_batt')

    comp1 = Component(name='battery', compType=CompTypes.ACTOR,
                      description='Battery which sends info to the controller')
    comp2 = Component(name='controller', compType=CompTypes.SUT, description='This is the SUT component')

    iState = State(name='init')
    fState = State(name='final_state')

    msg = Message(name='check', inParam=None, outParam=att2)
    req = Requirement(text='If t_batt_min is less than 10, error message is displayed.')

    reqModel.add_attribute(attribute=[att1, att2])
    reqModel.add_component(component=[comp1, comp2])
    reqModel.add_message(message=[msg])
    reqModel.add_state(state=[iState, fState])
    reqModel.add_requirement(requirement=[req])

    expression1 = Expression(leftValue=att1, compSymbol=CompSymbols.EQUAL_TO, rightValue=att2)
    expression2 = Expression(leftValue=att1, compSymbol=CompSymbols.GREATER_THAN, rightValue=att2)
    guard = Guard()
    guard.add_expression([expression1, expression2])
    guard.add_operators([Operators.AND])
    # print('GUARD:', guard)
    operand = Operand(fState=fState, type='if')
    operand.add_steps([msg])
    operand.add_guard([guard])

    opt = Opt()
    opt.add_operands([operand])

    sequence = Sequence(iState=iState, fState=fState)
    sequence.add_steps([opt])

    # print("Sequence\n", sequence)
    req.add_sequences([sequence])
    # req.print_values()

    # print("Req\n", req)

    # reqModel.print_values()
    # _print_values(reqModel)
    # _print_values(req)
    req.print_values()

    '''
    How to feed values to class?
    ----------------------------
    1. Instantiate a requirements model. This shall contain all the details of all the requirements.
    For eg. reqModel = RequirementModel(name="Bombardier use cases")
    
    2. Identify and add attributes, components, messages, states and requirements to the model.
    For eg. reqModel.add_attribute(attribute=[att1, att2])
            reqModel.add_component(component=[comp1, comp2])
            reqModel.add_message(message=[msg])
            reqModel.add_state(state=[iState, fState])
            reqModel.add_requirement(requirement=[req])
            
    3. Now for each requirement, instantiate and add sequences.
    Bottom-up approach.
        a. Build an expression.
        b. Add this expression to a guard as,
           -- single expression (with no operators)
           -- combination of expressions (with operators)
        c. Add this guard to an operand.
        d. Identify the steps - Opt/Alt/Loop/Message
        e. Add the step (obtained in step d.) to the operand (obtained in step c.).
        f. Add the step to the sequence.
        g. Add the sequence to the requirement
        h. Add the requirement to the requirement model.
    '''
