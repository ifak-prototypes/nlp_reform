# Automated Requirement Formalization using Product Design Specifications

We present a new approach based on Natural Language Processing and textual similarity using requirements and product design specifications to generate human- and machine-readable models. The method is evaluated on an industrial use case from the railway domain and achieved an average accuracy of more than 90\% and an exact match of the entire models of about 55\%. 

<p align="center">
  <img src="nlp_reform/data/example.png"  width="500"/>
</p>

<!-- <img align="center" width="500" src="nlp_reform_pipeline/data/example.png"> -->

# Getting started

## Installation
We recommend **Python 3.8** or higher.

To install the requirements,

``pip install -r requirements.txt``

## Setup
You can set the configuration parameters in ``nlp_reform/config.ini``.

- The configuration parameter ``signal_detection`` helps you choose how to detect signals from the requirements. You can choose from the following options:
    - ``tf`` runs with Term frequency,
    - ``fw`` runs with Fuzzy-Wuzzy,
    - ``bert`` runs with the pre-trained BERT model,
    - ``tf+fw`` runs with a combination of both term frequency and Fuzzy-Wuzzy, and,
    - ``bert+fw`` runs with a combination of both the pre-trained BERT model and Fuzzy-Wuzzy.

    **Note:** The default paremter for signal detection is set as ``bert+fw`` and the fastest option is ``tf``.
- The configuration parameter ``param_detection`` helps you choose how to detect parameters from the requirements. You can choose from the follwoing options: 
    - ``PD`` runs as a paraphrase detection task,
    - ``TE`` runs as a textual entailment task, and
    - ``SA`` runs as a sentiment analysis task. 

    **Note:** The default paremter for parameter detection is set as ``TE`` and the fastest option is ``PD``.
- The configuration parameter ``method`` helps you choose which stages of the pipeline to run. You can choose from the following options: 
    - ``Decomposition`` runs the decomposition stage, 
    - ``Signal`` runs the signal detection stage with the configuration parmeter you chose for ``signal_detection``, 
    - ``Parameter`` runs the parameter detection stage with the configuration parameter you chose for ``param_detection``, and
    - ``Pipeline`` runs the whole pipeline with all the stages mentioned above. 

## Run the tool

To run the tool,

```
cd nlp_reform
python main.py
```


# Citation

Please cite the publication in case you use our work or parts of it.

```bibtex
@inproceedings{groepler2022automated,
    title = "Automated Requirement Formalization using Product Design Specifications",
    author = "Gröpler, Robin and Kutty, Libin and Sudhi, Viju and Smalley, Daran",
    booktitle = "REFSQ Workshops",
    month = "03",
    year = "2022",
}
```
