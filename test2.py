import configparser
import Artist
import codecs
import json



data = json.load(open("data/comments.json"))
comments = data

print (comments)
d1 = {3: "three"}



data2 =  { "3": {
"id" : 2,
"name" : "darwon",
"message" : "message"
} }
comments.update(data2)


with open('data/comments.json', 'w', encoding='utf8') as outfile:

    json.dump(comments, outfile)
