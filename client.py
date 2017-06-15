#!/usr/bin/env python3

from pymongo import MongoClient

class ReadData():
    def __init__(self):
        self.db = MongoClient('127.0.0.1', 27017).data

    def intention_answer(self, intention):
        try:
            data = self.db.intention.find_one({'intention':intention},
                    {'_id':0, 'answer':1})
            return data['answer']
        except Exception:
            return None

    def intention_questions(self, intention):
        try:
            data = self.db.intention.find_one({'intention':intention},
                    {'_id':0, 'questions':1})
            return data['questions']
        except Exception:
            return None

    def dialogue(self):
        try:
            data = [[x['question_list'], x['answer_list']] for x in
                    self.db.dialogue.find()]
            return data
        except Exception:
            return None
    



if __name__ == '__main__': 
    readData = ReadData()

    print('[存款五万以下] answer:')
    print(readData.intention_answer('存款五万以下'))
    print('[存款五万以下] question_list:')
    print(readData.intention_questions('存款五万以下'))
    print('-------------------------------------')
    print('[XXX] answer:')
    print(readData.intention_answer('XXX'))
    print('[XXX] question_list:')
    print(readData.intention_questions('XXX'))










