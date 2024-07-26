# -*- coding: utf-8 -*-
import csv
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
from html import unescape
import unicodedata

def scrapeMetaPage(source_url): # capture metadata from the legislation details page - lists legislation metadata
    print("Legislation Metadata Details Page scraping has begun")
    try:
        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        # fieldnames = ['Legislation Status', 'Administered By', 'Latest Version', 'Title ID', 'Registered Date', 'Effective Date Start', 'Type', 'To Be Repealed', 'Due to Sunset Date']
        fieldnames = ['Meta Key', 'Meta Value']
        linkarray = []        
        missng = "missing metadata"
        stat = ""
        admin = ""
        vers = ""
        titleID = ""
        regDate = ""
        for span in soup.find_all('span', attrs={'class':'badge badge-default badge-size-large bg-success'}): # Legislation Status
            stat = span.string
            break
        if not stat == "":
            stat = stat.strip()
            stat = stat.replace('\n', ' ').replace('\r', '')
        else:
            stat = missng
        linkarray.append(['Legislation Status', stat])
        for span in soup.find_all('span', attrs={'class':'item-id small fw-bold'}): # Latest Version
            vers = span.string
            break
        if not vers == "":
            vers.strip('\n')
            vers.strip('\"')
        else:
            vers = missng
        linkarray.append(['Latest Version', vers])
        print(f"got to breakpoint 1 {vers} {stat}")
        for ul in soup.find_all('ul', attrs={'class':'list-group list-unstyled ms-3'}): # Administered By
            licnt = 0
            for li in ul.find_all('li'):
                sadmin = li.string
                if len(sadmin) > 0:
                    if licnt > 0:
                        admin = " - " + sadmin
                        licnt + 1
                    else:
                        admin = sadmin
                        licnt + 1
            if admin == "":
                admin = missng
                break
        admin = admin.replace('\n', ' ').replace('\r', '')
        admin = admin.strip()
        linkarray.append(['Administered By', admin])
        print(f"got to breakpoint 2 {admin}")
        for div in soup.find_all('div', attrs={'class':'col-lg-9 title-id'}): # Title ID
            titleID = div.string
            titleID.strip()
            break
        if titleID == "":
            titleID = missng
        linkarray.append(['Title ID', titleID])
        for div in soup.find_all('div', attrs={'class':'col-lg-9 registered-at'}): # Registered Date
                regDate = div.string
        if regDate == "":
            regDate = missng
        linkarray.append(['Registered Date', regDate])
        print(f"got to breakpoint 3 {titleID} {regDate}")
        label = legID
        label += '_pagemetadata'
        writecsv(linkarray, label, fieldnames)
        return True
    except Exception as e:
        return e

def scrapeMeta(source_url): # capture page metadata for the legislation page
    print("Legislation Metadata scraping has begun")
    try:
        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        fieldnames = ['Meta Key', 'Meta Value']
        meta_tags = soup.find_all('meta')
        metadata = {}
        for tag in meta_tags:
            if 'name' in tag.attrs:
                name = tag.attrs['name']
                content = tag.attrs.get('content', '')
                metadata[name] = content
            elif 'prop' in tag.attrs:  # For OpenGraph metadata
                prop = tag.attrs['property']
                content = tag.attrs.get('content', '')
                metadata[prop] = content
        label = legID
        label += '_metadata'
        writecsv(metadata.items(), label, fieldnames)
        return True
    except Exception as e:
        return e

def scrape(source_url): # capture the table of contents links and associated metadata for the legislation page
    print("Legislation ToC scraping has begun")
    try:

        parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
        resp = requests.get(source_url)
        http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
        html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        soup = BeautifulSoup(resp.content, parser, from_encoding=encoding)
        fieldnames = ['DOM Element Count', 'Legislation Section URL', 'Chapter', 'Part', 'Divison', 'SubHeading']
        linkarray = []
        chapter = ""
        part = ""
        division = ""
        subheading = ""
        cnt = 0
        for link in soup.find_all('a'): # break into chapter, part, division, statement
            if 'Toc' in link['href']:
                cnt = cnt+1
                heading = link.string
                # clean up the text
                heading = cleanCruft(str(heading)) # clean up the string adding space after digits
                if 'Chapter' in heading:
                    if heading.startswith("Chapter"):
                        chapter = heading
                if 'Part' in heading:
                    if heading.startswith("Part"):
                        part = heading
                if 'Division' in heading:
                    if heading.startswith("Division"):
                        division = heading
                if heading != "" and heading != chapter and heading != part and heading != division and heading != subheading:
                    subheading = heading
                else:
                    subheading = ""
                linkarray.append([str(cnt), link['href'], chapter, part, division, subheading])
        label = legID
        label += '_data'
        writecsv(linkarray, label, fieldnames)
        return True
    except Exception as e:
        return e

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

def writecsv(content, title, fieldnames): # The scraped info will be written to a CSV here.))
    try:
        with open(f"{globals().get('outputFolder')}{title}.csv", "w", encoding='UTF8', newline='') as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(fieldnames)
            csv_writer.writerows(content)
    except:
        return False

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
    result = scrape(leg_seed_url)
    if result == True:
        result = scrapeMeta(leg_seed_url)
    if result == True:
        result = scrapeMetaPage(f"https://www.legislation.gov.au/{legID}/latest/details") # e.g.https://www.legislation.gov.au/F2021L00319/latest/details
    if result == True:
        print("Legislation ToC and Metadata and Metadata Details scraping is now complete!")
    else:
        print(f"\nOops, That doesn't seem right!!!:\n{result}")
