#!/usr/bin/env python3

import pandas as pd
import numpy as np
import xlrd

from pymongo import MongoClient

question = []
answer = []
intention = []
super_intention = []
equal_question = []

file_path = r'./data.xlsx'
book = xlrd.open_workbook(file_path)
for sheet in book.sheets():
    df = pd.read_excel('./data.xlsx', sheet.name)
    if sheet.name != 'Sheet1':
        for i in df['问题']:
            question.append(str(i).strip())
        for i in df['回答']:
            answer.append(str(i).strip())
        for i in df['意图']:
            intention.append(str(i).strip())
        for i in df['上级意图']:
            super_intention.append(str(i).strip())
        for i in df['等价描述']:
            equal_question.append(str(i).strip())

client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]
bank = db['bank']
bank.remove()

index = 0
length = len(question)
while index < length:
    if question[index] != 'nan':
        a1 = question[index]
        a2 = '' if answer[index] == 'nan' else answer[index]
        a3 = '' if intention[index] == 'nan' else intention[index]
        a4 = '' if super_intention[index] == 'nan' else super_intention[index]
        bank.insert({"question":a1, "answer":a2, "intention":a3,\
                "super_intention":a4})
        q = equal_question[index].split('/')
        for i in q:
            if i != '':
                bank.insert({"question":i, "answer":a2, "intention":a3,\
                        "super_intention":a4})
    index += 1

#for row in bank.find():
#    print(row)

Q = []
A = []
Q_A = []
index = 0
while index < length:
    if question[index] != 'nan':
        a1 = question[index]
        a2 = '' if answer[index] == 'nan' else answer[index]
        a3 = '' if intention[index] == 'nan' else intention[index]
        a4 = '' if super_intention[index] == 'nan' else super_intention[index]
        Q.append(a4+a1)
        A.append(a3+'_'+a2)
        Q_A.append([a4+a1, a3+'_'+a2])
        q = equal_question[index].split('/')
        for i in q:
            if i != '':
                Q.append(a4+i)
                A.append(a3+'_'+a2)
                Q_A.append([a4+i, a3+'_'+a2])

    index += 1

A_list = list(set(A))
for name in A_list:
    f = open('./data/'+name, 'w')
    for i in Q_A:
        if name == i[1]:
            f.write(i[0]+'\n')
    f.close()



