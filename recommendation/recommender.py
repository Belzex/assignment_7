import pandas as pd


class Recommender:

    def __init__(self):
        self.df_movies = pd.read_csv("../resources/movies.csv", encoding="Latin1")
