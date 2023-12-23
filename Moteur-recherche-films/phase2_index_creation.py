import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["movies-indexes"]

# Création des collections MongoDB
db.create_collection("title_index")
db.create_collection("description_index")
db.create_collection("genre_index")
db.create_collection("stars_index")
db.create_collection("year_index")

# Chargement de données depuis le fichier movies.json
with open("movies.json", "r") as data_file:
    movies = json.load(data_file)

def load_stop_words():
    stop_words = set(stopwords.words('english'))
    stop_words.update(['the', ':', "'s", ',', '-', '.', '!', '&', "'", '?'])
    return stop_words

def storeIndexInMongoDB(index, collection_name):
    collection = db[collection_name]
    for key, value in index.items():
        # Ajout des données à la collection MongoDB
        collection.insert_one({"key": key, "value": value})

def getIndex(key, collection_name, stop_words):
    index = dict()
    for movie in movies:
        word_tokens = word_tokenize(movie[key].lower())
        filtered_tokens = [token for token in word_tokens if token not in stop_words]
        for token in filtered_tokens:
            if token not in index:
                index[token] = [movie['id']]
            else:
                index[token].append(movie['id'])

    # Stockage de l'index dans MongoDB
    storeIndexInMongoDB(index, collection_name)

    return index


def groupIndex(key, collection_name):
    index = dict()
    for movie in movies:
        for i in movie[key]:
            if i.lower() not in index:
                index[i.lower()] = [movie['id']]
            else:
                index[i.lower()].append(movie['id'])

    # Stockage de l'index dans MongoDB
    storeIndexInMongoDB(index, collection_name)

    return index


# Définition des stop words
stop_words = set(stopwords.words('english'))

# Création des index
title_index = getIndex('title', "title_index", stop_words)
description_index = getIndex('description', "description_index", stop_words)
genre_index = groupIndex('genre', "genre_index")
stars_index = groupIndex('stars', "stars_index")

year_index = dict()
for movie in movies:
    if movie['year'] not in year_index:
        year_index[movie['year']] = [movie['id']]
    else:
        year_index[movie['year']].append(movie['id'])

# Stockage de l'index dans MongoDB
storeIndexInMongoDB(year_index, "year_index")

if __name__ == '__main__':
    print("Start of the script")
    print(stop_words)
    print(title_index)
    print("End of the script")
