import os

import pandas as pd

from assignment_7.settings import MOVIELENS_ROOT
from django.shortcuts import render
from recommendation import recommender
from recommendation.movie_recommendation_itemRating import MovieRecommendationItemRating
from recommendation.movie_recommendation_by_genre import MovieRecommendationByGenre
from recommendation.movie_recommendation_by_tags import MovieRecommendationByTags
import recommendation.movie_poster as mp
from recommendation.decorators import timer

# logger to track the application process
from recommendation.logger_config import logging

# used to multi thread the image retrieval
import concurrent.futures

# Fuzzy string matching
from fuzzywuzzy import process

MOVIE_ID: str = 'movieId'
TITLE: str = 'title'


@timer
def home(request):
    if request.method == 'POST':
        logging.debug(f'[{home.__name__}] - start with POST request: {request}')
        # Extract the search query from page
        data = request.POST.copy()
        # Query saved in Textfield
        search_query = data.get('movieTextField')
        logging.debug(f'[{home.__name__}] - search query: {search_query}')
        # Match the search_query and return the result
        results = match_strings(search_query)

        temp_dict = dict(results)

        for key in temp_dict.keys():
            temp_dict[key] = mp.get_image_url(key)

        return render(request, "index.html", {"results": temp_dict})

    # No search query yet entered
    logging.debug('No search query entered at the moment')
    return render(request, "index.html", {})


def error(request):
    logging.error(f'An error occurred during the process with request: {request}')
    return render(request, "index.html", {})


@timer
def recommendation(request):
    if request.method == 'POST':
        logging.debug(f'[{recommendation.__name__}] - start function with request: {request}')
        # The movie title is the value of the selected submit button in the form
        selection_query = request.POST['submit']
        # Again needs to be mapped to the actual movie object as only the string is provided
        selection = map_string_to_movie(selection_query)
        # ID for different algorithms to work
        selection_id = selection.iloc[0][MOVIE_ID]
        # Title to show the user as the selected movie
        selection_title = selection.iloc[0][TITLE]

        print('selection id {}, selection title {}'.format(selection_id, selection_title))
        # Results of different algorithms
        rec = recommender.Recommender()

        movies_metadata: list = rec.metadata_recommender(selection_id)
        movies_keywords: list = rec.metadata_recommender_with_keywords(selection_id)

        rec_obj = MovieRecommendationItemRating()
        movies_item_rating = rec_obj.get_similar_movies_based_on_itemRating(rec_obj, selection_title)

        obj_rec = MovieRecommendationByGenre()
        movies_genres = obj_rec.get_similar_movies_based_on_genre(selection_title)

        obj = MovieRecommendationByTags()
        movies_tags = obj.get_similar_movies_based_on_tags(selection_title)

        selection_tuple: tuple = (selection_title, mp.get_image_url(selection_title))

        try:
            alg1: dict = dict()
            alg2: dict = dict()
            alg3: dict = dict()
            alg4: dict = dict()
            alg5: dict = dict()

            movieList = [movies_metadata, movies_keywords, movies_item_rating, movies_genres, movies_tags]
            alg_list = [alg1, alg2, alg3, alg4, alg5]

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(_get_views_dict, movieList, alg_list)

            return render(request, "recommendations.html",
                          {"selection_title": selection_tuple, "alg1": alg1, "alg2": alg2, "alg3": alg3, "alg4": alg4,
                           "alg5": alg5})
        except Exception as excError:
            logging.error(f'An error occurred during the recommendation process with error: {excError}')
            return render(request, "error.html", {"error": excError})


def match_strings(search_query):
    """
    Matches a string provided by the user to the existing movie database to find the best fitting movie
    @param search_query: The value the user is searching for as a String
    @return: A list of five elements with the highest accuracy in terms of string matching
    """
    # Create a list of movie titles that should be compared to the search query
    all_movies = get_all_titles()
    # Calculate the ratios between the initial query and the list
    ratios = process.extract(search_query, all_movies)
    # Returns the 5 elements with the highest accuracy
    return ratios


def map_string_to_movie(selection_query):
    """
    It is necessary to match a string back to its original movie object so the id can be used for further provision of information
    @param selection_query: Matches the string of an existing movie back to the id
    @return: A movie object with the ID and title of the movie
    """

    # Split the provided string that was used for the matching
    # It contains the score which is not needed anymore at this point
    # split_movie_title = selectionQuery.split('\'')
    # Extract the actual title
    # movie_title = split_movie_title[1]
    logging.debug(f'[{map_string_to_movie.__name__}] - start of function with selection query: {selection_query}')
    movie_title = selection_query
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})

    # Map the title back to the original movie to use its id
    movie_object = df_movies.loc[df_movies[TITLE] == movie_title]
    logging.debug(f'[{map_string_to_movie.__name__}] - Movie object: {movie_object}')

    return movie_object


def get_all_titles():
    """
    For the fuzzy string match a list of all titles needs to be provided for it to work.
    @return: A list of all titles
    """
    df_movies = get_movie_df()
    # A list for all movie titles is created
    movie_titles = []
    # Iterating over all movie titles and storing them in a new list
    df_movies_titles = df_movies[TITLE]
    for title in df_movies_titles:
        movie_titles.append(title)
    return movie_titles


def get_title(movieId: int):
    """
    Get the title from the movieId attribute.
    @param: the id of the movie
    @return: the title of the movie
    """
    df_movies = get_movie_df()
    return df_movies.loc[movieId][TITLE]


def get_movie_df():
    """
    Read file and create a dataframe containing movieId and the movie title
    @return: The dataframe containing movieId and title
    """
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})
    df_movies.set_index(MOVIE_ID, inplace=True)
    return df_movies


def _get_views_dict(movie_collection: list, movie_dict: dict) -> dict:
    logging.debug(
        f'[{_get_views_dict.__name__}] - start to transform movie collection to dictionary')
    if type(movie_collection) is list:
        _get_movie_dict(movie_collection, movie_dict)
    elif type(movie_collection) is dict:
        _df_to_movie_dict(movie_collection, movie_dict)
    return movie_dict


def _df_to_movie_dict(movie_df, movie_dict: dict) -> dict:
    """
    Safes the title of each entry of the given movie_df in the movie_dict as key
    @param movie_df: the src object
    @param movie_dict: the dst object, with key = movie_title of movie_df and image url of movie title as a value
    @return: a movie_dict with key=title, value=image_url
    """
    temp_list: list = [movie_df[TITLE][idx] for idx in movie_df[TITLE]]
    for movie in temp_list:
        movie_dict[movie] = mp.get_image_url(movie)
    return movie_dict


def _get_movie_dict(movie_list: list, movie_dict: dict) -> dict:
    """
    Reads all movies of the movie list and stores each title as the key of the movie_dict reference in the parameter.
    @param movie_list: contains all movie titles which will be used as keys of the dictionary
    @param movie_dict: dictionary, which uses the movie title as the key and the movie poster url as the value
    @return: the final movie_dict object
    """
    for movie in movie_list:
        title: str = get_title(movie)
        movie_dict[title] = mp.get_image_url(title)
    return movie_dict
