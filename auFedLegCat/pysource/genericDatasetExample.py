# -*- coding: utf-8 -*-import csv
from rdflib import Graph, URIRef, XSD, DCAT, SKOS, DCTERMS, RDF, RDFS, Literal, SDO, OWL, Namespace
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
from html import unescape
import unicodedata
import datetime

def scrapeMetaPage(g, legID, source_url): # capture metadata from the legislation details page - lists legislation metadata
    print(f"Legislation Metadata Details Page https://www.legislation.gov.au/{legID}/latest/details scraping has begun")
    try:
        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        stat = ""
        admin = ""
        vers = ""
        titleID = ""
#        regDate = ""
        baseURL = f"http://example.org/au/leg/dataset/{legID}/"
        nspace = URIRef(baseURL)
        for span in soup.find_all('span', attrs={'class':'badge badge-default badge-size-large bg-success'}): # Legislation Status
            stat = span.string
            break
        if not stat == "":
            stat = stat.strip()
            stat = stat.replace('\n', ' ').replace('\r', '')
            g.add((nspace, SDO.status, Literal(stat)))
        for span in soup.find_all('span', attrs={'class':'item-id small fw-bold'}): # Latest Version
            vers = span.string
            break
        if not vers == "":
            vers = vers.replace('\n', ' ').replace('\r', '')
            g.add((nspace, SDO.version, Literal(vers)))
        for ul in soup.find_all('ul', attrs={'class':'list-group list-unstyled ms-3'}): # Administered By
            licnt = 0
            for li in ul.find_all('li'):
                sadmin = li.string
                if len(sadmin) > 0:
                    if licnt > 0:
                        admin += " - " + sadmin
                        licnt + 1
                    else:
                        admin = sadmin
                        licnt + 1
        if not admin == "":
            admin = admin.replace('\n', ' ').replace('\r', '')
            admin = admin.strip()
            g.add((nspace, DCTERMS.publisher, Literal(admin)))
        for div in soup.find_all('div', attrs={'class':'col-lg-9 title-id'}): # Title ID
            titleID = div.string
            titleID.strip()
            break
        if not titleID == "":
            g.add((nspace, SDO.identifier, Literal(titleID)))
        return True
    except Exception as e:
          return e

