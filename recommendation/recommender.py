import pandas as pd
import json

from math import inf

from recommendation import similarity_measures as sm
# used for time measurement of functions
from recommendation.decorators import timer

# logger to track the application process
from recommendation.logger_config import logging

MOVIE_ID: str = 'movieId'
USER_ID: str = 'userId'
RATING: str = 'rating'
TITLE: str = 'title'
NAME: str = 'name'
CAST: str = 'cast'
CREW: str = 'crew'
JOB: str = 'job'
DIRECTOR: str = 'Director'

IMDB_COL: str = 'imdb'
TMDB_COL: str = 'tmdb'
GENRES_COL: str = 'genres'
MOVIELENS: str = 'movielens'

DIRECTORS_COL: str = 'directors'
ACTORS_COL: str = 'actors'
LANGUAGES_COL: str = 'languages'
KEYWORDS_COL: str = 'keywords'
CREDITS_COL: str = 'credits'
SPOKEN_LANGUAGES: str = 'spoken_languages'

DATA_PATH: str = "resources/"
DATA_PATH_JSON: str = "resources/resources/"

df_movies: pd.DataFrame = pd.read_csv(DATA_PATH + 'movies.csv', encoding="UTF-8",
                                      usecols=[MOVIE_ID, TITLE, GENRES_COL],
                                      dtype={MOVIE_ID: 'int32', TITLE: 'str', GENRES_COL: 'str'})

df_ratings: pd.DataFrame = pd.read_csv(DATA_PATH + 'ratings.csv',
                                       usecols=[USER_ID, MOVIE_ID, RATING],
                                       dtype={USER_ID: 'int32', MOVIE_ID: 'int32', RATING: 'float32'})


