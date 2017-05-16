#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

from fun import clean_str

#读取excel
question = []
answer = []
intention = []
super_intention = []
equal_question = []
business = []

file_path = r'./data.xlsx'
book = xlrd.open_workbook(file_path)
for sheet in book.sheets():
    df = pd.read_excel('./data.xlsx', sheet.name)
    if sheet.name != 'Sheet1':
        for i in df['问题']:
            question.append(str(i))
        for i in df['回答']:
            answer.append(str(i))
        for i in df['意图']:
            intention.append(str(i))
        for i in df['上级意图']:
            super_intention.append(str(i))
        for i in df['等价描述']:
            equal_question.append(str(i))
        for i in df['业务']:
            business.append(str(i))

#写入mongodb
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]
bank = db['bank']
bank.remove()

index = 0
length = len(question)
while index < length:
    if question[index] != 'nan':
        a1 = clean_str(question[index])
        a2 = '' if answer[index] == 'nan' else clean_str(answer[index])
        a3 = '' if intention[index] == 'nan' else clean_str(intention[index])
        a4 = '' if super_intention[index] == 'nan'\
                        else clean_str(super_intention[index])
        a5 = '' if business[index] == 'nan' else clean_str(business[index])
        bank.insert({"question":a1, "answer":a2, "intention":a3,\
                "super_intention":a4, "business":a5})
        q = equal_question[index].split('/')
        for i in q:
            if i != '':
                bank.insert({"question":clean_str(i), "answer":a2,\
                        "intention":a3, "super_intention":a4, "business":a5})
    index += 1

#生成指定格式
Q = []
A = []
Q_A = []
for row in bank.find():
    Q.append(row['super_intention']+row['question'])
    A.append(row['intention']+'_'+row['answer'])
    Q_A.append([row['super_intention']+row['question'],\
                    row['intention']+'_'+row['answer']])
    

if not os.path.exists(r'./data'):
    os.mkdir("data")
A_list = list(set(A))
for name in A_list:
    f = open('./data/'+name, 'w')
    for i in Q_A:
        if name == i[1]:
            f.write(i[0]+'\n')
    f.close()


