# auFedLegCat

## Description: Australian Federal Legislation DCAT Dataset Entries

@author: [ORCID 0009-0007-8434-7325](https://orcid.org/0009-0007-8434-7325)

### Goals

A DCAT catalog of Australian Legislation is an example of a utility that will assist with indexing references to Australian Federal Law.

The immediate goals for this example includes a) generation of datasets from Australian Legislation b) catalog datasets in a DCAT Catalog, c) the ability to update (regenerate) the catalog as the law changes.

### Generate DCAT Dataset

The Python script to create DCAT Datasets from Australian Legislation including:

- Metadata from an Act or Legislative Instrument from: [https://www.legislation.gov.au/](https://www.legislation.gov.au/) search results

- Table of contents structure (as ToC metadata) for instances of ACTs or Legislative Instruments

- A SKOS Vocabulary that enables use as [dcat:theme](https://www.w3.org/TR/vocab-dcat-3/#Property:resource_theme) for DCAT dataset and related [DCAT catalog](https://www.w3.org/TR/vocab-dcat-3/#Class:Catalog) that reflects the structure of legislation (derived from source)

The (Python) application that scrapes the Act or Legislative Instrument (legilsation) is: [genericDatasetExample.py](./auFedLegCat/pysource/genericDatasetExample.py)

Outputs from running the script are written to the following directory: [output directory](./auFedLegCat/vocdata).

Where search results results in multiple pages of results, each page is parsed.

The application configuration file is: [config.py](./auFedLegCat/pysource/config.py)

config.py provides the application the following name/value pair for configuring application target/output:

| Name               | Value Example                                                                                                                                                                                                           | Description                                                                                                                                   |
|:------------------:| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `tableOfContents`  | `True`                                                                                                                                                                                                                  | Mine the table of contents structure, (metadata) content, and hypterlinks. Omit this mining and output if set to False                        |
| `pageMetadata`     | `True`                                                                                                                                                                                                                  | Mine the Dubline Core Terms metadata (as a CSV file) from  Legislative Instrument or ACT webpage. Omit this mining and output if set to False |
| `detailedMetadata` | `True`                                                                                                                                                                                                                  | Mine the metadata from the Legislative Instrument or ACT Details webpage. Omit this mining and output if set to False                         |
| `pagelimit`        | `<an integer that states the page limit of search page results>`                                                                                                                                                        | Limit the parsing of search result pages from [https://www.legislation.gov.au/](https://www.legislation.gov.au/)                              |
| `outputFolder`     | `<a local path to and output directory relative to the script path>`                                                                                                                                                    | The path to the directory where output CSV files will be written.                                                                             |
| `catalogName`      | `<a single word tag for the catalog name to be gererated>`                                                                                                                                                              | Used to tag catalog URI, including datasets indexed in the catalog.                                                                           |
| `catalogTarget`    | `https://www.legislation.gov.au/search/text(%22agriculture%22,nameAndText,contains)/status(InForce)/pointintime(Latest)/collection(Act,AdministrativeArrangementsOrder)/sort(searchcontexts%2Ftext%2Frelevance%20desc)` | Copied (and pasted) URL for search at [https://www.legislation.gov.au/](https://www.legislation.gov.au/)                                      |

### Themes

The taxonomy file [legilsationConcepts.ttl](./auFedLegCat/voc/legislationConcepts.ttl) contains a SKOS concept scheme for the structures in Australian Legislative Instruments and Acts, as a SKOS taxonomy.

### Script

The Python script file: [mineLegIdentifiers.py](./auFedLegCat/pysource/mineLegIdentifiers.py) writes a DCAT catalog file (with the `catalogName`) for the datasets that are scraped.

The Python script file: [genericDatasetExample.py](./auFedLegCat/pysource/genericDatasetExample.py) writes a DCAT Dataset file for to output for referencing in a DCAT Catalog.

The Python script file: [outputTripleCount.py](./auFedLegCat/pysource/genericDatasetExample.py) returns triple count for generated files to the console.

### Script Dependencies

- Python 3.8.10

- `pip install requests`

- `pip install beautifulsoup4`

- `pip install rdflib`

- `pip install threading`
