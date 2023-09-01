import re
from typing import List, Union, Any

from nlp_reform.dto import Relation, Version, Structure
from nlp_reform_sem_sim.modules.util import load_req_signals
from util.util import load_reqs


class ReformUI:
    def __init__(self, st):
        self.submit = None
        self.version: Version = Version.POS_DEP
        self.req: str = ''
        self.st = st

    def add_sidebar(self):
        with self.st.sidebar:

            self.version = self.st.radio(
                "Choose a version",
                (Version.POS_DEP, Version.SRL, Version.SEM_SIM)
            )

            self.st.write("Read more "
                          "[here](https://github.com/ifak-prototypes/nlp_reform#readme).")

            for i in range(10):
                self.st.write('')

            self.st.write("For more details, please contact: robin.groepler@ifak.eu")
            self.st.image("data/logo.svg", width=10)

    def write_title(self):
        col1, col2 = self.st.columns([10, 20])
        col1.markdown("<span class='title big'>Re-Form</span>",
                      unsafe_allow_html=True)
        col2.markdown("<span class='title small'>Natural language "
                      "**Re**quirements "
                      "**Form**alization</span>",
                      unsafe_allow_html=True)
        self.st.markdown(' ',
                         unsafe_allow_html=True)

    def input_requirement(self):
        with self.st.form("key"):
            req_from_text = self.st.text_area("Enter the requirement")
            req_from_menu = self.st.selectbox(
                "Or choose from this drop down",
                tuple([""]
                      + load_reqs()
                      )
            )
            submit = self.st.form_submit_button(label='Formalize!')

        if submit:
            self.req = req_from_text if req_from_text else req_from_menu
            self.st.markdown(f"**Formalizing relations for the requirement:**",
                             unsafe_allow_html=True)
            self.st.markdown(f"{self.req}", unsafe_allow_html=True)

    def input_requirement_sem_sim(self):

        with self.st.form("key"):
            self.st.info(
                "You can formalize requirements from your input file or "
                "use the default ones. Choose the tabs below accordingly.")
            t1, t2 = self.st.tabs(["Upload the input file",
                                   "Use default requirements"])
            uploaded_file = t1.file_uploader("Choose the input file", type='xlsx')
            if uploaded_file:
                user_reqs_list = load_req_signals(uploaded_file)[0]
                user_reqs = [s['req_desc'] for s in user_reqs_list]
                user_req = t1.selectbox(
                    "Choose from the drop down of requirements",
                    [""] + user_reqs
                )
                t2.warning("Refresh the app to see the default requirements!")
            else:
                default_reqs_list = load_req_signals()[0]
                default_reqs = [s['req_desc'] for s in default_reqs_list]
                default_req = t2.selectbox(
                    "Choose from the drop down of requirements",
                    [""] + default_reqs
                )

            submit = self.st.form_submit_button(label='Formalize!')

        if submit:
            if uploaded_file:
                self.req = user_req
                reqs_list = user_reqs_list
            else:
                self.req = default_req
                reqs_list = default_reqs_list

            if self.req:
                self.st.markdown(f"**Formalizing relations for the "
                                 f"requirement:**",
                                 unsafe_allow_html=True)
                self.st.markdown(f"{self.req}", unsafe_allow_html=True)
                req_id = ''
                linked_item = ''
                for s in reqs_list:
                    if s['req_desc'] == self.req:
                        req_id = s['req_id']
                        linked_item = s['linked_item']
                self.st.markdown(
                    f"**Requirement ID:** {req_id} **Linked Item:** {linked_item}",
                    unsafe_allow_html=True)

    def display_decomp_req(self, decomp_req):
        for clause in decomp_req:
            self.st.markdown(clause)

    @staticmethod
    def chunk_text(clause_text):
        sp = clause_text.split(' ')
        new_sp = []
        lt = 0
        for word in sp:
            new_sp.append(word)
            lt += len(word)
            if lt > 100:
                new_sp.append('<br></br>')
                lt = 0
        return ' '.join(new_sp)

    def display_relation_elements(self, idx: int, relation: Relation):
        if self.version == Version.SEM_SIM:
            self.display_v2(idx, relation)
        else:
            self.display_v1(idx, relation)

    def display_v1(self, idx: int, relation: Relation):
        print(relation)
        clause_text = relation.clause
        elements: List[str] = [relation.syntax.subj, relation.syntax.obj,
                               relation.syntax.action, relation.condition]
        element_types: List[str] = ["SIGNAL", "PARAMETER", "ACTION",
                                    "CONDITION"]

        print(relation.condition)

        for element, element_type in zip(elements, element_types):
            if str(element) == '':
                continue
            if str(element) in clause_text:
                el = element
            else:
                el = re.sub('_', ' ', str(element))
            clause_text = re.sub(el,
                                 f"<span class='highlight {element_type.lower()}'> {el} <sub>{element_type}</sub></span>",
                                 clause_text)
        # TODO: chunk text properly
        # clause_text = self.chunk_text(clause_text)
        relation_text = relation.get_text()

        # if relation.neg_or_pos == 'neg':
        #    relation_text = f"**{relation.condition} (** {relation.left} ! {relation.symbol} {relation.right} **)**"
        # else:
        #    relation_text = f"**{relation.condition} (** {relation.left} {relation.symbol} {relation.right} **)**"

        with self.st.expander(f'Relation for Clause {idx + 1}'):
            with self.st.container():
                col1, col2 = self.st.columns([5, 30])
                col1.markdown("**Entities**", unsafe_allow_html=True)
                col2.markdown(clause_text, unsafe_allow_html=True)
            with self.st.container():
                col1, col2 = self.st.columns([5, 30])
                col1.markdown("**Relation**", unsafe_allow_html=True)
                col2.markdown(relation_text, unsafe_allow_html=True)

    def display_v2(self, idx: int, relation: Relation):
        _, signals_in, signals_out, parameters = load_req_signals()
        print(relation)
        clause_text = relation.clause
        elements: List[str] = [relation.syntax.subj['name'],
                               relation.syntax.obj,
                               relation.syntax.action,
                               relation.condition]
        element_types: List[str] = ["SIGNAL", "PARAMETER", "ACTION",
                                    "CONDITION"]

        print(relation.condition)

        for element, element_type in zip(elements, element_types):
            if str(element) == '':
                continue
            if str(element) in clause_text:
                el = element
            else:
                el = re.sub('_', ' ', str(element))
            clause_text = re.sub(el,
                                 f"<span class='highlight {element_type.lower()}'> {el} <sub>{element_type}</sub></span>",
                                 clause_text)
        # TODO: chunk text properly
        # clause_text = self.chunk_text(clause_text)

        if relation.neg_or_pos == 'neg':
            relation_text = f"**{relation.condition} (** {relation.left} ! {relation.symbol} {relation.right} **)**"
        else:
            relation_text = f"**{relation.condition} (** {relation.left} {relation.symbol} {relation.right} **)**"

        with self.st.expander(f'Relation for Clause {idx + 1}'):
            with self.st.container():
                col1, col2 = self.st.columns([5, 30])
                col1.markdown("**Entities**", unsafe_allow_html=True)
                col2.markdown(clause_text, unsafe_allow_html=True)
            with self.st.container():
                col1, col2 = self.st.columns([5, 30])
                col1.markdown("**Relation**", unsafe_allow_html=True)
                col2.markdown(relation_text, unsafe_allow_html=True)
            with self.st.container():
                col1, col2 = self.st.columns([5, 30])
                col1.markdown("**Metadata**", unsafe_allow_html=True)
                tab1, tab2 = col2.tabs([relation.syntax.subj['name'], relation.syntax.obj])
                for key in relation.syntax.subj:
                    tab1.markdown(
                        f"<i>{re.sub('_', ' ', key.capitalize())}</i>: {relation.syntax.subj[key]}",
                        unsafe_allow_html=True)
                for param in parameters:
                    if param['name'] == relation.syntax.obj:
                        for key in param:
                            tab2.markdown(
                                f"<i>{re.sub('_', ' ', key.capitalize())}</i>: {param[key]}",
                                unsafe_allow_html=True)

    def display_full_relation(self, structure: Structure):
        self.st.markdown(f"**This yields us the following relation model:**",
                         unsafe_allow_html=True)
        text = ""
        if structure.if_text:
            text += f"<span class='highlight signal'> if </span> **(** {structure.if_text.strip()} **)**"
            text += "<br><br>"
        if structure.then_text:
            text += f"<span class='highlight parameter'> then </span> **(** {structure.then_text.strip()} **)**"
            text += "<br><br>"
        if structure.until_text:
            text += f"<span class='highlight condition'> until </span> **(** {structure.until_text.strip()} **)**"
            text += "<br><br>"

        with self.st.container():
            _, col, _ = self.st.columns([5, 50, 5])
            col.markdown(text, unsafe_allow_html=True)
