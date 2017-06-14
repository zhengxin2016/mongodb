#!/usr/bin/env python3

from pymongo import MongoClient

class ReadData():
    def __init__(self):
        self.db = MongoClient('127.0.0.1', 27017).data

    def intention_answer(self, intention):
        data = self.db.intention.find_one({'intention':intention},
                {'_id':0, 'answer':1})
        return data['answer']

    def intention_questions(self, intention):
        data = self.db.intention.find_one({'intention':intention},
                {'_id':0, 'questions':1})
        return data['questions']

    def dialogue(self):
        data = [[x['question_list'], x['answer_list']] for x in
                self.db.dialogue.find()]
        return data




if __name__ == '__main__': 
    readData = ReadData()

    print(readData.intention_answer('存款五万以下'))
    print('-------------------------------------')
    print(readData.intention_questions('存款五万以下'))
