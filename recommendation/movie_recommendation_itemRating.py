import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from recommendation.decorators import timer

# logger to track the application process
from recommendation.logger_config import logging


class MovieRecommendationItemRating:
    @staticmethod
    def data_initialization(self):
        logging.debug(f'[{MovieRecommendationItemRating.data_initialization.__name__}] - start of function')
        df_movies, df_ratings = self.read_files()
        combine_movie_rating = pd.merge(df_ratings, df_movies, on='movieId')
        combine_movie_rating = combine_movie_rating.dropna(axis=0, subset=['title'])
        movie_ratingCount = (combine_movie_rating.
            groupby(by=['title'])['rating'].
            count().
            reset_index().
            rename(columns={'rating': 'totalRatingCount'})
        [['title', 'totalRatingCount']]
            )
        rating_with_totalRatingCount = combine_movie_rating.merge(movie_ratingCount, left_on='title', right_on='title',
                                                                  how='left')
        user_rating = rating_with_totalRatingCount.drop_duplicates(['userId', 'title'])
        movie_user_rating_pivot = pd.pivot_table(user_rating, index='userId', columns='title', values='rating').fillna(
            0)
        X = movie_user_rating_pivot.values.T

        # calculating correlation matrix i.e.model
        SVD = TruncatedSVD(n_components=12, random_state=17)
        matrix = SVD.fit_transform(X)
        corr = np.corrcoef(matrix)
        movie_title = movie_user_rating_pivot.columns
        return movie_title, corr, df_movies

    # reading data files
    def read_files(self):
        logging.debug(f'[{self.read_files.__name__}] - reading csv files')
        df_movies = pd.read_csv('resources/movies.csv', encoding="Latin1")
        df_ratings = pd.read_csv('resources/ratings.csv', usecols=['userId', 'movieId', 'rating'])
        return df_movies, df_ratings

    # get recommendations
    @staticmethod
    @timer
    def get_similar_movies_based_on_itemRating(self, input_movie_title):
        logging.debug(
            f'[{MovieRecommendationItemRating.get_similar_movies_based_on_itemRating.__name__}] - '
            f'start of function with movie title <{input_movie_title}>')
        movie_title, model, df_movies = self.data_initialization(self)
        movie_title_list = list(movie_title)
        movie_index = movie_title_list.index(input_movie_title)
        sim_scores = list(enumerate(model[movie_index]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        movie_indices = [i[0] for i in sim_scores]
        similar_movies = pd.DataFrame()
        similar_movies['title'] = movie_title[movie_indices]
        logging.debug(
            f'[{MovieRecommendationItemRating.get_similar_movies_based_on_itemRating.__name__}] - item-rating executed')
        return similar_movies.to_dict()

# if __name__ == '__main__':
#
#     input_movie = 'Exorcist The (1973)'
#     movie_recommendations = get_similar_movies_based_on_content(input_movie)
#     print(movie_recommendations)
