#!/usr/bin/env python3

import os
import shutil
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

import fun

def read_excel(filepath):
    book = xlrd.open_workbook(filepath)
    data = []
    for sheet in book.sheets():
        for i in range(sheet.nrows):
            row = sheet.row(i)
            if row[0].value != '' and row[1].value != '':
                d = [fun.clean_str(str(x.value)) for x in row]
                data.append(d)
    return data

def write_sale2mongodb(sale_db, Data):
    data = []
    for d in Data:
        data.append({'question':d[0], 'answer':d[1]})
    sale_db.insert(data)


#读取excel
print('read_excel starting...')
Data = []
dirpath = r'./sale_data/'
filelist = os.listdir(dirpath)
for f in filelist:
    Data += read_excel(os.path.join(dirpath, f))
print('read_excel ending...')

#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

print('sale starting...')
#write sale dialogue to mongodb, doc:'sale'
sale_db = db['sale']
#sale_db.remove()
sale_db.drop()
write_sale2mongodb(sale_db, Data)
#print(sale_db.find().count())
print('sale ending...')

#save to file
f = open(r'./sale.txt', 'w')
for d in sale_db.find():
    f.write(d['question']+'#'+d['answer']+'\n')
f.close()
