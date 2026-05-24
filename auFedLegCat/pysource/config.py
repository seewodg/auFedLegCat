# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 16:43:38 2024

@author: marcu
"""

CONFIG_INFO = {
    "tableOfContents": True,
    "pageMetadata": True,
    "detailedMetadata": True,
    "pagelimit": 2,
    "outputFolder": "../output/",
    "catalogName": "agricultureLawCatalog",
#    "catalogTarget": "https://www.legislation.gov.au/search/text(%22marine%22,nameAndText,contains)/status(InForce)/pointintime(Latest)/collection(Act,AdministrativeArrangementsOrder)/sort(searchcontexts%2Ftext%2Frelevance%20desc))"
    "catalogTarget": "https://www.legislation.gov.au/search/text(%22agriculture%22,nameAndText,contains)/status(InForce)/pointintime(Latest)/collection(Act,AdministrativeArrangementsOrder)/sort(searchcontexts%2Ftext%2Frelevance%20desc)"
}