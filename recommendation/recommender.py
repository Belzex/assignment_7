import pandas as pd
import json
from recommendation import similarity_measures as sm

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
                    keywords = set()
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
                    if 'tmdb' in data:
                        tmdb = data['tmdb']
                        for actor in tmdb['credits']['cast']:
                            actors.add(actor['name'])
                        for crew in tmdb['credits']['crew']:
                            if crew['job'] == 'Director':
                                directors.add(crew['name'])
                        for language in tmdb['spoken_languages']:
                            languages.add(language['name'])
                        for genre in tmdb['genres']:
                            genres.add(genre['name'])
                        for keyword in tmdb['keywords']:
                            keywords.add(keyword['name'])
                    self.movie_metadata[row[MOVIE_ID]] = {'directors': directors, 'languages': languages,
                                                          'actors': actors, 'genres': genres, 'keywords': keywords}
            except FileNotFoundError:
                print('no metadata for movie ' + str(row[MOVIE_ID]))

    def recommendMovies(self, movieId, n=15):
        genres = self.movie_metadata[movieId]['genres']
        languages = self.movie_metadata[movieId]['languages']
        actors = self.movie_metadata[movieId]['actors']
        directors = self.movie_metadata[movieId]['directors']
        keywords = self.movie_metadata[movieId]['keywords']
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
        movieScore = 0
        for keyword in keywords:
            movieScore = movieScore + n
        movieScoresRef.append(movieScore)

        moviePointsCosine = dict()

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
            movieScore = 0
            for keyword in movie['keywords']:
                if keyword in keywords:
                    movieScore = movieScore + n
                else:
                    movieScore = movieScore - 1
            movieScores.append(movieScore)
            moviePointsCosine[key] = float(sm.cosine_similarity(movieScoresRef, movieScores))
        list5 = sorted(moviePointsCosine, key=lambda x: moviePointsCosine[x], reverse=True)
        return list5[:5]

    def recommendMovies1(self, movieId):
        genres = self.movie_metadata[movieId]['genres']
        keywords = self.movie_metadata[movieId]['keywords']
        movieScoresRef = list()
        movieScore = 0
        for genre in genres:
            movieScore = movieScore + 2
        movieScoresRef.append(movieScore)
        movieScore = 0
        for keyword in keywords:
            movieScore = movieScore + 10
        movieScoresRef.append(movieScore)


        moviePointsJaccard = dict()

        for key, movie in self.movie_metadata.items():
            if key == movieId:
                continue
            movieScores = list()
            movieScore = 0
            for genre in movie['genres']:
                if genre in genres:
                    movieScore = movieScore + 2
                else:
                    movieScore = movieScore - 0
            movieScores.append(movieScore)
            movieScore = 0
            for keyword in movie['keywords']:
                if keyword in keywords:
                    movieScore = movieScore + 15
                else:
                    movieScore = movieScore - 5
            movieScores.append(movieScore)
            moviePointsJaccard[key] = float(sm.jaccard_similarity(movieScoresRef, movieScores))
        list5 = sorted(moviePointsJaccard, key=lambda x: moviePointsJaccard[x], reverse=True)
        return list5[:5]


if __name__ == "__main__":
    rec = Recommender()
    for val in rec.movie_metadata.items():
        print(val)
    print(rec.recommendMovies(112852))
    print(rec.recommendMovies1(112852))
