# auFedLegCat

## Description: Australian Federal Legislation DCAT Dataset Entries

@author: [ORCID 0009-0007-8434-7325](https://orcid.org/0009-0007-8434-7325)

### Goals

A DCAT catalog of Australian Legislation will assist with indexing references to standards and legislation to point at from Profiles where a Profile is pointed to from a Varifiable Credential.

The immediate goals include a) create the dataset b) catalog the dataset, b) validate dataset on publilshing c) eventually populate a provenance graph with changes resulting from the changed dataset (changed from publishing).

### Generate CSV Guide

The Python script to create CSV of legilsation is: [collect_links.py](./auFedLegCat/pysource/collect_links.py)

Outputs from running the script are written to the following directory: [output directory](./auFedLegCat/vocdata).

The files optionally written to the output directory by the script include:

| File Name                  | Description                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `<legID>_data.csv`         | The links and associated metadata scraped from the table of contents for the Legislative Instrument or Act webpage |
| `<legID>_metadata.csv`     | The page metadata (Dublin Core Terms) scraped from the page header for the Legislative Instrument or Act webpage   |
| `<legID>_pagemetadata.csv` | The metadata from the Details scraped from the Legislative Instrument or Act Details webpage                       |

The collect_links.py script scrapes (mines) page metadata and table of contents from Legilsative Instruments and Acts at [https://www.legislation.gov.au/](https://www.legislation.gov.au/), and creates three outputs, depending on the settings in global.txt

The configuration file for the collect_links script is: [globals.txt](./auFedLegCat/pysource/globals.txt)

globals.txt is populated with the following semicolon seperated name/value pairs:

| Name             | Value Example                               | Description                                                                                                                                   |
| ---------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| legID            | `C1901A00006`                               | The Legislative Instrument or ACT ID to target for mining (scraping).                                                                         |
| tableOfContents  | `True`                                      | Mine the table of contents structure, (metadata) content, and hypterlinks (as a CSV file). Omit this mining and output if set to False        |
| pageMetadata     | `True`                                      | Mine the Dubline Core Terms metadata (as a CSV file) from  Legislative Instrument or ACT webpage. Omit this mining and output if set to False |
| detailedMetadata | `True`                                      | Mine the metadata (as a CSV file) from the Legislative Instrument or ACT Details webpage. Omit this mining and output if set to False         |
| outputFolder     | `<some local path to and output directory>` | The path to the directory where output CSV files will be written.                                                                             |

### RDF

The taxonomy file [legilsationConcepts.ttl](./auFedLegCat/voc/legislationConcepts.ttl) contains a SKOS concept scheme for the structures in Australian Legislative Instruments and Acts, as a SKOS taxonomy and includes owl:subClassOf declarations.

The Python script file: [rdfLegCatalogDataset.py](./auFedLegCat/pysource/rdfLegCatalogDataset.py) writes a DCAT Catalog file for CSV files written by [collect_links.py](./auFedLegCat/pysource/collect_links.py)
