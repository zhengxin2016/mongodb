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
    #string = string.replace(' ', '')
    string = string.replace(',', '，')
    string = string.replace('.', '。')
    string = string.replace('?', '？')
    string = string.replace('!', '！')
    return string

#句尾添加标点，修正部分句型的标点
def proc_punctuation(string):
    p = ['，', '。', '！', '？']
    w = ['呢', '吗', '么']
    if string[-1] not in p:
        if string[-1] in w:
            string = string + '？'
        else:
            string = string + '。'
    if string[-1] in p:
        if string[-2] in w:
            string = string[:-1] + '？'
    return string

#读取excel，每项存到列表中
def read_excel(D):
    file_path = r'./data.xlsx'
    book = xlrd.open_workbook(file_path)
    sh_names = book.sheet_names()

    #Sheets
    for sh_name in sh_names[:21]:
        #print(sh_name)
        df = pd.read_excel('./data.xlsx', sh_name)
        for i in df['问题']:
            D['question'].append(str(i))
        for i in df['回答']:
            D['answer'].append(str(i))
        for i in df['问题句型']:
            D['q_sentence_type'].append(str(i))
        for i in df['回答句型']:
            D['a_sentence_type'].append(str(i))
        for i in df['类型']:
            D['type'].append(str(i))
        for i in df['业务']:
            D['business'].append(str(i))
        for i in df['意图']:
            D['intention'].append(str(i))
        for i in df['上级意图']:
            D['super_intention'].append(str(i))
        for i in df['场景']:
            D['scene'].append(str(i))
        for i in df['领域']:
            D['domain'].append(str(i))
        for i in df['关键词']:
            D['key_words'].append(str(i))
        for i in df['等价描述']:
            D['equal_questions'].append(str(i))

        if D['answer'][-1] != 'nan':
            D['question'].append('nan')
            D['answer'].append('nan')
            D['q_sentence_type'].append('nan')
            D['a_sentence_type'].append('nan')
            D['type'].append('nan')
            D['business'].append('nan')
            D['intention'].append('nan')
            D['super_intention'].append('nan')
            D['scene'].append('nan')
            D['domain'].append('nan')
            D['key_words'].append('nan')
            D['equal_questions'].append('nan')


#按对话切分列表
#输入：Dict
#输出：raw_data格式
def split_dialog(D):
    DD = []
    start = 0
    end = 0
    for q in D['question']:
        if q == 'nan':
            e_qs = []
            i = start
            while i < end:
                qs = D['equal_questions'][i].split('/')
                qs.append(D['question'][i])
                e_qs.append(qs)
                i += 1
            DD.append({'question':D['question'][start:end],
                'answer':D['answer'][start:end],
                'q_sentence_type':D['q_sentence_type'][start:end],
                'a_sentence_type':D['a_sentence_type'][start:end],
                'type':D['type'][start:end],
                'business':D['business'][start:end],
                'intention':D['intention'][start:end],
                'super_intention':D['super_intention'][start:end],
                'scene':D['scene'][start:end],
                'domain':D['domain'][start:end],
                'key_words':D['key_words'][start:end],
                'equal_questions':e_qs})
            start = end + 1
            end += 1
            continue
        end += 1
    return DD


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
#输出：以intention为唯一标识
def write_iqs2mongodb(intention_db, qa_db):
    intention = [{'intention':x, 'questions':None, 'answer':None, 'super_intention':None,
        'business':None} for x in qa_db.distinct('intention')]
    for i in intention:
        i['questions'] = list(set(x['question']
            for x in qa_db.find({'intention':i['intention']})))
        data = qa_db.find_one({'intention':i['intention'], 'super_intention':{"$ne":'nan'}})
        if data is None:
            i['super_intention'] = 'nan'
            data = qa_db.find_one({'intention':i['intention']})
        else:
            i['super_intention'] = data['super_intention']
        i['answer'] = data['answer']
        i['business'] = data['business']
    intention_db.insert(intention)


#以super_intention:intention为标识，intention重复
def write_iqs2mongodb0(intention_db, qa_db):
    data = [{'intention':x['intention'], 'questions':None, 'answer':None,
        'super_intention':x['super_intention'], 'business':None} for x in qa_db.find()]
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
    intention.insert(intention)


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
                t = '正反问'
            L.append([sh.cell_value(i, 0), sh.cell_value(i, 1), t])
    return L

#更新q_a中问题类型
def update_sentence_type_2_q_a(qa_db, L):
    for x in L:
        qa_db.update_many({'super_intention':x[0], 'question':x[1]},
                {'$set':{'q_sentence_type':x[2]}})










