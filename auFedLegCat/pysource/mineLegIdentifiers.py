# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 13:37:46 2024

@author: marcu
"""
from rdflib import Graph, URIRef, XSD, DCAT, SKOS, DCTERMS, RDF, RDFS, Literal, OWL
from bs4 import BeautifulSoup
# from bs4.dammit import EncodingDetector
# import requests
import datetime
from time import sleep
import os.path
from config import CONFIG_INFO
import urllib.parse
import genericDatasetExample as gendataset
import re
import threading
import time

def init():
    # get the target URL - e.g. search URL from https://legislation.gov.au
    target = CONFIG_INFO["catalogTarget"]
    global source_url; source_url = urllib.parse.unquote(target)
    global outputFolder; outputFolder = CONFIG_INFO["outputFolder"]
    global catalogName; catalogName = CONFIG_INFO["catalogName"]
    global pagelimit; pagelimit = CONFIG_INFO["pagelimit"]
    g = Graph()
    
    # Run scraping in a separate thread to avoid event loop issues
    thread = threading.Thread(target=scrapeSearchResults, args=(g, source_url))
    thread.start()
    thread.join()

def load_next_page(page, wait_time=10000):
    """
    Load the next page of search results by clicking the next page button.
    Uses Playwright for more reliable JavaScript handling.
    
    Args:
        page: Playwright page object
        wait_time: Maximum time to wait for page to load (in milliseconds)
    
    Returns:
        True if next page was loaded successfully, False otherwise
    """
    try:
        # Find the "next page" button specifically in the results table
        next_button = page.get_by_role("table").get_by_role("button", name="go to next page")
        
        # Check if the button exists
        if not next_button.is_visible():
            print("Next page button not found or not visible")
            return False
        
        # Check if the button is enabled (disabled buttons won't navigate)
        if not next_button.is_enabled():
            print("Next page button is disabled - reached last page")
            return False
        
        print("Next page button found, clicking...")
        
        # Scroll to ensure the button is visible
        next_button.scroll_into_view_if_needed()
        time.sleep(1)
        
        # Click the next button
        next_button.click()
        
        # Wait for navigation to complete
        page.wait_for_load_state("networkidle", timeout=wait_time)
        
        # Additional wait for content to render
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"Error loading next page: {e}")
        return False


def scrapeSearchResults(g, source_url):
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            parser = 'html.parser'
            baseURL = "http://example.org/au/leg/catalog/" + catalogName.lower() +'/'
            namesp = URIRef(baseURL)
            
            # Check if there is an existing catalog to append to
            fileToCheck = outputFolder + catalogName + ".ttl"
            if os.path.exists(fileToCheck):
                g.parse(fileToCheck, format="ttl")
            else:
                newCatalogHeader(g, namesp)
            
            # Navigate to search page using Playwright
            page.goto(source_url, wait_until="networkidle")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            page_number = 1
            
            # Main scraping loop
            while True:
                print(f"\n--- Scraping Page {page_number} ---")
                
                # Get current page content and parse with BeautifulSoup
                page_content = page.content()
                soup = BeautifulSoup(page_content, parser)
                
                # Add links from current page
                addReferencesToCatalog(g, soup, namesp)
                
                # Try to load next page if less than or equal to the page limit configuration, otherwise break
                if load_next_page(page) and page_number < pagelimit + 1:
                    page_number += 1
                    print(f"Successfully loaded page {page_number}")
                else:
                    print("No more pages available or error loading next page")
                    break
            
        except Exception as e:
            print(f"Error in main scraping loop: {e}")
        finally:
            browser.close()

def addReferencesToCatalog(g, soup, namesp):
    # itterate through the legislation IDs returned in a scrape and add them as dcat:Dataset references in the catalog
    cnt = 1
    if addDatasetReferences(g, soup, namesp, cnt) is True:
        print("Successfully cataloged datasets")
        
    else: print("No datasets cataloged")

def newCatalogHeader(g, namesp):
    # begin building catalog graph - first the prefixes
    catPrefix = catalogName.lower()
    g.bind(catPrefix, namesp)
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
    g.add((namesp, DCTERMS.title, Literal("Australian Legislation Catalog - " + catalogName, lang="en")))
    g.add((namesp, RDFS.label, Literal("Australian Legislation Catalog - " + catalogName, lang="en")))
    g.add((namesp, DCTERMS.alternative, Literal(catalogName + " Catalog", lang="en")))
    g.add((namesp, DCTERMS.description, Literal("The Australian Legislation Catalog Example, short-named" + catalogName + ", is a structured and open-source catalog that refers to RDF datasets generated from Australian Legislation. It was designed to provide an example for research, and could be applied in any applications.""", lang="en")))
    g.add((namesp, URIRef("https://w3id.org/ontouml-models/vocabulary#storageUrl"), URIRef("https://github.com/seewodg/auFedLegCat/tree/main/auFedLegCat/catalog")))
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
    # for span in soup.find_all('span', {'class': 'title-id'}, recursive=True):
    for link in soup.find_all('a'):
        # if span is not None:
        if use_regex(link.get('href')):
            legid = link.get('href')
            resource = f"http://example.org/au/leg/dataset{legid}/"
            if not (namesp, DCAT.dataset, URIRef(resource)) in g: # first check to see if dataset is not aleady cataloged
                fileToCheck = outputFolder + legid + ".ttl" # then check to ensure file is not already in folder
                print(fileToCheck)
                if not os.path.exists(fileToCheck):
                    addDataset(legid)
                    g.add((namesp, DCAT.dataset, URIRef(resource))) # add the dcat:Dataset reference to the catalog
                    # print(f"Span: {legid} Count: {cnt}")
                    cnt += 1
                    sleep(10) # waite 10 seconds out of respect for robots.txt
    g.serialize(outputFolder + catalogName + '.ttl', format='ttl') # generate the dcat:Dataset
    if (namesp, DCAT.dataset, None) in g:
        return True
    else: return False
    
def addDataset(legid):
    print("GOT HERE")
    result = gendataset.init(legid) # create the dataset
    return result

def use_regex(input_text):
    pattern = re.compile(r"^/[A-Z0-9]+/[A-Za-z]+$")
    return pattern.match(input_text)

if __name__ == "__main__":
    init()