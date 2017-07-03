#!/usr/bin/env python3

import os
import shutil
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

import fun

Dict = {'问题':'question',
        '回答':'answer',
        '合成句':'synthesis_sentence',
        '问题句型':'q_sentence_type',
        '回答句型':'a_sentence_type',
        '类型':'type',
        '业务':'business',
        '意图':'intention',
        '上级意图':'super_intention',
        '场景':'scene',
        '领域':'domain',
        '关键词':'key_words',
        '分词':'seg',
        '等价描述':'equal_questions',
        '等价描述（陈述句）':'q_statement',
        '等价描述（疑问句）':'q_question',
        }

#读取excel
print('read_excel starting...')
data_path = r'./data.xlsx'
Data = fun.read_excel(data_path, Dict)
print('read_excel ending...')

#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

print('raw_data starting...')
#write raw dialogue to mongodb, doc:'raw_data'
raw_db = db['raw_data']
#raw_db.remove()
raw_db.drop()
fun.write_raw_data2mongodb(raw_db, Data)
#print(raw_db.find().count())
print('raw_data ending...')

print('dialogue starting...')
#write dialogue to mongodb, doc:'dialogue'
dia_db = db['dialogue']
#dia_db.remove()
dia_db.drop()
fun.write_dialog2mongodb(dia_db, raw_db)
#print(dia_db.find().count())
print('dialogue ending...')

print('q_a starting...')
#write q_a to mongodb, doc:'q_a'
qa_db = db['q_a']
#qa_db.remove()
qa_db.drop()
fun.write_qa2mongodb(qa_db, raw_db)
#更新句子类型到q_a
#sentence_types = fun.read_sentence_type(r'./sentence_type.xls')
#fun.update_sentence_type_2_q_a(qa_db, sentence_types)
print('q_a ending...')


print('intention starting...')
#write intention_questions_answer to mongodb, doc:'intention'
intention_db = db['intention']
#intention_db.remove()
intention_db.drop()
fun.write_iqs2mongodb0(intention_db, qa_db)
print('intention ending...')