def scrape(g, source_url, legID, outputFolder): # capture the legislation associated metadata for the legislation page, write the graph header, and pass miner for leg mining
    print("Legislation ToC scraping has begun")
    print(f"legilsation Identifier: {legID}")
    print(f"Legislation Webpage: {source_url}")
    try:
        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        
        # build first part of graph
        global baseURL
        baseURL = f"http://example.org/au/leg/dataset/{legID}/"
        nspace = URIRef(baseURL)
        g.bind("LegID", Namespace(nspace))
        global skosref
        skosref = URIRef("http://example.org/au/leg/concepts/")
        builder = "https://orcid.org/0009-0007-8434-7325"
        g.bind(':', Namespace(nspace))
        g.bind(legID, nspace) # the base URI
        g.bind('rdf', RDF)
        g.bind('rdfs', RDFS)
        g.bind('skos', SKOS)
        g.bind('dcat', DCAT)
        g.bind('dt', DCTERMS)
        g.bind("legcons", skosref)
        g.add((nspace, RDF.type, OWL.Ontology))
        g.add((nspace, RDF.type, DCAT.Dataset))
        g.add((nspace, DCTERMS.creator, Literal(builder, datatype=XSD.anyURI)))
        g.add((nspace, DCTERMS.created, Literal(datetime.datetime.now(), datatype=XSD.dateTime)))
        # get the page metadata
        key = ""
        value = ""
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs:
                name = meta.attrs['name']
                if not name.startswith("dcterms"): # don't capture this metadata so iterate the for loop
                    continue
                else:
                    key = name
                if 'content' in meta.attrs:  # For OpenGraph metadata
                    value = meta.attrs['content']
                    if key == "dcterms.title":
                        g.add((nspace, DCTERMS.title, Literal(value, lang="en-AU")))
                    elif key == "dcterms.identifier":
                        g.add((nspace, DCTERMS.identifier, Literal(value, datatype=XSD.anyURI)))
                    elif key == "dcterms.creator":
                        if ";" in value:
                            end = len(value)
                            index = value.index(";") + 2
                            value = value[index:end]
                            if "corporateName" in value:
                                index = value.index("corporateName") + 14
                                end = len(value)
                                value = value[index:end]
                        g.add((nspace, DCTERMS.Agent, Literal(value, lang="en-AU")))
                    elif key == "dcterms.publisher":
                        g.add((nspace, DCTERMS.source, Literal(value, lang="en-AU")))
                    elif key == "dcterms.description":
                        g.add((nspace, DCTERMS.description, Literal(value, lang="en-AU")))
                    elif key == "dcterms.date":
                        end = len(value)
                        beg =len("scheme=dcterms.ISO8601; ")
                        value = value[beg:end]
                        g.add((nspace, DCTERMS.date, Literal(value, datatype=XSD.dateTime)))
                    elif key == "dcterms.subject":
                        g.add((nspace, DCTERMS.subject, Literal(value, lang="en-AU")))
        # get metadata from the legislation details page
        if legID != None and globals().get('detailedMetadata') == 'True':
            result = scrapeMetaPage(g, legID, f"https://www.legislation.gov.au/{legID}/latest/details") # e.g.https://www.legislation.gov.au/F2021L00319/latest/details
            if result != True:
                return result
        # add dcat theme
        g.add((nspace, DCAT.theme, URIRef(skosref + "ToC")))
        # add imports
        g.add((nspace, OWL.imports, URIRef(skosref)))
        # scrape data for DCAT dataset
        tocScrape(g, soup, nspace)
        # an arry of classification concepts
#        global lawCategory
#        lawCategory = ["Volume", "Part", "Chapter", "Schedule", "Endnotes", "Division", "Subdivision", "Section", "Item"]
        # add the classes
        global vol
        vol = "Volume"
        global chap
        chap = "Chapter"
        global sch
        sch = "Schedule"
        global part
        part = "Part"
        global endn
        endn = "Endnotes"
        global divis
        divis = "Division"
        global sub
        sub = "Subdivision"
        global sec
        sec = "Section"
        global it
        it = "Item"
        # write the output (turtle) file
        g.serialize(destination=outputFolder + legID + '.ttl', format='ttl')
        return True
        return g
    except Exception as e:
        return e

def tocScrape(g, soup, nspace):
    try:
        cnt = 0
        for div in soup.find_all('div', {'class': 'toc-body flex-grow-1'}, recursive=True):
            if div is not None:
                # print(adiv)
                ul = div.find('ul')
                if ul is not None:
                    for toc in ul.find_all('li', {'class': 'toc-link'}, recursive = False):
                        if toc is not None:
                            link = toc.find('a')
                            if link is not None:
                                cnt = cnt + 1
                                heading = link.string
                                # print(heading)
                                heading = cleanCruft(str(heading))
                                leader = URIRef(nspace + str(cnt))
                                # add top level menu items to graph
                                if addNode(g, cnt, heading, leader, link) == True:
                                    # print(leader)
                                    ## check for children and if found, recurse
                                    if checkForChildren(toc) == True:
                                        kids = toc.findChildren("ul" , recursive=False)
                                        for kid in kids:
                                            ccnt = childTocScrape(g, kid, nspace, leader, cnt)
                                            if ccnt > cnt: cnt = ccnt
                                            # print(cnt)
    except Exception as e:
        return e

