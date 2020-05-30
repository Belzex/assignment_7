from django import template
from django.shortcuts import render

# Fuzzy string matching
from fuzzywuzzy import process

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
        selection = request.POST['submit']
        # Again needs to be mapped to the actual movie object as only the string is provided

        # Results of different algorithms
        alg1 = {1: 'Movie 1', 2: 'Movie 2', 3: 'Movie 3', 4: 'Movie 4', 5: 'Movie 5'}
        alg2 = {1: 'Movie 1', 2: 'Movie 2', 3: 'Movie 3', 4: 'Movie 4', 5: 'Movie 5'}
        alg3 = {1: 'Movie 1', 2: 'Movie 2', 3: 'Movie 3', 4: 'Movie 4', 5: 'Movie 5'}
        alg4 = {1: 'Movie 1', 2: 'Movie 2', 3: 'Movie 3', 4: 'Movie 4', 5: 'Movie 5'}
        alg5 = {1: 'Movie 1', 2: 'Movie 2', 3: 'Movie 3', 4: 'Movie 4', 5: 'Movie 5'}
        return render(request, "recommendations.html", {"selection":selection, "alg1":alg1, "alg2":alg2, "alg3":alg3, "alg4":alg4, "alg5":alg5})

def matchStrings(searchQuery):
    # Create a list of movie titles that should be compared to the search query
    # Only strings

    # Current placeholder
    options = ["Titanic", "Finding Nemo", "Pirates of the caribbean", "Another", "Cats", "Batman", "The Lion King", "King Arthur", "King for a day", "King Julien"]
    # Calculate the ratios between the initial query and the list
    ratios = process.extract(searchQuery, options)
    # Returns the 5 elements with the highest accuracy
    matches = {}
    for movie in ratios:
        # for item in allMovies
        # As only strings were provided previously - Check back for actual movie object
        # if item.name == movie[0]:
        matches[movie[0]] = movie[0]
    return matches