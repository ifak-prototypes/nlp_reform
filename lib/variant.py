class VariantException(Exception):
    pass

class Variant:

    @classmethod 
    def create(self, typeName: str, val: str):
        variantGenerators = [
            BooleanVariant,
            NumberVariant
        ]
        for generator in variantGenerators:
            if ( generator.supports(typeName) ):
                return generator.create(val)
        raise VariantException("Invalid typename " + typeName)

class BooleanVariant(Variant):

    def __init__(self, value: bool):
        self.value = value

    @classmethod
    def supports(self, typeName: str):
        return typeName == 'boolean'

    @classmethod
    def create(self, val: str):
        val = val.upper()
        if val == "TRUE": return BooleanVariant(True)
        if val == "FALSE": return BooleanVariant(False)
        raise VariantException("Cannot parse value {} as boolean".format(val))

    def get_typename(self) -> str:
        return "boolean"

    def to_string(self) -> str:
        return "TRUE" if self.value else "FALSE"

class NumberVariant(Variant):
    
    def __init__(self, value: float):
        self.value = value

    @classmethod
    def supports(self, typeName: str) -> bool:
        return typeName == 'single' or typeName == 'uint16'

    @classmethod
    def create(self, val: str) -> Variant:
        try:
            f = float(val)
        except ValueError as e:
            raise VariantException("Cannot parse {} as float: {}".format(val, e))
        return NumberVariant(f)

    def get_typename(self) -> str:
        return "single"

    def to_string(self) -> str:
        return str(self.value)