def childTocScrape(g, soup, nspace, parent, cnt):
    try:
        for toc in soup.find_all('li', {'class': 'toc-link'}, recursive = False):
            if toc is not None:
                link = toc.find('a')
                if link is not None:
                    cnt = cnt + 1
                    heading = link.string
                    # print(heading)
                    heading = cleanCruft(str(heading))
                    leader = URIRef(nspace + str(cnt))
                    # add top level menu items to graph
                    if addNode(g, cnt, heading, leader, link) == True:
                        if linkToParent(g, leader, parent) == True:
                            # print(leader)
                            if checkForChildren(toc) == True:
                                    kids = toc.findChildren("ul" , recursive=False)
                                    for kid in kids:
                                        ccnt = childTocScrape(g, kid, nspace, leader, cnt)
                                        if ccnt > cnt: cnt = ccnt
        return cnt
    except Exception as e:
        return e

def checkForChildren(toc):
    kids = toc.findChildren("ul" , recursive=False) # grab the next submenu item
    # print(len(kids))
    if kids is not None and len(kids) > 0: # if submenu exists...
        # print(len(kids))
        return True
    else: return False

def addNode(g, cnt, heading, leader, link):
    try:
        # add some triples
        # leader = URIRef(leader + str(cnt))
        # print(f"Link: {link['href']}")
        if not (leader, None, None) in g:
            # i = 0
            # while i < len(lawCategory) - 1:
            #     if not i < 8:
            #         if heading.startswith(lawCategory[i]):
            #             if not (URIRef(baseURL + heading), RDF.type, OWL.Class) in g:
            #                 nodeHeader(g, lawCategory[i])
            #                 buildNode(g, lawCategory[i], cnt, leader, heading, link)      
            #     elif i < 7:
            #         if not (URIRef(baseURL + heading), RDF.type, OWL.Class) in g:
            #             nodeHeader(g, lawCategory[i])
            #             buildNode(g, lawCategory[i], cnt, leader, heading, link)                      
            #     i = i + 1

            if heading.startswith(vol):
                if not (URIRef(baseURL + vol), RDF.type, OWL.Class) in g:
                    nodeHeader(g, vol)
                buildNode(g, vol, cnt, leader, heading, link)
            elif heading.startswith(chap):
                if not (URIRef(baseURL + chap), RDF.type, OWL.Class) in g:
                    nodeHeader(g, chap)
                buildNode(g, chap, cnt, leader, heading, link)
            elif heading.startswith(sch):
                if not (URIRef(baseURL + sch), RDF.type, OWL.Class) in g:
                    nodeHeader(g, sch)
                buildNode(g, sch, sch, leader, heading, link)
            elif heading.startswith(part):
                if not (URIRef(baseURL + part), RDF.type, OWL.Class) in g:
                    nodeHeader(g, part)
                buildNode(g, part, cnt, leader, heading, link)
            elif heading.startswith(endn):
                if not (URIRef(baseURL + endn), RDF.type, OWL.Class) in g:
                    nodeHeader(g, endn)
                buildNode(g, endn, cnt, leader, heading, link)
            elif heading.startswith(divis):
                if not (URIRef(baseURL + divis), RDF.type, OWL.Class) in g:
                    nodeHeader(g, divis)
                buildNode(g, divis, cnt, leader, heading, link)
            elif heading.startswith(sub):
                if not (URIRef(baseURL + sub), RDF.type, OWL.Class) in g:
                    nodeHeader(g, sub)
                buildNode(g, sub, cnt, leader, heading, link)
            elif heading.startswith(sec):
                if not (URIRef(baseURL + sec), RDF.type, OWL.Class) in g:
                    nodeHeader(g, sec)
                buildNode(g, sec, cnt, leader, heading, link)
            else:
                if not (URIRef(baseURL + it), RDF.type, OWL.Class) in g:
                    nodeHeader(g, it)
                buildNode(g, it, cnt, leader, heading, link)
        if (leader, None, None) in g:
            return True
        else:
            return False
    except Exception as e:
        return e

