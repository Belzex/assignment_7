from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

import pandas as pd
from fuzzywuzzy import fuzz

MOVIE_ID: str = 'movieId'
USER_ID: str = 'userId'
RATING: str = 'rating'
TITLE: str = 'title'

IMDB_COL: str = 'imdb'
GENRES_COL: str = 'genres'
MOVIELENS: str = 'movielens'

DIRECTORS_COL: str = 'directors'
ACTORS_COL: str = 'actors'
LANGUAGES_COL: str = 'languages'

DATA_PATH: str = "../resources/"

df_movies: pd.DataFrame = pd.read_csv(DATA_PATH + 'movies.csv', encoding="UTF-8",
                                      usecols=[MOVIE_ID, TITLE, GENRES_COL],
                                      dtype={MOVIE_ID: 'int32', TITLE: 'str', GENRES_COL: 'str'})

df_ratings: pd.DataFrame = pd.read_csv(DATA_PATH + 'ratings.csv',
                                       usecols=[USER_ID, MOVIE_ID, RATING],
                                       dtype={USER_ID: 'int32', MOVIE_ID: 'int32', RATING: 'float32'})

# pivot ratings into movie features
df_movie_features = df_ratings.pivot(
    index=MOVIE_ID,
    columns=USER_ID,
    values=RATING
).fillna(0)

#  converting movie features to scipy sparse matrix
sparse_movie_features = csr_matrix(df_movie_features.values)

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=15, n_jobs=1)

MOVIE_ID: str = MOVIE_ID
USER_ID: str = USER_ID
RATING: str = RATING


class KNN:

    def __init__(self, movie_rating_threshold: int = 0, user_rating_threshold: int = 0):
        self.movie_rating_threshold: int = movie_rating_threshold
        self.user_rating_threshold: int = user_rating_threshold
        self.model = NearestNeighbors()

    def make_recommendations(self, movie_title: str, n_recommendations: int):
        """
        make top n movie recommendations
        Parameters
        ----------
        movie_title: str, name of user input movie
        n_recommendations: int, top n recommendations
        """
        # get data
        movie_user_mat_sparse, hashmap = self._prepare_data()
        # get recommendations
        raw_recommends = self._inference(
            self.model, movie_user_mat_sparse, hashmap,
            movie_title, n_recommendations)
        # print results
        reverse_hashmap = {v: k for k, v in hashmap.items()}
        print('Recommendations for {}:'.format(movie_title))
        for i, (idx, dist) in enumerate(raw_recommends):
            print('{0}: {1}, with distance '
                  'of {2}'.format(i + 1, reverse_hashmap[idx], dist))

    def _prepare_data(self):
        df_movies_count = pd.DataFrame(df_ratings.groupby(MOVIE_ID).size(),
                                       columns=['count'])
        popular_movies: list = list(set(df_movies_count.query('count >= @self.movie_rating_threshold').index))
        movie_filter = df_ratings[MOVIE_ID].isin(popular_movies).values

        df_users_count = pd.DataFrame(df_ratings.groupby(MOVIE_ID).size(),
                                      columns=['count'])
        active_users: list = list(set(df_users_count.query('count >= @self.user_rating_threshold').index))
        users_filter = df_ratings[USER_ID].isin(active_users).values

        # filtered dataframe of movies and active users
        df_filtered_ratings: pd.DataFrame = df_ratings[movie_filter & users_filter]

        user_movie_pivot_mat: pd.DataFrame = df_filtered_ratings.pivot(
            index=MOVIE_ID,
            columns=USER_ID,
            values=RATING
        ).fillna(0)

        sparse_movie_user_matrix = csr_matrix(user_movie_pivot_mat.values)

        # create mapper from movie title to index
        movie_dictionary: dict = {
            movie: i for i, movie in
            enumerate(list(df_movies.set_index('movieId').loc[user_movie_pivot_mat.index].title))
        }

        # clean up
        del df_users_count, df_movies_count
        del movie_filter, users_filter, user_movie_pivot_mat

        return sparse_movie_user_matrix, movie_dictionary

    def _inference(self, model, data, movie_dictionary: dict,
                   movie_title: str, n_recommendations: int):
        """
                return top n similar movie recommendations based on user's input movie
                Parameters
                ----------
                model: sklearn model, knn model
                data: movie-user matrix
                movie_dictionary: dict, map movie title name to index of the movie in data
                movie_title: str, name of user input movie
                n_recommendations: int, top n recommendations
                Return
                ------
                list of
        """
        model.fit(data)

        # get input movie index
        movieId = self._fuzzy_matching(movie_dictionary, movie_title)
        distances, indices = model.kneighbors(
            data[movieId],
            n_neighbors=n_recommendations + 1)
        # get list of raw idx of recommendations
        raw_recommends = \
            sorted(
                list(
                    zip(
                        indices.squeeze().tolist(),
                        distances.squeeze().tolist()
                    )
                ),
                key=lambda x: x[1]
            )[:0:-1]
        return raw_recommends

    def _fuzzy_matching(self, movie_dictionary: dict, movie: str, ratio_threshold: int = 60):
        """
        return the closest match via fuzzy ratio.
        If no match found, return None
        Parameters
        ----------
        movie_dictionary: dict, map movie title name to index of the movie in data
        movie: str, name of user input movie
        Return
        ------
        index of the closest match
        """
        match_tuple: list = list()

        # find matches for each title
        for title, movieId in movie_dictionary.items():
            ratio = fuzz.ratio(title.lower(), movie.lower())
            if ratio >= ratio_threshold:
                match_tuple.append((title, movieId, ratio))

        match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]

        return match_tuple[0][1] if match_tuple else None


if __name__ == '__main__':
    knn = KNN(5, 3)
    knn.make_recommendations('Lord of the Rings: The Return of the King', 15)
