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

fun.read_excel(D)

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

#按对话切分列表
dd = fun.split_dialog(D)
#print(len(dd))
#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

#write raw dialogue to mongodb, doc:'raw_data'
raw_db = db['raw_data']
raw_db.remove()
fun.write_raw_data2mongodb(raw_db, dd)
#print(raw_db.find().count())

#write dialogue to mongodb, doc:'dialogue'
dia_db = db['dialogue']
dia_db.remove()
fun.write_dialog2mongodb(dia_db, raw_db)
#print(dia_db.find().count())

#write q_a to mongodb, doc:'q_a'
qa_db = db['q_a']
qa_db.remove()
fun.write_qa2mongodb(qa_db, raw_db)

#for qa in qa_db.find():
#    print(qa['_id'], qa['question'])


###############################################
#
#
#           输出制定格式数据
#
#
###############################################
#print {dialogue} to dialogue
#
# q1/intention1
# q2/intention2
# q3/intention3
#
# q1/intention1
# q2/intention2
#
f = open('./dialogue', 'w')
for d in dia_db.find():
    for i in range(len(d['question_list'])):
        f.write(d['question_list'][i] + '/' + d['intention_list'][i] + '\n')
    f.write('\n')
f.close()

######################################
#数据提取

test_intention = []
test_business = []
test_sentence_type = []
test_intention_answer = []
test_data = [] #[问题，上级意图问题，意图，业务，问题句型, 回答]
for d in raw_db.find():
    for i in range(len(d['intention_list'])):
        test_intention.append(d['intention_list'][i])
        test_business.append(d['business_list'][i])
        test_sentence_type.append(d['q_sentence_type_list'][i])
        test_intention_answer.append(d['intention_list'][i] + ':' +
            d['answer_list'][i])
        for q in d['question_list'][i]:
            if d['super_intention_list'][i] == 'nan':
                test_data.append([q, q, d['intention_list'][i],
                    d['business_list'][i], d['q_sentence_type_list'][i],
                    d['answer_list'][i]])
            else:
                test_data.append([q, d['super_intention_list'][i] + q,
                    d['intention_list'][i], d['business_list'][i],
                    d['q_sentence_type_list'][i], d['answer_list'][i]])

#####################################
#print {raw_data} to dialogue
#
# intention1:a1
# intention2:a2
# intention3:a3
#
#[0问题，1上级意图问题，2意图，3业务，4问题句型, 5回答]

f = open('intention_answer', 'w')
for i in list(set(test_intention_answer)):
    f.write(i + '\n')
f.close()


######################################
#意图{上级意图问题, 上级意图问题}
#/data/
#[0问题，1上级意图问题，2意图，3业务，4问题句型, 5回答]

path = r'./intention/'
if os.path.exists(path):
    shutil.rmtree(path)
os.mkdir(path)
path_0 = r'./intention_0/'
if os.path.exists(path_0):
    shutil.rmtree(path_0)
os.mkdir(path_0)
for intention_name in list(set(test_intention)):
    f = open(path+intention_name, 'w')
    f0 = open(path_0+intention_name, 'w')
    tmp = []
    for i in test_data:
        if intention_name == i[2]:
            f.write(i[1]+'\n')
            tmp.append(i[0])
    for i in list(set(tmp)):
        f0.write(i+'\n')
    f.close()
    f0.close()

######################################
#[0问题，1上级意图问题，2意图，3业务，4问题句型, 5回答]
path = r'./business/'
if os.path.exists(path):
    shutil.rmtree(path)
os.mkdir(path)
for business_name in list(set(test_business)):
    f = open(path+business_name, 'w')
    for i in test_data:
        if business_name == i[3]:
            f.write(i[1]+'\n')
    f.close()

######################################
#[0问题，1上级意图问题，2意图，3业务，4问题句型, 5回答]
path = r'./sentence_type/'
if os.path.exists(path):
    shutil.rmtree(path)
os.mkdir(path)
for sentence_type_name in list(set(test_sentence_type)):
    f = open(path+sentence_type_name, 'w')
    for i in test_data:
        if sentence_type_name == i[4]:
            f.write(i[0]+'\n')
    f.close()

######################################

