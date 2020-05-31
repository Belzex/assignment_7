import pandas as pd
import numpy as np
import sklearn
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import linear_kernel

df_movies = pd.read_csv("movies.csv",encoding="Latin1")
df_ratings = pd.read_csv("ratings.csv", usecols=['userId', 'movieId', 'rating'])

#df_ratings = df_ratings[:2650000]
combine_movie_rating = pd.merge(df_ratings, df_movies, on='movieId')
combine_movie_rating = combine_movie_rating.dropna(axis = 0, subset = ['title'])
movie_ratingCount = (combine_movie_rating.
     groupby(by = ['title'])['rating'].
     count().
     reset_index().
     rename(columns = {'rating': 'totalRatingCount'})
     [['title', 'totalRatingCount']]
    )
rating_with_totalRatingCount = combine_movie_rating.merge(movie_ratingCount, left_on = 'title', right_on = 'title', how = 'left')
user_rating = rating_with_totalRatingCount.drop_duplicates(['userId','title'])
movie_user_rating_pivot = pd.pivot_table(user_rating, index = 'userId', columns = 'title', values = 'rating').fillna(0)
#movie_user_rating_pivot = user_rating.pivot(index = 'userId', columns = 'title', values = 'rating').fillna(0)
X = movie_user_rating_pivot.values.T

SVD = TruncatedSVD(n_components=12, random_state=17)
matrix = SVD.fit_transform(X)
corr = np.corrcoef(matrix)
movie_title = movie_user_rating_pivot.columns
movie_title_list = list(movie_title)

def get_similar_movies_based_on_content(movie_titile):
    movie_index = movie_title_list.index(movie_titile)
    sim_scores  = list(enumerate(corr[movie_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    movie_sim_scores = [i[1] for i in sim_scores]
    scores = [round(x, 2) for x in movie_sim_scores]
    similar_movies =pd.DataFrame()
    similar_movies['title'] = movie_title[movie_indices]
    similar_movies['score'] = scores
    temp_genre =pd.merge(similar_movies,df_movies, on=['title'], how='left')
    similar_movies['genre'] = temp_genre['genres']
    return  similar_movies

if __name__ == '__main__':
        input_movie = 'Exorcist The (1973)'
        movie_recommendations = get_similar_movies_based_on_content(input_movie)
        print(movie_recommendations)
