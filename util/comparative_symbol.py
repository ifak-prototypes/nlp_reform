import xml.etree.ElementTree as ET


def find_comparative_symbol(nlp, norm_req, op_file_xml='data/operator_symbols.xml'):
    doc = ET.parse(op_file_xml).getroot()

    tokens = []
    for token in nlp(norm_req):
        tokens.append(token.lemma_)

    comp_symbol = ""

    for child in doc:
        symbol = child.find('comp_symbol').text
        for child_1 in child:
            if child_1.text in tokens:
                comp_symbol = symbol

    return comp_symbol
