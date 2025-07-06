from sklearn.feature_extraction.text import CountVectorizer
from nltk import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from numpy.linalg import norm
import numpy as np
import math


class Evaluate:
    def __init__(self):
        pass

    def content_based(self, summary, full_text):
        sentences = sent_tokenize(full_text)
        vectorizer = CountVectorizer().fit(sentences)
        full_text_vector = vectorizer.transform([full_text])
        summary_vector = vectorizer.transform([summary])
        score = cosine_similarity(full_text_vector, summary_vector)[0][0]
        return score