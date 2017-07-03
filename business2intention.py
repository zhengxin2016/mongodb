#!/usr/bin/env python3

from pymongo import MongoClient

class Tree:
    def __init__(self, data):
        self._data = data
        self._children = []

    def getdata(self):
        return self._data

    def getchildren(self):
        return self._children

    def add(self, node):
        self._children.append(node)
    def go(self, data):
        for child in self._children:
            if child.getdata() == data:
                return child
        return None


def get_intention(db, super_intention, tree):
    i_a = [x['intention']+'-->'+x['answer'] for x in db.intention.find({'super_intention':super_intention})]
    if i_a == []:
        return None
    else:
        for i in set(i_a):
            tree.add(Tree(i))
            child = tree.go(i)
            get_intention(db, i.split('-->')[0], child)

def print_intention(intention, path):
    if intention.getchildren() == []:
        print('\t'+path+'\n')
    else:
        for i in intention.getchildren():
            print_intention(i, path+'\n\t'+i.getdata())

def print_intention_tree(db):
    business = [x for x in db.intention.distinct('business')]
    for b in business:
        print(b)
        i_a = [x['intention']+'-->'+x['answer'] for x in db.intention.find({'business':b})]
        for i in set(i_a):
            A = Tree(i)
            get_intention(db, i.split('-->')[0], A)
            print_intention(A, A.getdata())

def print_business2intention(db):
    business = [x for x in db.intention.distinct('business')]
    print(len(business))
    print(business)
    for b in business:
        intention = [x['intention'] for x in db.intention.find({'business':b})]
        print(b)
        for i in set(intention):
            print('\t'+i)

if __name__ == '__main__': 
    db = MongoClient('127.0.0.1', 27017).data
    #print_business2intention(db)
    print_intention_tree(db)



