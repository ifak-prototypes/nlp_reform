import xml.etree.ElementTree as ET
op_file_xml = 'data/operator_symbols.xml'

def find_comp_symbol_from_xml(norm_req, models):
    doc = ET.parse(op_file_xml).getroot()

    tokens = []
    for token in models.spacy_nlp(norm_req):
        tokens.append(token.lemma_)

    comp_symbol = ""

    for child in doc:
        symbol = child.find('comp_symbol').text
        for child_1 in child:
            if child_1.text in tokens:
                comp_symbol = symbol

    return comp_symbol

def get_comp_symbol_single(clause, models):
    doc = models.spacy_nlp(clause)
    verb_text = ''
    for token in doc:
        if token.tag_ == 'VBZ':
            verb_text = token.text
            string = clause.split(" ")
            try:
                index = string.index(verb_text)
                next_word = string[index + 1]
            except:
                next_word = ''
            verb_text = verb_text + ' ' + next_word

    comp_symbol = find_comp_symbol_from_xml(verb_text, models)

    if comp_symbol == '':
        comp_symbol = '='

    return comp_symbol

def get_comp_symbol(clause, signal, models):
    if signal['data_type'] == 'boolean':
        return '='
    else:
        return get_comp_symbol_single(clause, models)