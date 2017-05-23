#!/usr/bin/env python3

import os
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

import fun

#读取excel
D = {'question':[],
        'answer':[],
        'business':[],
        'intention':[],
        'super_intention':[],
        'equal_questions':[]}

fun.read_excel(D)

#clean_str
#标点修正，等价描述修正
i = 0
while i < len(D['question']):
    for r in D.values():
        r[i] = fun.clean_str(r[i])
    if D['answer'][i] != 'nan':
        D['answer'][i] = fun.proc_punctuation(D['answer'][i]) 
    #修正等价描述格式
    D['equal_questions'][i] = D['equal_questions'][i].replace(' ', '')
    D['equal_questions'][i] = D['equal_questions'][i].replace('//', '/')
    if D['equal_questions'][i][-1] == '/':
        D['equal_questions'][i] = D['equal_questions'][i][:-1]
    if D['equal_questions'][i][0] == '/':
        D['equal_questions'][i] = D['equal_questions'][i][:-1]
    i += 1

#write to data.txt
fun.data_xlsx2txt(D)

#生成Qs_A[]
Qs_A = fun.generate_Qs_A(D)

#按对话切分列表
#Qs_A[] => Q_A[]
#[{1},{2},{'nan'},{3}] => [[{1},{2}], [{3}]]
Q_A = fun.split_dialogue(Qs_A) 
#print(len(Q_A))

#随机生成对话(*20)
dialogues = fun.generate_dialog_list(Q_A)
#print(dialogues[0])
#print(len(dialogues))

#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

#write dialogue to mongodb, doc:'dialogue'
#random 20*[]
dia_db = db['dialogue']
dia_db.remove()
fun.write_dialog2mongodb(dia_db, dialogues)

#print(dia_db.find().count())

#write q_a to mongodb, doc:'q_a'
qa_db = db['q_a']
qa_db.remove()
for d in dia_db.find():
    fun.write_qa2mongodb(qa_db, d)

#for qa in qa_db.find():
#    print(qa['_id'], qa['question'])



#####################################
#print Q/A to dialogue
# Q1/intention
# Q2/intention
# Q3/intention
#
# Q1/intention
# Q2/intention
f = open('./dialogue', 'w')
for d in dia_db.find():
    question_list = d['question_list'].split('/')
    intention_list = d['intention_list'].split('/')
    i = 0
    while i < len(question_list):
        f.write(question_list[i] + '/' + intention_list[i] + '\n')
        i += 1
    f.write('\n')

#----------------------------------
#意图_回答{上级意图问题, 上级意图问题}
test_Q = []
test_A = []
test_Q_A = []
test_intention = []
for row in Qs_A:
    if row['answer'] == 'nan':
        continue
    for q in row['questions']:
        super_intention = row['super_intention']
        if row['super_intention'] == 'nan':
            super_intention = ''
        test_Q.append(super_intention+q)#上级意图问题
        test_A.append(row['intention']+':'+row['answer'])#意图_回答
        test_intention.append(row['intention'])
        test_Q_A.append([super_intention+q,\
                row['intention']])

if not os.path.exists(r'./data'):
    os.mkdir("data")
test_intention_list = list(set(test_intention))
for name in test_intention_list:
    f = open('./data/'+name, 'w')
    for i in test_Q_A:
        if name == i[1]:
            f.write(i[0]+'\n')
    f.close()

f = open('intention_answer', 'w')
test_A_list = list(set(test_A))
for i in test_A_list:
    f.write(i + '\n')
f.close()

#test_Q_list = list(set(test_Q))
#for i in test_Q_list:
#    print(i)

######################################