# used when adding nodes - addNode(...)
def nodeHeader(g, headerVal):
    rdfComp = URIRef(baseURL + headerVal)
    sko = URIRef(skosref + headerVal)
    print(sko)
    g.add((rdfComp, RDF.type, OWL.Class))
    g.add((rdfComp, RDF.type, sko))
    g.add((rdfComp, RDF.type, SKOS.Concept))
    g.add((rdfComp, RDF.type, DCAT.Resource))
    g.add((rdfComp, RDFS.label, Literal(headerVal)))
    g.add((rdfComp, SKOS.prefLabel, Literal(headerVal)))
    
def buildNode(g, headingVal, cnt, leader, heading, link): # this is where the not is constructed, including its place in the SKOS taxonomy
    try:
        # print(f"heading: {heading}")
        prfx = headingVal[0].upper() + str(cnt)
        nodeURI = URIRef(skosref + headingVal)
        cleanHeading = cleanCruft(headingVal)
        g.add((leader, DCAT.accessURL, Literal(link['href'], datatype=XSD.anyURI)))
        g.add((leader, RDF.type, URIRef(baseURL + headingVal)))
        g.add((leader, RDF.type, nodeURI))
        g.add((leader, SKOS.definition, Literal(heading, lang="en-AU")))
        g.add((leader, SKOS.prefLabel, Literal(cleanHeading + ' ' + prfx, lang="en-AU")))
        g.add((leader, RDFS.comment, Literal(heading + ' - Abrievated Graph Key: ' + prfx, lang="en-AU")))
        g.add((leader, RDFS.label, Literal(cleanHeading + ' - ' + prfx + ' ' + heading, lang="en-AU")))
        return
    except Exception as e:
        return e

def linkToParent(g, leader, parent):
    # if not leader == parent: # do not allow self references
        g.add((leader, SKOS.narrower, parent))
        g.add((parent, SKOS.broader, leader))
        g.add((leader, DCTERMS.isPartOf, parent))
        g.add((parent, DCTERMS.hasPart, leader))
        return True
    # else: return False

            
    
def cleanCruft(test_str): # clean string of all non RDF-8 characters
    result = ''
    test_str = unescape(test_str)
    test_str = unicodedata.normalize('NFKD', test_str)
    test_str = unicodedata.normalize('NFKD', test_str)
    test_str = filter(lambda x: x.isalnum() or x.isspace(), test_str) # remove non alphanumeric characters and preserve whitespaces
    test_str = "".join(test_str) # reconstruct string
    # loop through the test string character by character
    for i in range(len(test_str)):
        # check if the current character is a digit and the previous character is an alphabet
        if test_str[i].isdigit() and result and result[-1].isalpha():
            # if so, add a space to the result string
            result += ' '
        # check if the current character is an alphabet and the previous character is a digit
        elif test_str[i].isalpha() and result and result[-1].isdigit():
            # if so, add a space to the result string
            result += ' ' # add the current character to the result string
        result +=  test_str[i]
    return result

def init():
    # Get vars from conf file
    var = {}
    with open("./LinkMiner/globals.txt") as conf:
            for line in conf:
                    if ";" in line:
                            name, value = line.split(";")
                            var[name] = str(value).rstrip()
    globals().update(var)
    tocMessage = ""
    pageMetaMessage = ""
    result = True
    g = Graph()
    # set some globals
    global legID
    legID = globals().get('legID')
    leg_seed_url = f"https://www.legislation.gov.au/{legID}/latest/text" # e.g.https://www.legislation.gov.au/F2021L00319/latest/text
    if legID != None and globals().get('tableOfContents') == 'True':
        result = scrape(g, leg_seed_url, legID, globals().get('outputFolder'))
        tocMessage = "Page Table of Contents"
        pageMetaMessage = "Details Page Metadata"
        if result == True:
            print(f'Success! Mined {pageMetaMessage} and {tocMessage}')
        else:
            print(f"\nOops, That doesn't seem right!!!:\n{result}")


if __name__ == "__main__":
    init()
