import pandas as pd
import json
import os

from math import inf

from recommendation import similarity_measures as sm

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
                with open(DATA_PATH + str(row[MOVIE_ID]) + '.json', encoding="UTF-8") as json_file:
                    data = json.load(json_file)
                    directors = set()
                    languages = set()
                    actors = set()
                    genres = set()
                    keywords = set()
                    if IMDB_COL in data:
                        imdb = data[IMDB_COL]
                        Recommender.addToCollection(imdb[DIRECTORS_COL], directors)
                        languages.add(imdb['originalLanguage'])
                        actor_str = imdb[ACTORS_COL]
                        actor_str = str(actor_str).replace("['Stars: ", "")
                        actor_str = str(actor_str).replace(" | See full cast and crew »']", "")
                        for actor in str(actor_str).split(", "):
                            actors.add(actor)
                        Recommender.addToCollection(imdb[GENRES_COL], genres)

                    if MOVIELENS in data:
                        movielensNode = data[MOVIELENS]
                        Recommender.addToCollection(movielensNode[DIRECTORS_COL], directors)
                        Recommender.addToCollection(movielensNode[LANGUAGES_COL], languages)
                        Recommender.addToCollection(movielensNode[ACTORS_COL], actors)
                        Recommender.addToCollection(movielensNode[GENRES_COL], genres)
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
                print('no metadata for movie ' + str(row[MOVIE_ID]))

    @staticmethod
    def addToCollection(src, dest):
        """
        Adds the source collection to the destination collection. Needed in cases, where the iterable object is
        neither hashable nor of NonType
        :param src: source collection, which gets added to destination
        :param dest: destination collection
        :return: None
        """
        if src is None or dest is None:
            return
        for elem in src:
            dest.add(elem)

    @staticmethod
    def matchWithBias(srcList: list = list(), matchList: list = list(), bias: int = 1, negBias: int = 1,
                      dstList: list = list()) -> list:
        """
        Adds a score value to the destination list given in parameter
        :param srcList: source list of elements, which will be matched against the matchList
        :param matchList: match list for determining the bias
        :param bias: positive bias is applied if an source list element is found in the match list
        :param negBias: negative bias is applied if an source list element is found in the match list
        :param dstList: destination list in which the score gets saved
        :return: the destiniation list after calculating the score
        """
        score: int = 0
        for elem in srcList:
            if elem in matchList:
                score += bias
            else:
                score -= negBias
        dstList.append(score)
        return dstList

    @staticmethod
    def addScoreToList(metaData, bias: int, dstList: list):
        score: int = 0
        for _ in metaData:
            score += bias
        dstList.append(score)

    def recommendMovies(self, movieId: int, bias: int = 15, negBias: int = 1):
        genres: list = self.movie_metadata[movieId][GENRES_COL]
        languages: list = self.movie_metadata[movieId][LANGUAGES_COL]
        actors: list = self.movie_metadata[movieId][ACTORS_COL]
        directors: list = self.movie_metadata[movieId][DIRECTORS_COL]

        movieScoresRef: list = list()

        Recommender.addScoreToList(genres, bias, movieScoresRef)
        Recommender.addScoreToList(languages, bias, movieScoresRef)
        Recommender.addScoreToList(actors, bias, movieScoresRef)
        Recommender.addScoreToList(directors, bias, movieScoresRef)

        moviePointsManhattan: dict = dict()
        moviePointsEuclidean: dict = dict()
        moviePointsChebyshev: dict = dict()
        moviePointsCosine: dict = dict()
        moviePointsJaccard: dict = dict()

        for key, movie in self.movie_metadata.items():
            if key == movieId:
                continue

            movieScores = list()
            Recommender.matchWithBias(movie[GENRES_COL], genres, bias, negBias, movieScores)
            Recommender.matchWithBias(movie[LANGUAGES_COL], languages, bias, negBias, movieScores)
            Recommender.matchWithBias(movie[ACTORS_COL], actors, bias, negBias, movieScores)
            Recommender.matchWithBias(movie[DIRECTORS_COL], directors, bias, negBias, movieScores)

            moviePointsManhattan[key] = float(sm.minkowski_distance(movieScoresRef, movieScores, 1))
            moviePointsEuclidean[key] = float(sm.minkowski_distance(movieScoresRef, movieScores, 2))
            moviePointsChebyshev[key] = float(sm.minkowski_distance(movieScoresRef, movieScores, inf))
            moviePointsCosine[key] = float(sm.cosine_similarity(movieScoresRef, movieScores))
            moviePointsJaccard[key] = float(sm.jaccard_similarity(movieScoresRef, movieScores))

        list1 = sorted(moviePointsManhattan, key=lambda x: moviePointsManhattan[x], reverse=False)
        list2 = sorted(moviePointsEuclidean, key=lambda x: moviePointsEuclidean[x], reverse=False)
        list3 = sorted(moviePointsChebyshev, key=lambda x: moviePointsChebyshev[x], reverse=False)
        list4 = sorted(moviePointsCosine, key=lambda x: moviePointsCosine[x], reverse=True)
        list5 = sorted(moviePointsJaccard, key=lambda x: moviePointsJaccard[x], reverse=True)
        return list1[:5], list2[:5], list3[:5], list4[:5], list5[:5]

    def recommendMovies1(self, movieId, n=15):
        genres = self.movie_metadata[movieId]['genres']
        languages = self.movie_metadata[movieId]['languages']
        actors = self.movie_metadata[movieId]['actors']
        directors = self.movie_metadata[movieId]['directors']
        keywords = self.movie_metadata[movieId]['keywords']

        movieScoresRef = list()
        Recommender.addScoreToList(genres, n, movieScoresRef)
        Recommender.addScoreToList(languages, n, movieScoresRef)
        Recommender.addScoreToList(actors, n, movieScoresRef)
        Recommender.addScoreToList(directors, n, movieScoresRef)
        Recommender.addScoreToList(keywords, n, movieScoresRef)

        moviePointsCosine = dict()

        for key, movie in self.movie_metadata.items():
            if key == movieId:
                continue
            movieScores = list()
            Recommender.matchWithBias(movie[GENRES_COL], genres, n, 1, movieScores)
            Recommender.matchWithBias(movie[LANGUAGES_COL], languages, n, 1, movieScores)
            Recommender.matchWithBias(movie[ACTORS_COL], actors, n, 1, movieScores)
            Recommender.matchWithBias(movie[DIRECTORS_COL], directors, n, 1, movieScores)
            Recommender.matchWithBias(movie[KEYWORDS_COL], keywords, n, 1, movieScores)

            moviePointsCosine[key] = float(sm.cosine_similarity(movieScoresRef, movieScores))
        list5 = sorted(moviePointsCosine, key=lambda x: moviePointsCosine[x], reverse=True)
        return list5[:5]

    def recommendMovies2(self, movieId):
        genres = self.movie_metadata[movieId]['genres']
        keywords = self.movie_metadata[movieId]['keywords']

        movieScoresRef = list()
        Recommender.addScoreToList(genres, 2, movieScoresRef)
        Recommender.addScoreToList(keywords, 10, movieScoresRef)

        moviePointsJaccard = dict()

        for key, movie in self.movie_metadata.items():
            if key == movieId:
                continue
            movieScores = list()
            Recommender.matchWithBias(movie[GENRES_COL], genres, 2, 0, movieScores)
            Recommender.matchWithBias(movie[KEYWORDS_COL], keywords, 15, 5, movieScores)

            moviePointsJaccard[key] = float(sm.jaccard_similarity(movieScoresRef, movieScores))
        list5 = sorted(moviePointsJaccard, key=lambda x: moviePointsJaccard[x], reverse=True)
        return list5[:5]


if __name__ == "__main__":
    rec = Recommender()
    # knn = knn.KNN()

    print(rec.recommendMovies(2))

    print(rec.recommendMovies1(112852))
    print(rec.recommendMovies2(112852))
