# auFedLegCat

## Description: Australian Federal Legislation DCAT Dataset Entries

@author: [ORCID 0009-0007-8434-7325](https://orcid.org/0009-0007-8434-7325)
Template the RDF below, then alter collect_links.py to handle name value pairs and call collect_links to populate the RDF
in this. The goal is to a) create the dataset b) catalog the dataset, b) validate dataset on publilshing c) eventually populate
a provenance graph with changes resulting from the changed dataset (changed from publishing).

The Python script to create CSV of legilsation is: [collect_links.py](./auFedLegCat/auFedLegCat/pysource/collect_links.py)

The collect_links.py script scrapes (mines) page metadata and table of contents from Legilsative Instruments and Acts at [https://www.legislation.gov.au/](https://www.legislation.gov.au/), and creates three outputs, depending on the settings in global.txt

The configuration file for the collect_links script is: [globals.txt](./auFedLegCat/auFedLegCat/pysource/globals.txt)

globals.txt is populated with the following semicolon seperated name/value pairs:

 

| Name             | Value Example                             | Description                                                                                                                                   |
| ---------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| legID            | C1901A00006                               | The Legislative Instrument or ACT ID to target for mining (scraping).                                                                         |
| tableOfContents  | True                                      | Mine the table of contents structure, (metadata) content, and hypterlinks (as a CSV file). Omit this mining and output if set to False        |
| pageMetadata     | True                                      | Mine the Dubline Core Terms metadata (as a CSV file) from  Legislative Instrument or ACT webpage. Omit this mining and output if set to False |
| detailedMetadata | True                                      | Mine the metadata (as a CSV file) from the Legislative Instrument or ACT Details webpage. Omit this mining and output if set to False         |
| outputFolder     | <some local path to and output directory> | The path to the directory where output CSV files will be written.                                                                             |
