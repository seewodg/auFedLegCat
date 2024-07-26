# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:13:48 2024

@author: https://orcid.org/0009-0007-8434-7325
Template the RDF below, then alter collect_links.py to handle name value pairs and call collect_links to populate the RDF
in this. The goal is to a) create the dataset b) catalog the dataset, b) validate dataset on publilshing c) eventually populate
a provenance graph with changes resulting from the changed dataset (changed from publishing).
"""
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF , XSD, SCHEMA, DCAT, DCTERMS, OWL, RDFS, RDF
import collect_links

# Create a Graph
g = Graph()

# Create an RDF URI node to use as the subject for multiple triples
donna = URIRef("http://example.org/donna")

if __name__ == "__main__":
    # Get vars from conf file
    var = {}
    with open("./LinkMiner/globals.txt") as conf:
            for line in conf:
                    if ";" in line:
                            name, value = line.split(";")
                            var[name] = str(value).rstrip()
    globals().update(var)
    global legID
    legID = globals().get('legID')
    leg_seed_url = f"https://www.legislation.gov.au/{legID}/latest/text" # e.g.https://www.legislation.gov.au/F2021L00319/latest/text
    