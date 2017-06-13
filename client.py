#!/usr/bin/env python3

from pymongo import MongoClient

class ReadData():
    def __init__(self):
        self.db = MongoClient('127.0.0.1', 27017).data

    def intention_group(self):
        intention = [x for x in self.db.q_a.distinct('intention')]
        intention_answer = {x['intention']:x['answer'] for x in self.db.q_a.find()}
        intention_questions = {}
        for i in intention:
            intention_questions[i] = list(set([x['question'] for x in self.db.q_a.find({'intention':i})]))
        return intention_answer, intention_questions

    def dialogue(self):
        data = [[x['question_list'], x['answer_list']] for x in
                self.db.dialogue.find()]
        return data




if __name__ == '__main__': 
    readData = ReadData()

    for i in readData.intention_group():
        pass#print(i)
