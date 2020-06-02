import pandas as pd
import json
from recommendation import similarity_measures as sm
from math import inf

MOVIE_ID = 'movieId'


class Recommender:
    df_movies = pd.DataFrame()

    def __init__(self):
        self.df_movies = pd.read_csv("../resources/movies.csv", encoding="Latin1")
        self.movie_metadata = dict()
        for index, row in self.df_movies.iterrows():
            try:
                with open('../resources/' + str(row[MOVIE_ID]) + '.json', encoding="UTF-8") as json_file:
                    data = json.load(json_file)
                    directors = set()
                    languages = set()
                    actors = set()
                    genres = set()
                    if 'imdb' in data:
                        imdb = data['imdb']
                        for director in imdb['directors']:
                            directors.add(director)
                        languages.add(imdb['originalLanguage'])
                        actor_str = imdb['actors']
                        actor_str = str(actor_str).replace("['Stars: ", "")
                        actor_str = str(actor_str).replace(" | See full cast and crew »']", "")
                        for actor in str(actor_str).split(", "):
                            actors.add(actor)
                        for genre in imdb['genres']:
                            genres.add(genre)
                    if 'movielens' in data:
                        movielens = data['movielens']
                        for director in movielens['directors']:
                            directors.add(director)
                        for language in movielens['languages']:
                            languages.add(language)
                        for actor in movielens['actors']:
                            actors.add(actor)
                        for genre in movielens['genres']:
                            genres.add(genre)
                    # print(directors, languages, actors, genres)
                    self.movie_metadata[row[MOVIE_ID]] = {'directors': directors, 'languages': languages,
                                                          'actors': actors, 'genres': genres}
            except FileNotFoundError:
                print('no metadata for movie ' + str(row[MOVIE_ID]))

    def recommendMovies(self, movieId, n=15):
        genres = self.movie_metadata[movieId]['genres']
        languages = self.movie_metadata[movieId]['languages']
        actors = self.movie_metadata[movieId]['actors']
        directors = self.movie_metadata[movieId]['directors']
        movieScoresRef = list()
        movieScore = 0
        for genre in genres:
            movieScore = movieScore + n
        movieScoresRef.append(movieScore)
        movieScore = 0
        for language in languages:
            movieScore = movieScore + n
        movieScoresRef.append(movieScore)
        movieScore = 0
        for actor in actors:
            movieScore = movieScore + n
        movieScoresRef.append(movieScore)
        movieScore = 0
        for director in directors:
            movieScore = movieScore + n
        movieScoresRef.append(movieScore)

        moviePointsManhattan = dict()
        moviePointsEuclidean = dict()
        moviePointsChebyshev = dict()
        moviePointsCosine = dict()
        moviePointsJaccard = dict()

        for key, movie in self.movie_metadata.items():
            if key == movieId:
                continue
            movieScores = list()
            movieScore = 0
            for genre in movie['genres']:
                if genre in genres:
                    movieScore = movieScore + n
                else:
                    movieScore = movieScore - 1
            movieScores.append(movieScore)
            movieScore = 0
            for language in movie['languages']:
                if language in languages:
                    movieScore = movieScore + n
                else:
                    movieScore = movieScore - 1
            movieScores.append(movieScore)
            movieScore = 0
            for actor in movie['actors']:
                if actor in actors:
                    movieScore = movieScore + n
                else:
                    movieScore = movieScore - 1
            movieScores.append(movieScore)
            movieScore = 0
            for director in movie['directors']:
                if director in directors:
                    movieScore = movieScore + n
                else:
                    movieScore = movieScore - 1
            movieScores.append(movieScore)
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


if __name__ == "__main__":
    rec = Recommender()
    for val in rec.movie_metadata.items():
        print(val)
    print(rec.recommendMovies(112852))
