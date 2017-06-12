#!/usr/bin/env python3

from pymongo import MongoClient

class ReadData():
    def __init__(self):
        self.db = MongoClient('10.89.14.67', 27017).data

    def intention_answer(self):
        data = [x['intention'] +':'+ x['answer'] for x in self.db.q_a.find()]
        return list(set(data))

    def dialogue(self):
        data = [[x['question_list'], x['answer_list']] for x in
                self.db.dialogue.find()]
        return data
    def intention_group(self):
        intention = [x for x in self.db.q_a.distinct('intention')]
        print(dir(self.db.q_a))



if __name__ == '__main__': 
    readData = ReadData()

    for i in readData.intention_answer():
        pass#print(i)
    readData.intention_group()
