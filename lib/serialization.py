from .models import *
from dataclasses import asdict
from typing import Union

def pipeline_result_to_dict(result: PipelineResult) -> dict:

    def param_to_str(p: Union[Parameter, None, str]):
        if p is None:
            return None
        if isinstance(p, Parameter):
            return p.id
        if isinstance(p, str):
            return p
        raise Exception("Invalid parameter type {}".format(p))

    clauses = [{
        'signal': i.signal.id if i.signal else None,
        'parameter': param_to_str(i.parameter),
        'clause_start': i.clause.start,
        'clause_end': i.clause.end,
        'condition': i.clause.condition,
        'operator': i.operator.value,
    } for i in result.clauses ]
    return {
        'clauses': clauses,
        'conjunctions': result.conjunctions
    }

def pipeline_result_from_dict(data: dict, requirement: Requirement, arch: Architecture) -> PipelineResult:
    result = PipelineResult()
    for i in data['clauses']:
        signal_id = i.get('signal')
        parameter_raw = i.get('parameter')
        if parameter_raw in arch.parameters:
            parameter = arch.parameters[parameter_raw]
        else:
            parameter = parameter_raw
        result.clauses.append( PipelineResult.Clause(
            clause = Clause(requirement.description, i['clause_start'], i['clause_end'], condition=i['condition']),
            signal = arch.signals[signal_id] if signal_id else None,
            parameter = parameter,
            operator = Operator(i['operator'])
        ))
    result.conjunctions = data['conjunctions']
    return result

def requirement_to_dict(req: Requirement) -> dict:
    data = asdict(req)
    data['components'] = [ i['id'] for i in data['components'] ]
    data['result'] = pipeline_result_to_dict(req.result)
    return data

def requirement_from_dict(data: dict, arch: Architecture) -> Requirement:
    data = data.copy()
    components = data.pop('components')
    requirement = Requirement(**data, components = [])
    if 'result' in data:
        requirement.result = pipeline_result_from_dict(data['result'], requirement, arch)
    for component_id in components:
        try:
            requirement.components.append( arch.components[component_id] )
        except KeyError:
            print("Skipping unknown component {}".format(component_id))
    return requirement

def signal_to_dict(signal: Signal) -> dict:
    return {
        "id": signal.id,
        "description": signal.description,
        "components": [ i.id for i in signal.components ],
        "type": signal.type,
    }

def parameter_to_dict(parameter: Parameter) -> dict:
    return {
        "id": parameter.id,
        "description": parameter.description,
        "component": parameter.component.id,
        "type": parameter.value.get_typename(),
        "value": parameter.value.to_string()
    }

def architecture_to_dict(arch: Architecture) -> dict:
    return {
        "components": [ asdict(i) for i in arch.components.values() ],
        "signals": [ signal_to_dict(i) for i in arch.signals.values() ],
        "parameters": [parameter_to_dict(i) for i in arch.parameters.values()],
    }

def architecture_from_dict(data: dict) -> Architecture:
    arch = Architecture()
    for i in data['components']:
        component = SoftwareComponent(i['id'], i['description'])
        arch.components[component.id] = component
    for i in data['parameters']:
        c = i['component']
        component = arch.components[c]
        val = Variant.create(i['type'], i['value'])
        parameter = Parameter(component, val, i['id'], i['description'])
        if c in arch.parameters_by_component:
            arch.parameters_by_component[c].append(parameter)
        else:
            arch.parameters_by_component[c] = [parameter]
        arch.parameters[parameter.id] = parameter
    for i in data['signals']:
        c = i['components']
        signal = Signal( [arch.components[j] for j in c], i['id'], i['description'], i['type'])
        for j in c:
            if j in arch.signals_by_component:
                arch.signals_by_component[j].append(signal)
            else:
                arch.signals_by_component[j] = [signal]
        arch.signals[signal.id] = signal
    return arch

def project_to_dict(project: Project) -> dict:
    return {
        "architecture": architecture_to_dict(project.architecture),
        "requirements": [ requirement_to_dict(i) for i in project.requirements ]
    }

def project_from_dict(data: dict) -> Project:
    project = Project()
    project.architecture = architecture_from_dict( data['architecture'] )
    project.requirements = [ requirement_from_dict(i, project.architecture) for i in data['requirements'] ]
    return project