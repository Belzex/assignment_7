import os

import pandas as pd
from assignment_7.settings import MOVIELENS_ROOT
from django.shortcuts import render
from recommendation.algorithm_interface import algorithm_interface
from recommendation.data_management_interface import mapper
from recommendation import recommender

# Fuzzy string matching
from fuzzywuzzy import process
from recommendation import similarity_measures

def home(request):
    if request.method == 'POST':
        print("Searching")
        # Extract the search query from page
        data = request.POST.copy()
        searchQuery = data.get('movieTextField')
        print(searchQuery)
        results = matchStrings(searchQuery)
        return render(request, "index.html", {"results":results})

    # No search query yet entered
    print("Starting")
    return render(request, "index.html", {})

def recommendation(request):
    if request.method == 'POST':
        # The movie title is the value of the selected submit button in the form
        selection_query = request.POST['submit']
        print(selection_query)
        # Again needs to be mapped to the actual movie object as only the string is provided
        selection = map_string_to_movie(selection_query)
        # ID for different algorithms to work
        selection_id = selection.iloc[0]['movieId']
        # Title to show the user as the selected movie
        selection_title = selection.iloc[0]['title']
        # Results of different algorithms
        rec = recommender.Recommender()
        movieList1=rec.recommendMovies1(selection_id)
        movieList2=rec.recommendMovies2(selection_id)
        alg1 = {1: movieList1[0], 2: movieList1[1], 3:movieList1[2], 4:movieList1[3], 5:movieList1[4]}
        alg2 = {1: movieList2[0], 2: movieList2[1], 3:movieList2[2], 4:movieList2[3], 5:movieList2[4]}
        # TODO: change to the actual algorithm classes
        alg3 = {1: 'Movie 1', 2: 'Movie 2', 3:'Movie 3', 4:'Movie 4', 5:'Movie 5'}
        alg4 = {1: 'Movie 1', 2: 'Movie 2', 3:'Movie 3', 4:'Movie 4', 5:'Movie 5'}
        alg5 = {1: 'Movie 1', 2: 'Movie 2', 3:'Movie 3', 4:'Movie 4', 5:'Movie 5'}
        return render(request, "recommendations.html", {"selection_title":selection_title, "alg1":alg1, "alg2":alg2, "alg3":alg3, "alg4":alg4, "alg5":alg5})

def matchStrings(searchQuery):
    '''
    Matches a string provided by the user to the existing movie database to find the best fitting movie
    :param searchQuery: The value the user is searching for as a String
    :return: A list of five elements with the highest accuracy in terms of string matching
    '''
    # Create a list of movie titles that should be compared to the search query
    all_movies = get_all_titles()
    # Calculate the ratios between the initial query and the list
    ratios = process.extract(searchQuery, all_movies)
    # Returns the 5 elements with the highest accuracy
    return ratios

def map_string_to_movie(selectionQuery):
    '''
    It is necessary to match a string back to its original movie object so the id can be used for further provision of information
    :param selectionQuery: Matches the string of an existing movie back to the id
    :return: A movie object with the ID and title of the movie
    '''

    # Split the provided string that was used for the matching
    # It contains the score which is not needed anymore at this point
    split_movie_title = selectionQuery.split('\'')
    # Extract the actual title
    movie_title = split_movie_title[1]

    MOVIE_ID: str = 'movieId'
    TITLE: str = 'title'
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    print(PATH)
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})

    # Map the title back to the original movie to use its id
    movie_object = df_movies.loc[df_movies[TITLE] == movie_title]
    return movie_object

def get_all_titles():

    '''
    For the fuzzy string match a list of all titles needs to be provided for it to work.
    :return: A list of all titles
    '''

    # Currently needs to be implemented here as no global class was created (which is useable)

    MOVIE_ID: str = 'movieId'
    TITLE: str = 'title'
    PATH = os.path.join(MOVIELENS_ROOT, 'movies.csv')
    print(PATH)
    df_movies: pd.DataFrame = pd.read_csv(PATH, encoding="UTF-8",
                                          usecols=[MOVIE_ID, TITLE],
                                          dtype={MOVIE_ID: 'int32', TITLE: 'str'})
    # A list for all movie titles is created
    movie_titles = []
    # Iterating over all movie titles and storing them in a new list
    df_movies_titles = df_movies["title"]
    for title in df_movies_titles:
        movie_titles.append(title)
    return movie_titles