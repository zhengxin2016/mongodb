#!/usr/bin/env python3

import os
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient


#字符清理
def clean_str(string):
    string = string.strip()
    string = string.replace(',', '，')
    string = string.replace('.', '。')
    string = string.replace('?', '？')
    string = string.replace('!', '！')
    return string

#回答句尾添加标点，修正部分句型的标点
def proc_answer(d):
    p = ['，', '。', '！', '？']
    w = ['呢', '吗', '么']
    if d['回答'][-1] not in p:
        if d['回答'][-1] in w:
            d['回答'] = d['回答'] + '？'
        else:
            d['回答'] = d['回答'] + '。'
    if d['回答'][-1] in p:
        if d['回答'][-2] in w:
            d['回答'] = d['回答'][:-1] + '？'
#等价描述切分
def proc_equal_questions(d):
    if d['等价描述'] == '':
        d['等价描述'] = [d['问题']]
        return
    d['等价描述'] = d['等价描述'].replace(' ', '')
    d['等价描述'] = d['等价描述'].replace('//', '/')
    if d['等价描述'][-1] == '/':
        d['等价描述'] = d['等价描述'][:-1]
    if d['等价描述'][0] == '/':
        d['等价描述'] = d['等价描述'][1:]
    d['等价描述'] = d['等价描述'].split('/')
    d['等价描述'].append(d['问题'])

#读excel数据
def read_excel(filepath, Dict):
    book = xlrd.open_workbook(filepath)
    data = []
    head_name = [x.value for x in book.sheets()[0].row(0)]
    def init_dict():
        d = {}
        for i in Dict.values():
            d[i] = []
        return d
    for sheet in book.sheets():
        dia = init_dict()
        for i in range(1, sheet.nrows):
            if sheet.row(i)[0].value == '':
                if dia[Dict[head_name[0]]]:
                    data.append(dia)
                    dia = init_dict()
            else:
                d = dict(zip(head_name, 
                    [clean_str(x.value) for x in sheet.row(i)]))
                proc_answer(d)
                proc_equal_questions(d)
                for i in d.keys():
                   dia[Dict[i]].append(d[i]) 
        if dia[Dict[head_name[0]]]:
            data.append(dia)
    return data


#以对话为单位存到数据库中
#输入：raw_db, Q_A
#输出：无
def write_raw_data2mongodb(raw_db, dialogues):
    data = []
    for d in dialogues:
        data.append({"question_list":d['equal_questions'],
                "answer_list":d['answer'],
                "q_sentence_type_list":d['q_sentence_type'],
                "a_sentence_type_list":d['a_sentence_type'],
                "type_list":d['type'],
                "business_list":d['business'],
                "intention_list":d['intention'],
                "super_intention_list":d['super_intention'],
                "scene_list":d['scene'],
                "domain_list":d['domain'],
                "key_words_list":d['key_words']
                })
    raw_db.insert(data)

#随机生成对话列表，以对话为单位存到数据库中
#输入：dialog_db, raw_db
#输出：无
def write_dialog2mongodb(dialog_db, raw_db):
    data = []
    for d in raw_db.find():
        N = 0
        for q in d['question_list']:
            N += len(q)
        while N > 0:
            q_list = []
            for q in d['question_list']:
                i = random.randint(0, len(q) - 1)
                q_list.append(q[i])
            data.append({"question_list":q_list,
                    "answer_list":d['answer_list'],
                    "q_sentence_type_list":d['q_sentence_type_list'],
                    "a_sentence_type_list":d['a_sentence_type_list'],
                    "type_list":d['type_list'],
                    "business_list":d['business_list'],
                    "intention_list":d['intention_list'],
                    "scene_list":d['scene_list'],
                    "domain_list":d['domain_list'],
                    "key_words_list":d['key_words_list'],
                    "super_intention_list":d['super_intention_list']})
            N -= 1
    dialog_db.insert(data)

#以一问一答为单位存到数据库中
#输入：
#输出：无
def write_qa2mongodb(qa_db, raw_db):
    data = []
    for d in raw_db.find():
        for i in range(len(d['question_list'])):
            for j in range(len(d['question_list'][i])):
                data.append({
                    "question":d['question_list'][i][j],
                    "answer":d['answer_list'][i],
                    "q_sentence_type":d['q_sentence_type_list'][i],
                    "a_sentence_type":d['a_sentence_type_list'][i],
                    "type":d['type_list'][i],
                    "business":d['business_list'][i],
                    "intention":d['intention_list'][i],
                    "scene":d['scene_list'][i],
                    "domain":d['domain_list'][i],
                    "key_words":d['key_words_list'][i],
                    "super_intention":d['super_intention_list'][i]})
    qa_db.insert(data)


#以{意图，上级意图，问题列表，回答}为单位存到数据库中
#输入：
#输出：以intention为标识，super_intention:intention不全
def write_iqs2mongodb(intention_db, qa_db):
    intention = [{'intention':x, 'questions':None, 'answer':None, 'super_intention':None,
        'business':None} for x in qa_db.distinct('intention')]
    for i in intention:
        i['questions'] = list(set(x['question']
            for x in qa_db.find({'intention':i['intention']})))
        data = qa_db.find_one({'intention':i['intention'], 'super_intention':{"$ne":''}})
        if data is None:
            i['super_intention'] = ''
            data = qa_db.find_one({'intention':i['intention']})
        else:
            i['super_intention'] = data['super_intention']
        i['answer'] = data['answer']
        i['business'] = data['business']
    intention_db.insert(intention)

#以super_intention:intention为标识，intention有重复
def write_iqs2mongodb0(intention_db, qa_db):
    data = [{'intention':x['intention'], 'questions':None, 'answer':None,
        'super_intention':x['super_intention'], 'business':None}
            for x in qa_db.find()]
    intention = []
    for x in data:
        if x not in intention:
            intention.append(x)
    for i in intention:
        i['questions'] = list(set(x['question']
            for x in qa_db.find({'intention':i['intention']})))
        data = qa_db.find_one({'intention':i['intention']})
        i['answer'] = data['answer']
        i['business'] = data['business']
    intention_db.insert(intention)


#读取句子类型标注结果
def read_sentence_type(path):
    L = []
    book = xlrd.open_workbook(path)
    sh_names = book.sheet_names()
    for sh_name in sh_names[:1]:
        sh = book.sheet_by_name(sh_name)
        for i in range(1, sh.nrows):
            t = sh.cell_value(i, 2)
            if t == '':
                t = '正反问句'
            L.append([sh.cell_value(i, 0), sh.cell_value(i, 1), t])
    return L

#更新q_a中问题类型
def update_sentence_type_2_q_a(qa_db, L):
    for x in L:
        qa_db.update_many({'super_intention':x[0], 'question':x[1]},
                {'$set':{'q_sentence_type':x[2]}})






