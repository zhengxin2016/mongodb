#!/usr/bin/env python3

from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db_name = 'my_data'
db = client[db_name]
person = db['person']
for row in person.find():
    print(row)

print('-------------------------')

data = person.find_one({"name":"jack"})
print(data)

print('-------------------------')

for row in person.find(projection = ["name"]):
    print(row)

print('-------------------------')

for row in person.find({"age":27}, ["name"]):
    print(row)
print('-------------------------')

person.insert({"name":"AAA", "age":100})
person.insert([{"name":"BBB", "age":10}, {"name":"CCC", "age":11}])
for row in person.find():
    print(row)
print('-------------------------')


person.update({"name":"AAA"}, {'$set':{'name':'AAAA','age':10}})
for row in person.find():
    print(row)
print('-------------------------')

for r in person.find().sort([('age', 1), ('name', 1)]):
    print(r)
print('-------------------------')


person.remove({"name":"AAAA"})
person.remove({"name":"BBB"})
person.remove({"name":"CCC"})
for row in person.find():
    print(row)
print('-------------------------')




