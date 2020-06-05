from django import template
from django.shortcuts import render
from recommendation.algorithm_interface import algorithm_interface
from recommendation.data_management_interface import mapper

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
        selectionQuery = request.POST['submit']
        # Again needs to be mapped to the actual movie object as only the string is provided
        selection = mapper.map_string_to_movie(selectionQuery)
        # Results of different algorithms
        # TODO: change to the actual algorithm classes
        alg1 = algorithm_interface.generate_recommendation(selection)
        alg2 = algorithm_interface.generate_recommendation(selection)
        alg3 = algorithm_interface.generate_recommendation(selection)
        alg4 = algorithm_interface.generate_recommendation(selection)
        alg5 = algorithm_interface.generate_recommendation(selection)
        return render(request, "recommendations.html", {"selection":selection, "alg1":alg1, "alg2":alg2, "alg3":alg3, "alg4":alg4, "alg5":alg5})

def matchStrings(searchQuery):
    # Create a list of movie titles that should be compared to the search query
    all_movies = mapper.get_all_titles()

    # Current placeholder
    # all_movies = ["Titanic", "Finding Nemo", "Pirates of the caribbean", "Another", "Cats", "Batman", "The Lion King", "King Arthur", "King for a day", "King Julien"]

    # Calculate the ratios between the initial query and the list
    ratios = process.extract(searchQuery, all_movies)
    # Returns the 5 elements with the highest accuracy
    matches = {}
    for movie in ratios:
        mapper.map_string_to_movie(movie[0])
    return matches