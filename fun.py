#!/usr/bin/env python3

import os
import random
import pandas as pd
import numpy as np
import xlrd
from pymongo import MongoClient

#字符清理
def clean_str(string):
    string.strip()
    string = string.replace(' ', '')
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
        for i in df['业务']:
            D['business'].append(str(i))
        for i in df['意图']:
            D['intention'].append(str(i))
        for i in df['上级意图']:
            D['super_intention'].append(str(i))
        for i in df['等价描述']:
            D['equal_questions'].append(str(i))

        if D['answer'][-1] != 'nan':
            D['question'].append('nan')
            D['answer'].append('nan')
            D['business'].append('nan')
            D['intention'].append('nan')
            D['super_intention'].append('nan')
            D['equal_questions'].append('nan')

#将读取data.xlsx的内容写到data.txt中
#输入：修正后的data.xlsx内容 Dict
#输出：无
def data_xlsx2txt(Dict):
    f = open('./data.txt', 'w')
    i = 0
    while i < len(Dict['question']):
        f.write(Dict['question'][i]+' '+Dict['answer'][i]+' '
                        +Dict['business'][i]+' '+Dict['intention'][i] +' '
                        +Dict['super_intention'][i]+' '
                        +Dict['equal_questions'][i]+'\n')
        i += 1
    f.close()

#生成问答列表
#输入：修正后的data.xlsx内容 Dict
#输出：问答列表 Qs_A[]
def generate_Qs_A(Dict):
    Qs_A = []
    i = 0
    while i < len(Dict['question']):
        q = Dict['equal_questions'][i].split('/')
        q.append(Dict['question'][i])
        Qs_A.append({'questions':q,
            'answer':Dict['answer'][i],
            'business':Dict['business'][i],
            'intention':Dict['intention'][i],
            'super_intention':Dict['super_intention'][i]})
        i += 1
    return Qs_A

#按对话切分列表
#输入：Qs_A[]  [{1},{2},{'nan'},{3}]
#输出：Q_A[]   [[{1},{2}], [{3}]]
def split_dialogue(Qs_A):
    Q_A = []
    start = 0
    end = 0
    for r in Qs_A:
        if r['answer'] == 'nan':
            Q_A.append(Qs_A[start:end])
            start = end + 1
            end += 1
            continue
        end += 1
    return Q_A

#
#
#
def write_raw_data2mongodb(raw_db, Q_A):
    for d in Q_A:
        q_list = []
        a_list = []
        business_list = []
        intention_list = []
        super_intention_list = []
        for q_a in d:
            q_list.append(q_a['questions'])
            a_list.append(q_a['answer'])
            business_list.append(q_a['business'])
            intention_list.append(q_a['intention'])
            super_intention_list.append(q_a['super_intention'])
        raw_db.insert({"question_list":q_list,
                "answer_list":a_list,
                "business_list":business_list,
                "intention_list":intention_list,
                "super_intention_list":super_intention_list})

#产生一个对话 
#输入：[[第一句], [第二句],[第三句]]
#输出：[第一句, 第二句,第三句]
def generate_dialog(q_a):
    a = []
    for r in q_a:
        index = random.randint(0, len(r['questions'])-1)
        a.append([r['questions'][index], r['answer'], r['business'],\
                r['intention'], r['super_intention']])
    return a

def write_2(dialog_db, raw_db):
    for d in raw_db.find():
        N = 0
        for q in d['question_list']:
            N += len(q)
        while N > 0:
            q_list = []
            for q in d['question_list']:
                i = random.randint(0, len(q) - 1)
                q_list.append(q[i])
            dialog_db.insert({"question_list":q_list,
                    "answer_list":d['answer_list'],
                    "business_list":d['business_list'],
                    "intention_list":d['intention_list'],
                    "super_intention_list":d['super_intention_list']})
            N -= 1

#随机生成一组对话
#输入：对话列表 Q_A[]
#输出：对话列表实例 dialogues[]
def generate_dialog_list(Q_A):
    dialogues = []
    N = 0
    for q_a in Q_A:
        for r in q_a:
            N += len(r['questions'])
        while N > 0:
            dialogues.append(generate_dialog(q_a))
            N -= 1
    random.shuffle(dialogues)#列表元素打乱
    return dialogues


#以对话为单位存到数据库中
#输入：对话列表
#输出：无
def write_dialog2mongodb(dialog_db, dialogues):
    for d in dialogues:
        q_list = []
        a_list = []
        business_list = []
        intention_list = []
        super_intention_list = []
        for s in d:
            q_list.append(s[0])
            a_list.append(s[1])
            business_list.append(s[2])
            intention_list.append(s[3])
            super_intention_list.append(s[4])
        dialog_db.insert({"question_list":q_list,
                "answer_list":a_list,
                "business_list":business_list,
                "intention_list":intention_list,
                "super_intention_list":super_intention_list})

#以一问一答为单位存到数据库中
#输入：一个对话
#输出：无
def write_qa2mongodb(qa_db, dia):
    i = 0
    while i < len(dia['question_list']):
        qa_db.insert({"ID":str(dia['_id'])+'_'+ str(i),
                "question":dia['question_list'][i],
                "answer":dia['answer_list'][i],
                "business":dia['business_list'][i],
                "intention":dia['intention_list'][i],
                "super_intention":dia['super_intention_list'][i]})
        i += 1

