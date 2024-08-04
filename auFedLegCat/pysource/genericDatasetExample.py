# -*- coding: utf-8 -*-import csv
from rdflib import Graph, URIRef, XSD, DCAT, SKOS, DCTERMS, RDF, RDFS, Literal, SDO, OWL, Namespace
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
from html import unescape
import unicodedata
import datetime

def scrapeMetaPage(g, legID, source_url): # capture metadata from the legislation details page - lists legislation metadata
    print("Legislation Metadata Details Page scraping has begun")
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
#        for div in soup.find_all('div', attrs={'class':'col-lg-9 registered-at'}): # Registered Date
#                regDate = div.string
#        if not regDate == "":
#            g.add((nspace, DCTERMS.regDate, Literal(regDate)))
        return True
    except Exception as e:
          return e

def scrape(g, source_url, legID, outputFolder): # capture the table of contents links and associated metadata for the legislation page
    print("Legislation ToC scraping has begun")
    print(legID)
    print(source_url)
    try:

        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        # build first part of graph
        baseURL = f"http://example.org/au/leg/dataset/{legID}/"
        nspace = URIRef(baseURL)
        g.bind("LegID", Namespace(nspace))
        skosref = URIRef("http://example.org/au/leg/concepts/")
        builder = "https://orcid.org/0009-0007-8434-7325"
        g.bind(":", nspace)
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
                return
        # add imports
        g.add((nspace, OWL.imports, skosref))
        # used to set skos:broader/skos:narrower
        change_globals("V", None)
        change_globals("C", None)
        change_globals("P", None)
        change_globals("D", None)
        change_globals("S", None)
        change_globals("I", None)
        # itterate through mined page elements
        cnt = 0
        li = None
        div = None
        link = None
        for li in soup.find_all('li', {'class': 'toc-link'}):
            div = li.find("div")
            if not div == None:
                link = div.find('a', recursive=False)
                if not link == None:
                    cnt = cnt+1
                    # add some triples
                    leader = URIRef(nspace + str(cnt))
                    g.add((leader, URIRef(RDF.type), URIRef(DCAT.Resource)))
                    g.add((leader, URIRef(DCAT.accessURL), Literal(link['href'], datatype=XSD.anyURI)))
                    g.add((leader, RDF.type, URIRef(SKOS.Concept)))
                    heading = link.string
                    # clean up the text
                    heading = cleanCruft(str(heading)) # clean up the string adding space after digits and remove cruft
                    # set the global to enable skos
                    if 'Volume' in heading:
                        if heading.startswith('Volume'):
                            change_globals("V", leader)
                            change_globals("C", None)
                            change_globals("P", None)
                            change_globals("D", None)
                            change_globals("S", None)
                            change_globals("I", None)
                            buildNode(g, "Volume", cnt, skosref, leader, heading)
                    elif 'Chapter' in heading:
                        if heading.startswith("Chapter"):
                            change_globals("C", leader)
                            change_globals("P", None)
                            change_globals("D", None)
                            change_globals("S", None)
                            change_globals("I", None)
                            buildNode(g, "Chapter", cnt, skosref, leader, heading)
                    elif 'Endnotes' in heading:
                        if heading.startswith("Endnotes"):
                            change_globals("P", leader)
                            change_globals("C", None)
                            change_globals("S", None)
                            change_globals("D", None)
                            change_globals("I", None)
                            buildNode(g, "Part", cnt, skosref, leader, heading)
                    elif 'Part' in heading:
                        if heading.startswith("Part"):
                            change_globals("P", leader)
                            change_globals("D", None)
                            change_globals("S", None)
                            change_globals("I", None)
                            buildNode(g, "Part", cnt, skosref, leader, heading)
                    elif 'Division' in heading:
                        if heading.startswith("Division"):
                            change_globals("D", leader)
                            change_globals("S", None)
                            change_globals("I", None)
                            buildNode(g, "Division", cnt, skosref, leader, heading)
                    elif 'Subdivision' in heading:
                        if heading.startswith("Subdivision"):
                            change_globals("S", leader)
                            change_globals("I", None)
                            buildNode(g, "Subdivision", cnt, skosref, leader, heading)
                    elif not heading == None and not leader == None:
                        change_globals("I", leader)
                        buildNode(g, "Item", cnt, skosref, leader, heading)
#                        tst = str(leader)
#                        for leader, RDFS.label, tst in g:
#                            if (leader, RDF.label, tst) in g:
                    
                    continue
        g.serialize(destination=outputFolder + legID + '.ttl', format='ttl')
        return True
    except Exception as e:
        return e

