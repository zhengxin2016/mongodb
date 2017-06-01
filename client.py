#!/usr/bin/env python3

from pymongo import MongoClient

#打开Mongodb，集合：‘data’
client = MongoClient('127.0.0.1', 27017)
db_name = 'data'
db = client[db_name]

#write dialogue to mongodb, doc:'dialogue'
#random 20*[]
dia_db = db['dialogue']
qa_db = db['q_a']
for d in dia_db.find():
    print(d['answer_list'])
