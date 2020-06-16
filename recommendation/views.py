import os

import pandas as pd

from assignment_7.settings import MOVIELENS_ROOT
from django.shortcuts import render
from recommendation import recommender
from recommendation.movie_recommendation_itemRating import movie_recommendation_itemRating
from recommendation.movie_recommendation_by_genre import movie_recommendation_by_genre
from recommendation.movie_recommendation_by_tags import movie_recommendation_by_tags
import recommendation.movie_poster as mp
from recommendation.decorators import timer

import concurrent.futures

# Fuzzy string matching
from fuzzywuzzy import process
from recommendation import similarity_measures

MOVIE_ID: str = 'movieId'
TITLE: str = 'title'


@timer
def home(request):
    if request.method == 'POST':
        print("Searching")
        # Extract the search query from page
        data = request.POST.copy()
        # Query saved in Textfield
        searchQuery = data.get('movieTextField')
        print(searchQuery)
        # Match the searchquery and return the result
        results = matchStrings(searchQuery)

        temp_dict = dict(results)

        for key in temp_dict.keys():
            temp_dict[key] = mp.get_image_url(key)

        return render(request, "index.html", {"results": temp_dict})

    # No search query yet entered
    print("Starting")
    return render(request, "index.html", {})


def error(request):
    return render(request, "index.html", {})


@timer
def recommendation(request):
    if request.method == 'POST':
        # The movie title is the value of the selected submit button in the form
        selection_query = request.POST['submit']
        # Again needs to be mapped to the actual movie object as only the string is provided
        selection = map_string_to_movie(selection_query)
        # ID for different algorithms to work
        selection_id = selection.iloc[0]['movieId']
        # Title to show the user as the selected movie
        selection_title = selection.iloc[0]['title']

        print('selection id {}, selection title {}'.format(selection_id, selection_title))
        # Results of different algorithms
        rec = recommender.Recommender()

        movies_metadata: list = rec.metadataRecommender(selection_id)
        movies_keywords: list = rec.metadataRecommenderKeywords(selection_id)

        rec_obj = movie_recommendation_itemRating()
        movies_item_rating = rec_obj.get_similar_movies_based_on_itemRating(rec_obj, selection_title)

        obj_rec = movie_recommendation_by_genre()
        movies_genres = obj_rec.get_similar_movies_based_on_genre(selection_title)

        obj = movie_recommendation_by_tags()
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

            print(alg_list)
            return render(request, "recommendations.html",
                          {"selection_title": selection_tuple, "alg1": alg1, "alg2": alg2, "alg3": alg3, "alg4": alg4,
                           "alg5": alg5})
        except Exception as excError:
            return render(request, "error.html", {"error": excError})


@timer
def _get_movie_recommendations(selection_id: list, selection_title: list, movie_list_refs: list, recommender: int):
    print(f"recommender: {recommender}")
    if recommender == 0:
        rec_obj = movie_recommendation_itemRating()
        movie_list_refs[recommender] = rec_obj.get_similar_movies_based_on_itemRating(rec_obj, selection_title)
    elif recommender == 1:
        movie_list_refs[recommender] = movie_recommendation_by_genre().get_similar_movies_based_on_genre(
            selection_title)
    elif recommender == 2:
        obj = movie_recommendation_by_tags()
        movie_list_refs[recommender] = obj.get_similar_movies_based_on_tags(selection_title)


def _get_views_dict(movie_collection: list, movie_dict: dict) -> dict:
    if type(movie_collection) is list:
        _get_movie_dict(movie_collection, movie_dict)
    elif type(movie_collection) is dict:
        _df_to_movie_dict(movie_collection, movie_dict)
    return movie_dict


def _df_to_movie_dict(movie_df, movie_dict: dict) -> dict:
    temp_list: list = [movie_df[TITLE][idx] for idx in movie_df[TITLE]]
    for movie in temp_list:
        movie_dict[movie] = mp.get_image_url(movie)
    return movie_dict


def _get_movie_dict(movie_list: list, movie_dict: dict) -> dict:
    for movie in movie_list:
        title: str = get_title(movie)
        movie_dict[title] = mp.get_image_url(title)
    return movie_dict


def matchStrings(searchQuery):
    """
    Matches a string provided by the user to the existing movie database to find the best fitting movie
    :param searchQuery: The value the user is searching for as a String
    :return: A list of five elements with the highest accuracy in terms of string matching
    """
    # Create a list of movie titles that should be compared to the search query
    all_movies = get_all_titles()
    # Calculate the ratios between the initial query and the list
    ratios = process.extract(searchQuery, all_movies)
    # Returns the 5 elements with the highest accuracy
    return ratios


def map_string_to_movie(selectionQuery):
    """
    It is necessary to match a string back to its original movie object so the id can be used for further provision of information
    :param selectionQuery: Matches the string of an existing movie back to the id
    :return: A movie object with the ID and title of the movie
    """

    # Split the provided string that was used for the matching
    # It contains the score which is not needed anymore at this point
    # split_movie_title = selectionQuery.split('\'')
    # Extract the actual title
    # movie_title = split_movie_title[1]
    movie_title = selectionQuery
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})

    # Map the title back to the original movie to use its id
    movie_object = df_movies.loc[df_movies[TITLE] == movie_title]
    print(movie_object)
    return movie_object


def get_all_titles():
    """
    For the fuzzy string match a list of all titles needs to be provided for it to work.
    :return: A list of all titles
    """
    df_movies = get_movie_df()
    # A list for all movie titles is created
    movie_titles = []
    # Iterating over all movie titles and storing them in a new list
    df_movies_titles = df_movies["title"]
    for title in df_movies_titles:
        movie_titles.append(title)
    return movie_titles


def get_title(movieId: int):
    """
    Get the title from the movieId attribute.
    :param: the id of the movie
    :return: the title of the movie
    """
    df_movies = get_movie_df()
    return df_movies.loc[movieId]['title']


def get_movie_df():
    """
    Read file and create a dataframe containing movieId and the movie title
    :return: The dataframe containing movieId and title
    """
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})
    df_movies.set_index(MOVIE_ID, inplace=True)
    return df_movies