class Recommender:

    def __init__(self):
        self.movie_metadata = dict()
        for index, row in df_movies.iterrows():
            try:
                with open(DATA_PATH_JSON + str(row[MOVIE_ID]) + '.json', encoding="UTF-8") as json_file:
                    data = json.load(json_file)
                    directors = set()
                    languages = set()
                    actors = set()
                    genres = set()
                    keywords = set()
                    if IMDB_COL in data:
                        imdb = data[IMDB_COL]
                        Recommender.add_to_collection(imdb[DIRECTORS_COL], directors)
                        languages.add(imdb['originalLanguage'])
                        actor_str = imdb[ACTORS_COL]
                        actor_str = str(actor_str).replace("['Stars: ", "")
                        actor_str = str(actor_str).replace(" | See full cast and crew »']", "")
                        for actor in str(actor_str).split(", "):
                            actors.add(actor)
                        Recommender.add_to_collection(imdb[GENRES_COL], genres)

                    if MOVIELENS in data:
                        movielens_node = data[MOVIELENS]
                        Recommender.add_to_collection(movielens_node[DIRECTORS_COL], directors)
                        Recommender.add_to_collection(movielens_node[LANGUAGES_COL], languages)
                        Recommender.add_to_collection(movielens_node[ACTORS_COL], actors)
                        Recommender.add_to_collection(movielens_node[GENRES_COL], genres)
                    if TMDB_COL in data:
                        tmdb = data[TMDB_COL]
                        for actor in tmdb[CREDITS_COL][CAST]:
                            actors.add(actor[NAME])
                        for crew in tmdb[CREDITS_COL][CREW]:
                            if crew[JOB] == DIRECTOR:
                                directors.add(crew[NAME])
                        for language in tmdb[SPOKEN_LANGUAGES]:
                            languages.add(language[NAME])
                        for genre in tmdb[GENRES_COL]:
                            genres.add(genre[NAME])
                        for keyword in tmdb[KEYWORDS_COL]:
                            keywords.add(keyword[NAME])
                    self.movie_metadata[row[MOVIE_ID]] = {DIRECTORS_COL: directors, LANGUAGES_COL: languages,
                                                          ACTORS_COL: actors, GENRES_COL: genres,
                                                          KEYWORDS_COL: keywords}
            except FileNotFoundError:
                logging.error(f'[init] - No metadata for movie id <{str(row[MOVIE_ID])}>')

    @staticmethod
    def add_to_collection(src, dest):
        """
        Adds the source collection to the destination collection. Needed in cases, where the iterable object is
        neither hashable nor of NonType
        :param src: source collection, which gets added to destination
        :param dest: destination collection
        :return: None
        """
        if src is None or dest is None:
            logging.error(f'[{Recommender.add_to_collection.__name__}] - invalid parameters')
            return
        for elem in src:
            dest.add(elem)

    @staticmethod
    def match_with_bias(src_list: list = list(), match_list: list = list(), bias: int = 1, negative_bias: int = 1,
                        dst_list: list = list()) -> list:
        """
        Adds a score value to the destination list given in parameter
        :param src_list: source list of elements, which will be matched against the matchList
        :param match_list: match list for determining the bias
        :param bias: positive bias is applied if an source list element is found in the match list
        :param negative_bias: negative bias is applied if an source list element is found in the match list
        :param dst_list: destination list in which the score gets saved
        :return: the destination list after calculating the score
        """
        score: int = 0
        for elem in src_list:
            if elem in match_list:
                score += bias
            else:
                score -= negative_bias
        dst_list.append(score)
        return dst_list

    @staticmethod
    def add_score_to_list(meta_data, bias: int, dst_list: list):
        score: int = 0
        for _ in meta_data:
            score += bias
        dst_list.append(score)

    def general_metadata_recommender(self, movie_id: int, bias: int = 15, negative_bias: int = 1):
        """
        general Metadata recommender based on genres, language, actors, directors and keywords with multiple similarity
        measures
        :param movie_id: the id of the movie
        :param bias: the scoring bias
        :param negative_bias: the negative scoring bias
        :return: 5 lists of movie ids, they may be [], maximum length of each list is 5
        """
        genres = self.movie_metadata[movie_id][GENRES_COL]
        languages = self.movie_metadata[movie_id][LANGUAGES_COL]
        actors = self.movie_metadata[movie_id][ACTORS_COL]
        directors = self.movie_metadata[movie_id][DIRECTORS_COL]

        movie_scores_ref: list = list()

        Recommender.add_score_to_list(genres, bias, movie_scores_ref)
        Recommender.add_score_to_list(languages, bias, movie_scores_ref)
        Recommender.add_score_to_list(actors, bias, movie_scores_ref)
        Recommender.add_score_to_list(directors, bias, movie_scores_ref)

        movie_points_manhattan: dict = dict()
        movie_points_euclidean: dict = dict()
        movie_points_chebyshev: dict = dict()
        movie_points_cosine: dict = dict()
        movie_points_jaccard: dict = dict()

        for key, movie in self.movie_metadata.items():
            if key == movie_id:
                continue

            movie_scores = list()
            Recommender.match_with_bias(movie[GENRES_COL], genres, bias, negative_bias, movie_scores)
            Recommender.match_with_bias(movie[LANGUAGES_COL], languages, bias, negative_bias, movie_scores)
            Recommender.match_with_bias(movie[ACTORS_COL], actors, bias, negative_bias, movie_scores)
            Recommender.match_with_bias(movie[DIRECTORS_COL], directors, bias, negative_bias, movie_scores)

            movie_points_manhattan[key] = float(sm.minkowski_distance(movie_scores_ref, movie_scores, 1))
            movie_points_euclidean[key] = float(sm.minkowski_distance(movie_scores_ref, movie_scores, 2))
            movie_points_chebyshev[key] = float(sm.minkowski_distance(movie_scores_ref, movie_scores, inf))
            movie_points_cosine[key] = float(sm.cosine_similarity(movie_scores_ref, movie_scores))
            movie_points_jaccard[key] = float(sm.jaccard_similarity(movie_scores_ref, movie_scores))

        list1 = sorted(movie_points_manhattan, key=lambda x: movie_points_manhattan[x], reverse=False)
        list2 = sorted(movie_points_euclidean, key=lambda x: movie_points_euclidean[x], reverse=False)
        list3 = sorted(movie_points_chebyshev, key=lambda x: movie_points_chebyshev[x], reverse=False)
        list4 = sorted(movie_points_cosine, key=lambda x: movie_points_cosine[x], reverse=True)
        list5 = sorted(movie_points_jaccard, key=lambda x: movie_points_jaccard[x], reverse=True)
        return list1[:5], list2[:5], list3[:5], list4[:5], list5[:5]

    @timer
    def metadata_recommender(self, movie_id: int, bias=15):
        """
        Metadata recommender based on genres, language, actors, directors and keywords
        :param movie_id: the id of the movie
        :param bias: the scoring bias
        :return: list of movie ids, may be [], maximum length is 5
        """
        logging.debug(f'[{self.metadata_recommender.__name__}] - start function with movie id: {movie_id}')
        if movie_id not in self.movie_metadata:
            return []
        genres = self.movie_metadata[movie_id][GENRES_COL]
        languages = self.movie_metadata[movie_id][LANGUAGES_COL]
        actors = self.movie_metadata[movie_id][ACTORS_COL]
        directors = self.movie_metadata[movie_id][DIRECTORS_COL]
        keywords = self.movie_metadata[movie_id][KEYWORDS_COL]

        movie_scores_ref = list()
        Recommender.add_score_to_list(genres, bias, movie_scores_ref)
        Recommender.add_score_to_list(languages, bias, movie_scores_ref)
        Recommender.add_score_to_list(actors, bias, movie_scores_ref)
        Recommender.add_score_to_list(directors, bias, movie_scores_ref)
        Recommender.add_score_to_list(keywords, bias, movie_scores_ref)

        movie_points_cosine = dict()

        for key, movie in self.movie_metadata.items():
            if key == movie_id:
                continue
            movie_scores = list()
            Recommender.match_with_bias(movie[GENRES_COL], genres, bias, 1, movie_scores)
            Recommender.match_with_bias(movie[LANGUAGES_COL], languages, bias, 1, movie_scores)
            Recommender.match_with_bias(movie[ACTORS_COL], actors, bias, 1, movie_scores)
            Recommender.match_with_bias(movie[DIRECTORS_COL], directors, bias, 1, movie_scores)
            Recommender.match_with_bias(movie[KEYWORDS_COL], keywords, bias, 1, movie_scores)

            movie_points_cosine[key] = float(sm.cosine_similarity(movie_scores_ref, movie_scores))
        recommendation = sorted(movie_points_cosine, key=lambda x: movie_points_cosine[x], reverse=True)
        return recommendation[:5]

    @timer
    def metadata_recommender_with_keywords(self, movie_id):
        """
        Metadata recommender based on keywords and genres
        :param movie_id: the id of the movie
        :return: list of movie ids, may be [], maximum length is 5
        """
        logging.debug(
            f'[{self.metadata_recommender_with_keywords.__name__}] - start function with movie id: {movie_id}')
        if movie_id not in self.movie_metadata:
            return []
        genres = self.movie_metadata[movie_id][GENRES_COL]
        keywords = self.movie_metadata[movie_id][KEYWORDS_COL]

        movie_scores_ref = list()
        Recommender.add_score_to_list(genres, 2, movie_scores_ref)
        Recommender.add_score_to_list(keywords, 10, movie_scores_ref)

        movie_points_jaccard = dict()

        for key, movie in self.movie_metadata.items():
            if key == movie_id:
                continue
            movie_scores = list()
            Recommender.match_with_bias(movie[GENRES_COL], genres, 2, 0, movie_scores)
            Recommender.match_with_bias(movie[KEYWORDS_COL], keywords, 10, 5, movie_scores)

            movie_points_jaccard[key] = float(sm.jaccard_similarity(movie_scores_ref, movie_scores))
        recommendation = sorted(movie_points_jaccard, key=lambda x: movie_points_jaccard[x], reverse=True)
        return recommendation[:5]
