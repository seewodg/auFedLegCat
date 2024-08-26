# auFedLegCat

## Description: Australian Federal Legislation DCAT Dataset Entries

@author: [ORCID 0009-0007-8434-7325](https://orcid.org/0009-0007-8434-7325)

### Goals

A DCAT catalog of Australian Legislation is an example of a utility that will assist with indexing references to standards and legislation that includes the ability to Profile parts of the catalog where a Profile is pointed to from a Varifiable Credential using a single URL.

The immediate goals for this example includes a) generation of datasets from Australian Legislation b) catalog datasets in a DCAT Catalog, b) validate dataset on publilshing c) eventually populate a provenance graph with changes resulting from the changed dataset (changed from manual publishing).

### Generate DCAT Dataset

The Python script to create DCAT Datasets from Australian Legislation including:

- Metadata from an Act or Legislative Instrument from: [https://www.legislation.gov.au/](https://www.legislation.gov.au/) details page

- Table of contents structure (as ToC metadata) for instances of ACTs or Legislative Instruments

- A SKOS Vocabulary that enables use as [dcat:theme](https://www.w3.org/TR/vocab-dcat-3/#Property:resource_theme) for DCAT dataset and related [DCAT catalog](https://www.w3.org/TR/vocab-dcat-3/#Class:Catalog) that reflects the structure of legislation (derived from source)

The (Python) application that scrapes the Act or Legislative Instrument (legilsation) is: [genericDatasetExample.py](./auFedLegCat/pysource/genericDatasetExample.py)

Outputs from running the script are written to the following directory: [output directory](./auFedLegCat/vocdata).

The application configuration file is: [config.py](./auFedLegCat/pysource/config.py)

config.py provides the application the following name/value pair for configuring application target/output:

| Name             | Value Example                               | Description                                                                                                                                   |
| ---------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| legID            | `C1901A00006`                               | The Identifier for the Legislative Instrument or ACT - target for mining (scraping).                                                          |
| tableOfContents  | `True`                                      | Mine the table of contents structure, (metadata) content, and hypterlinks. Omit this mining and output if set to False                        |
| pageMetadata     | `True`                                      | Mine the Dubline Core Terms metadata (as a CSV file) from  Legislative Instrument or ACT webpage. Omit this mining and output if set to False |
| detailedMetadata | `True`                                      | Mine the metadata from the Legislative Instrument or ACT Details webpage. Omit this mining and output if set to False                         |
| outputFolder     | `<some local path to and output directory>` | The path to the directory where output CSV files will be written.                                                                             |

### Themes

The taxonomy file [legilsationConcepts.ttl](./auFedLegCat/voc/legislationConcepts.ttl) contains a SKOS concept scheme for the structures in Australian Legislative Instruments and Acts, as a SKOS taxonomy.

### Script

The Python script file: [genericDatasetExample.py](./auFedLegCat/pysource/genericDatasetExample.py) writes a DCAT Dataset file for to output for referencing in a DCAT Catalog