def buildNode(g, headingVal, cnt, skosref, leader, heading): # this is where the not is constructed, including its place in the SKOS taxonomy
    try:
        prfx = headingVal[0].upper() + str(cnt) + " - "
        lab = heading
        nodeURI = URIRef(skosref + headingVal)
        g.add((leader, URIRef(RDF.type), nodeURI))
        g.add((leader, RDF.type, URIRef(SKOS.Concept)))
        g.add((leader, SKOS.definition, Literal(lab, lang="en-AU")))
        g.add((leader, SKOS.prefLabel, Literal(prfx + headingVal, lang="en-AU")))
        g.add((leader, RDFS.comment, Literal(prfx + lab, lang="en-AU")))
        g.add((leader, RDFS.label, Literal(prfx + headingVal, lang="en-AU")))
        # add skos broader than or narrower than references according to global variable value settings if a parent exists
        if headingVal == "Chapter": # we have a Chapter, so check for parent (Volume)
            if not volumeBranch == None: # there is an existing Volume (parent) node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, volumeBranch))
                g.add((volumeBranch, SKOS.broader, leader))
        elif headingVal == "Part": # we have a Part, so check for parent (Chapter)
            if not chapterBranch == None: # there is an existing (parent) Chapter node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, chapterBranch))
                g.add((chapterBranch, SKOS.broader, leader))
            elif not volumeBranch == None: # there is an existing Volume (parent) node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, volumeBranch))
                g.add((volumeBranch, SKOS.broader, leader))
        elif headingVal == "Division": # we have a Division, so check for parent (Part)
            if not partBranch == None: # there is an existing (parent) Chapter node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, partBranch))
                g.add((partBranch, SKOS.broader, leader))
            elif not chapterBranch == None:
                g.add((leader, SKOS.narrower, chapterBranch))
                g.add((chapterBranch, SKOS.broader, leader))
        elif headingVal == "Subdivision": # we have a Subdivision, so check for parent (Part)
            if not divisionBranch == None: # there is an existing (parent) Division node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, divisionBranch))
                g.add((divisionBranch, SKOS.broader, leader))
            elif not partBranch == None: # there is an existing (parent) Part node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, partBranch))
                g.add((partBranch, SKOS.broader, leader))
            elif not chapterBranch == None: # there is an existing (parent) Chapter node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, chapterBranch))
                g.add((chapterBranch, SKOS.broader, leader))
            elif not volumeBranch == None: # there is an existing (parent) Volume node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, volumeBranch))
                g.add((volumeBranch, SKOS.broader, leader))
        elif headingVal == "Item" and not checkGlobalsForNone() == False: # we have a Item, so check for parent (Part)
            if not subdivisionBranch == None: # there is an existing (parent) subdivision node so specify a parent node exists and this node is a child
                g.add((leader, SKOS.narrower, subdivisionBranch))
                g.add((subdivisionBranch, SKOS.broader, leader))
            elif not divisionBranch == None: # there is an existing (parent) Division node so specify a parent node exists and this node is a child
                # print('divisionBranch')
                g.add((leader, SKOS.narrower, divisionBranch))
                g.add((divisionBranch, SKOS.broader, leader))
            elif not partBranch == None: # there is an existing (parent) Part node so specify a parent node exists and this node is a child
                # print(partBranch)
                g.add((leader, SKOS.narrower, partBranch))
                g.add((partBranch, SKOS.broader, leader))
            elif not chapterBranch == None: # there is an existing (parent) Chapter node so specify a parent node exists and this node is a child
                # print('chapterBranch')
                g.add((leader, SKOS.narrower, chapterBranch))
                g.add((chapterBranch, SKOS.broader, leader))
            elif not volumeBranch == None: # there is an existing (parent) Volume node so specify a parent node exists and this node is a child
                # print('volumeBranch')
                g.add((leader, SKOS.narrower, volumeBranch))
                g.add((volumeBranch, SKOS.broader, leader))
        return True
    except Exception as e:
        return e


def change_globals(name, val): # Take the name of the node type and the node instance then set the instance value to that passed in (either a URIRef or None)
    try:
        if name == None and isinstance(name, str):
            print("\"def change_globals(name, val)\" requires an \"name\" argument that is a string and a \"val\" argument that is rdfdib URIRef, or \"None\"")
            return False
        else:
            if name == "V":
                global volumeBranch
                volumeBranch = val
            elif (name == "C"):
                global chapterBranch
                chapterBranch = val
            elif (name == "P"):
                global partBranch
                partBranch = val
            elif (name == "D"):
                global divisionBranch
                divisionBranch = val
            elif (name == "S"):
                global subdivisionBranch
                subdivisionBranch = val
            elif (name == "I"):
                global itemBranch
                itemBranch = val
    except Exception as e:
        return e

def checkGlobalsForNone():
    returnVal = True
    if volumeBranch == None:
        returnVal = False
    if chapterBranch == None and returnVal == False:
        returnVal = False
    if partBranch == None and returnVal == False:
        returnVal = False
    if divisionBranch == None and returnVal == False:
        returnVal = False
    if subdivisionBranch == None and returnVal == False:
        returnVal = False
    return returnVal
            
    
def cleanCruft(test_str): # clean string of all non RDF-8 characters
    result = ''
    test_str = unescape(test_str)
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
        result += test_str[i]
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
        tocMessage = "Table of Contents"
        if result == True:
            print(f'Success! Mined {pageMetaMessage} and {tocMessage}')
        else:
            print(f"\nOops, That doesn't seem right!!!:\n{result}")


if __name__ == "__main__":
    init()
