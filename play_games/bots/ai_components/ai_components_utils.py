from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer

wordnet_lemmatizer = WordNetLemmatizer()
lancaster_stemmer = LancasterStemmer()

def arr_not_in_word(word, arr):
    if word in arr:
        return False
    lemm = wordnet_lemmatizer.lemmatize(word)
    lancas = lancaster_stemmer.stem(word)
    for i in arr:
        if i == lemm or i == lancas:
            return False
        if i.find(word) != -1:
            return False
        if word.find(i) != -1:
            return False
    return True