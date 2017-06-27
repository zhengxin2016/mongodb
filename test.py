#!/usr/bin/env python3

import os
import shutil
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

import fun

#读取excel
D = {'question':[],
        'answer':[],
        'q_sentence_type':[],
        'a_sentence_type':[],
        'type':[],
        'business':[],
        'intention':[],
        'super_intention':[],
        'scene':[],
        'domain':[],
        'key_words':[],
        'equal_questions':[]}

print('read_excel starting...')
data_path = r'./data.xlsx'
fun.read_excel(D, data_path)

#clean_str
#标点修正，等价描述修正
for i in range(len(D['question'])):
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

print('read_excel ending...')

print('split dialog starting...')
#按对话切分列表
dd = fun.split_dialog(D)
#print(len(dd))
print('split dialog starting...')

#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

print('raw_data starting...')
#write raw dialogue to mongodb, doc:'raw_data'
raw_db = db['raw_data']
raw_db.remove()
fun.write_raw_data2mongodb(raw_db, dd)
#print(raw_db.find().count())
print('raw_data ending...')

print('dialogue starting...')
#write dialogue to mongodb, doc:'dialogue'
dia_db = db['dialogue']
dia_db.remove()
fun.write_dialog2mongodb(dia_db, raw_db)
#print(dia_db.find().count())
print('dialogue ending...')

print('q_a starting...')
#write q_a to mongodb, doc:'q_a'
qa_db = db['q_a']
qa_db.remove()
fun.write_qa2mongodb(qa_db, raw_db)
#更新句子类型到q_a
#sentence_types = fun.read_sentence_type(r'./sentence_type.xls')
#fun.update_sentence_type_2_q_a(qa_db, sentence_types)
print('q_a ending...')


print('intention starting...')
#write intention_questions_answer to mongodb, doc:'intention'
intention_db = db['intention']
intention_db.remove()
fun.write_iqs2mongodb(intention_db, qa_db)
print('intention ending...')


