from sklearn.metrics.pairwise import linear_kernel
import pandas as pd

#reading the movies dataset
movie_list = pd.read_csv("movies.csv",encoding="Latin1")

genre_list = ""
for index,row in movie_list.iterrows():
        genre_list += row.genres + "|"
#split the string into a list of values
genre_list_split = genre_list.split('|')
#de-duplicate values
new_list = list(set(genre_list_split))
#remove the value that is blank
new_list.remove('')
#Enriching the movies dataset by adding the various genres columns.
movies_with_genres = movie_list.copy()

for genre in new_list :
    movies_with_genres[genre] = movies_with_genres.apply(lambda _:int(genre in _.genres), axis = 1)


#Getting the movies list with only genres like Musical and other such columns
movie_content_df_temp = movies_with_genres.copy()
movie_content_df_temp.set_index('movieId')
movie_content_df = movie_content_df_temp.drop(columns = ['movieId','title','genres'])
movie_content_df = movie_content_df.values
print(movie_content_df)

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(movie_content_df,movie_content_df)
#create a series of the movie id and title
indicies = pd.Series(movie_content_df_temp.index, movie_content_df_temp['title'])

print("data loaded")

#Gets the top 10 similar movies based on the content
def get_similar_movies_based_on_content(input_movie_title) :
    movie_index =indicies[input_movie_title]
    sim_scores = list(enumerate(cosine_sim[movie_index]))
    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[0:5]

    movie_sim_scores = [i[1] for i in sim_scores]
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    similar_movies = pd.DataFrame(movie_content_df_temp[['title','genres']].iloc[movie_indices])
    #similar_movies['score'] = movie_sim_scores
    return similar_movies

if __name__ == '__main__':
    input_movie = 'Exorcist The (1973)'
    recommended_movies_by_genre = get_similar_movies_based_on_content(input_movie)
    print(recommended_movies_by_genre)
