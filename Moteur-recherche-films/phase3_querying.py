import json

from sklearn.exceptions import UndefinedMetricWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import warnings
from operator import itemgetter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#import nltk
#nltk.download('stopwords')
#nltk.download('punkt')

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    stop_words.update(['the', ':', "'s", ',', '-', '.', '!', '&', "'", '?'])
    word_tokens = word_tokenize(text)
    filtered_tokens = [word.lower() for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_tokens)

def get_relevant_documents(index): # Fonction pour calculer la similarité entre requête et documents et selectionner les 5 documents les plus pertinents
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(index)
    cosine_similarities = linear_kernel(tfidf[-1], tfidf).flatten()
    #Sélectionner les 5 documents les plus pertinents
    relevant_docs_index = cosine_similarities.argsort()[-6:-1][::-1]
    relevant_docs_index = [index for index in relevant_docs_index if cosine_similarities[index] != 0.0]
    return relevant_docs_index

def get_movies(query): # Fonction pour récupérer les informations des films plus pertinents à partir du fichier JSON
    with open("movies.json", "r") as data_file:
        movies = json.load(data_file)

    movie_description = []
    stars = []
    genre = []
    directors = []
    title = []
    year = []
    rating = []

    for movie in movies:
        movie_description.append(remove_stopwords(movie['description']))
        stars.append(' '.join(movie['stars']))
        genre.append(' '.join(movie['genre']))
        directors.append(' '.join(movie['directors']))
        title.append(remove_stopwords(movie['title']))
        year.append(movie['year'])
        rating.append(movie['rating'])

    is_rating_query = all([char.isdigit() or char == '.' for char in query])
    is_year_query = all([char.isdigit() for char in query])
    indices = []

    if is_year_query: # si c'est une requête d'année
        indices = [i for i, x in enumerate(year) if str(x) == str(query)]

    if is_rating_query: # si c'est une requête de note
        indices = [i for i, x in enumerate(rating) if x == query]

    if len(indices):
        relevant_movies = itemgetter(*indices)(movies)
        return relevant_movies

    query_words = remove_stopwords(query).split()
    print(query_words)

    # Ajout de la requête aux listes pour la vectorisation
    title.extend(query_words)
    genre.extend(query_words)
    stars.extend(query_words)
    directors.extend(query_words)
    movie_description.extend(query_words)
    year.extend(query_words)

    relevant_movies_index = set() # Initialisation d'un ensemble vide pour les index de films pertinents.
    print(relevant_movies_index)
    relevant_movies_index.update(get_relevant_documents(title))
    relevant_movies_index.update(get_relevant_documents(genre))
    relevant_movies_index.update(get_relevant_documents(stars))
    relevant_movies_index.update(get_relevant_documents(directors))
    relevant_movies_index.update(get_relevant_documents(movie_description))
    relevant_movies_index.update(get_relevant_documents(year))

    # Conversion de l'ensemble en liste et l'afficher
    relevant_movies_index = list(relevant_movies_index)
    print(relevant_movies_index)

    # pour retourner les films correspondants aux indices retournés précédemment
    if relevant_movies_index:
        relevant_movies = itemgetter(*relevant_movies_index)(movies)
    else:
        relevant_movies = []

    if type(relevant_movies) == dict: # Si le type de films pertinents est un dictionnaire, on le retourne dans une liste
        return [relevant_movies]

    return list(relevant_movies)

def evaluate_metrics(true_labels, predicted_labels):
    """
    Évalue les métriques de recherche d'information : matrice de confusion, précision, rappel et score F1.

    Paramètres :
    - true_labels : Liste des vraies étiquettes (vérité terrain) pour chaque film.
    - predicted_labels : Liste des étiquettes prédites pour chaque film.

    Retourne :
    - Matrice de confusion, Précision, Rappel, Score F1
    """
    confusion = confusion_matrix(true_labels, predicted_labels)

    # Utilisation du paramètre zero_division pour éviter les avertissements
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UndefinedMetricWarning)
        precision = precision_score(true_labels, predicted_labels, average='weighted', zero_division=1)
        recall = recall_score(true_labels, predicted_labels, average='weighted', zero_division=1)
        f1 = f1_score(true_labels, predicted_labels, average='weighted', zero_division=1)

    return confusion, precision, recall, f1


def display_metrics(confusion, precision, recall, f1):
    """
    Affiche les métriques de recherche d'information.

    Paramètres :
    - confusion : Matrice de confusion.
    - precision : Précision.
    - recall : Rappel.
    - f1 : Score F1.
    """
    print("Matrice de Confusion :")
    print(confusion)
    print("\nPrécision : {:.4f}".format(precision))
    print("Rappel : {:.4f}".format(recall))
    print("Score F1 : {:.4f}".format(f1))


# Fonction pour tester
if __name__ == '__main__':
    result = get_movies("Oliver Hirschbiegel")
    print(result)

    # Extraire les genres réels des films
    true_labels = ["Drama", "Thriller"]  # Remplacez par les genres réels de vos films
    # Extraire les genres prédits à partir des résultats de get_movies
    if result:
        predicted_labels = result[0]['genre'] if isinstance(result[0]['genre'], list) else [result[0]['genre']]
        print(predicted_labels)
    else:
        predicted_labels = []  # Vous devez définir un comportement par défaut en cas de résultat vide
        print(predicted_labels)

    # Évaluer les métriques
    confusion, precision, recall, f1 = evaluate_metrics(true_labels, predicted_labels)

    # Afficher les métriques
    display_metrics(confusion, precision, recall, f1)