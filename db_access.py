import os
import datetime
import pprint

import json

import pymongo
from pymongo import MongoClient

pp = pprint.PrettyPrinter(indent=4)

def setup():
    client = MongoClient()
    client = MongoClient('mongodb://YourUsername:YourPasswordHere@localhost:27017/your-database-name')
    db = client['your-database-name']
    posts = db.posts
    return posts

def insert(posts):
    inserted_ids = []
    for subdir, dirs, files in os.walk("documents"):
        for file in files:
            with open(os.path.join(subdir, file)) as json_file:
                data = json.load(json_file)
                data['date'] = datetime.datetime.utcnow()

                ## Insert document
                post_id = posts.insert_one(data).inserted_id
                print(post_id)
                inserted_ids.append(str(post_id))
    return { "Inserted_ids" : inserted_ids }

## Query
def query(posts, date, panel):
    # get verified record for what we set on the network
    packaged_document = {}
    verified_documents = []
    for doc in posts.find(
            {
                "date": {"$gt": date},
                "verified": True,
                "panel": panel
            }
        ):
        verified_documents.append(doc)

    if not verified_documents:
        print('no verified documents found')
        return packaged_document

    first_doc = verified_documents[0]
    print('verified doc with a correlation ID of: ', verified_documents[0]['correlation_id'])
    print(first_doc)
    packaged_document = first_doc
    print('--------------')
    
    # given returned verified record, get the top 3 alternatives calculated for that conflict id
    x = posts.find(
        {
            "conflict_id": first_doc['conflict_id'], # these two first attributes mean we will reliably get back alternatives for that simulation e2e run
            "correlation_id": first_doc['correlation_id'],
            "alternative_id": {"$exists": True},
            "alternative_preference": {"$in": [ 1, 2, 3]}
        }
    )
    
    alt_documents = []
    for altx in x:
        pp.pprint(altx)
        alt_documents.append(altx)

    packaged_document['alternatives'] = alt_documents
    return packaged_document


def delete_query(posts):
    myquery = {"conflict_id": "qw122a_ke921r_BRGTN_07_02_2020"}
    x = posts.delete_many(myquery)
    print(x.deleted_count, " documents deleted.")
    return { "deleted_count" : x.deleted_count }