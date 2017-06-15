#!/usr/bin/env python3

from pymongo import MongoClient
from xml.dom.minidom import Document
import operator


intention_db = MongoClient('127.0.0.1', 27017).data.intention

data = []
intention = [x['business']+':'+x['super_intention']+':'+x['intention']
        for x in intention_db.find()]
for i in list(set(intention)):
    data.append(i.split(':'))
data.sort(key=operator.itemgetter(0))


def next_intention(data, current_intention):
    d = []
    for x in data:
        if x[1] == current_intention:
            d.append(x[2])
    return d

def add_node(doc, current_node, parent_node):
    node = doc.createElement('intention')
    node.setAttribute('name', current_node)
    parent_node.appendChild(node)
    return node

def add_tree(data, doc, current_node, parent_node):
    node = add_node(doc, current_node, parent_node)
    next_nodes = next_intention(data, current_node)
    for n in next_nodes:
        add_tree(data, doc, n, node)


doc = Document()

add_tree(data, doc, 'nan', doc)

with open('a.xml', 'w') as f:
    f.write(doc.toprettyxml(indent='\t'))





