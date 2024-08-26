# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 23:40:48 2024

@author: marcu
"""

import glob
from rdflib import Graph

def init():
    ttlfiles = []
    for file in glob.glob("./output/*.ttl"):
        ttlfiles.append(file)
    g = Graph()
    cnt = 0
    for file in ttlfiles:
        g.parse(file)
        cnt += len(g)
    print(f"Triples in generated dcat:Dataset and dcat:Catalog instances: {cnt}")
        
if __name__ == "__main__":
    init()
    