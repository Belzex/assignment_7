import sklearn
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

import pandas as pd

from recommendation import recommender

df_movies: pd.DataFrame = recommender.df_movies
df_ratings: pd.DataFrame = recommender.df_ratings

# pivot ratings into movie features
df_movie_features = df_ratings.pivot(
    index=recommender.MOVIE_ID,
    columns=recommender.USER_ID,
    values=recommender.RATING
).fillna(0)

#  converting movie features to scipy sparse matrix
sparse_movie_features = csr_matrix(df_movie_features.values)

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=15, n_jobs=1)

MOVIE_ID: str = recommender.MOVIE_ID


class KNN:

    def __init__(self, movie_path: str, ratings_path: str):
        self.movie_path: str = movie_path
        self.ratings_path: str = ratings_path
        self.movie_rating_threshold: int = 3
        self.user_rating_threshold: int = 3
        self.model = NearestNeighbors()
        self.sparse_movie_users: csr_matrix = csr_matrix()

    def make_recommendations(self, movie: str, num_recommendations: int):
        pass

    def _prepare_data(self):
        df_movies_count = pd.DataFrame(df_ratings.groupby(MOVIE_ID).size(),
                                       columns=['count'])
        df_users_count = pd.DataFrame(df_ratings.groupby(MOVIE_ID).size(),
                                      columns=['count'])

        popular_movies: list = list(set(df_movies_count.query('count >= @self.movie_rating_threshold').index))
        movie_filter = df_ratings[MOVIE_ID]

# sparse_movie_user
