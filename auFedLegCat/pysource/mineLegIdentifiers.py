# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 13:37:46 2024

@author: marcu
"""
from rdflib import Graph, URIRef, XSD, DCAT, SKOS, DCTERMS, RDF, RDFS, Literal, OWL
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
import datetime
from time import sleep
import os.path
from config import CONFIG_INFO
import urllib.parse
import genericDatasetExample as gendataset

def init():
    # get the target URL - e.g. search URL from https://legislation.gov.au
    target = CONFIG_INFO["catalogTarget"]
    global source_url; source_url = urllib.parse.unquote(target)
    global outputFolder; outputFolder = CONFIG_INFO["outputFolder"]
    g = Graph()
    # scrape the search results to build the catalog and datasets
    scrapeSearchResults(g, source_url)

def scrapeSearchResults(g, source_url):
    parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
    resp = requests.get(source_url)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
    baseURL = "http://example.org/au/leg/catalog/"
    namesp = URIRef(baseURL)
    # check if there is an existing catalog to append to
    fileToCheck = outputFolder + "lawCatalog.ttl"
    if os.path.exists(fileToCheck):
        # print(fileToCheck)
        g.parse(fileToCheck, format="ttl")
    else:
        newCatalogHeader(g, namesp)
    addReferencesToCatalog(g, soup, namesp)
    
    
    
def addReferencesToCatalog(g, soup, namesp):
    # itterate through the legislation IDs returned in a scrape and add them as dcat:Dataset references in the catalog
    cnt = 1
    if addDatasetReferences(g, soup, namesp, cnt) is True:
        print("Successfully cataloged datasets")
    else: print("No datasets cataloged")

def newCatalogHeader(g, namesp):
    # begin building catalog graph - first the prefixes
    g.bind("legcat", namesp)
    skosURL = "http://example.org/au/leg/concepts/"
    g.bind("legcons", skosURL)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('skos', SKOS)
    g.bind('dcat', DCAT)
    g.bind('dct', DCTERMS)
    g.bind('xsd', XSD)
    g.bind('owl', OWL)
    g.bind('vcard', URIRef("http://www.w3.org/2006/vcard/ns#"))
    g.bind('ocmv', URIRef("https://w3id.org/ontouml-models/vocabulary#"))
    # build the catalog minus the dcat:Datasets
    g.add((namesp, RDF.type, OWL.Class))
    g.add((namesp, RDF.type, DCAT.Resource))
    g.add((namesp, RDF.type, DCAT.Catalog))
    g.add((namesp, DCTERMS.title, Literal("Australian Legislation Catalog Example", lang="en")))
    g.add((namesp, RDFS.label, Literal("Australian Legislation Catalog Example", lang="en")))
    g.add((namesp, DCTERMS.alternative, Literal("UNTP/AuLeg Catalog", lang="en")))
    g.add((namesp, DCTERMS.description, Literal("""The Australian Legislation Catalog Example, short-named UNTP/AuLeg Catalog, is a structured and open-source catalog that refers to RDF datasets generated from Australian Legislation. It was designed to provide an example for research to support UNTP Digital Product Passports, but could be applied in other applications.""", lang="en")))
    g.add((namesp, URIRef("https://w3id.org/ontouml-models/vocabulary#storageUrl"), URIRef("https://github.com/seewodg/auFedLegCat/tree/main/auFedLegCat/catalog/")))
    g.add((namesp, DCAT.themeTaxonomy, URIRef("http://example.org/au/leg/concepts/")))
    # vcard = URIRef("http://www.w3.org/2006/vcard/ns#")
    # avcard = g.resource(vcard)
    # assert isinstance(avcard, URIRef("http://www.w3.org/2006/vcard/ns#Individual"))
    # assert avcard.identifier is vcard
    # avcard.set(URIRef("http://www.w3.org/2006/vcard/ns#fn"), Literal("Marcus Jowsey"))
    # avcard.set(URIRef("http://www.w3.org/2006/vcard/ns#hasEmail"), URIRef("seewodg@gmail.com"))
    # assert avcard.graph is g
    # g.add((namesp, DCAT.contactPoint, avcard))
    g.add((namesp, DCTERMS.bibliographicCitation, Literal("Marcus Jowsey et al. (UNECE Team 2024).", lang="en")))
    g.add((namesp, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by-sa/4.0/")))
    g.add((namesp, DCTERMS.issued, Literal("2024-06-16T17:53:16.365007", datatype=XSD['dateTime'])))
    g.add((namesp, DCTERMS.modified, Literal(datetime.datetime.now(), datatype=XSD['dateTime'])))
    g.add((namesp, DCTERMS.publisher, URIRef("https://orcid.org/0009-0007-8434-7325")))
    g.add((namesp, DCTERMS.creator, URIRef("https://orcid.org/0009-0007-8434-7325")))
    
def addDatasetReferences(g, soup, namesp, cnt):
    for span in soup.find_all('span', {'class': 'title-id'}, recursive=True):
        if span is not None:
            legid = span.string
            resource = f"http://example.org/au/leg/dataset/{legid}/"
            if not (namesp, DCAT.dataset, URIRef(resource)) in g: # first check to see if dataset is not aleady cataloged
                fileToCheck = outputFolder + legid + ".ttl" # then check to ensure file is not already in folder
                # print(fileToCheck)
                if not os.path.exists(fileToCheck):
                    addDataset(legid)
                    g.add((namesp, DCAT.dataset, URIRef(resource))) # add the dcat:Dataset reference to the catalog
                    # print(f"Span: {legid} Count: {cnt}")
                    cnt += 1
                    sleep(10) # waite 10 seconds out of respect for robots.txt
    g.serialize('./output/lawCatalog.ttl', format='ttl') # generate the dcat:Dataset
    if (namesp, DCAT.dataset, None) in g:
        return True
    else: return False
    
def addDataset(legid):
    result = gendataset.init(legid) # create the dataset
    return result

if __name__ == "__main__":
    init()