from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import numpy as np


class movie_recommendation_by_tags:
    #one time offline initialization
    def offline_initialization(self, moviesdata, tagsdata):
        #reading the movies dataset
        movie_list = pd.read_csv(moviesdata,encoding="Latin1")
        tag_list = pd.read_csv(tagsdata,encoding="Latin1")

        movie_tags_list = ""
        for index,row in tag_list.iterrows():
                movie_tags_list += row.tag + "|"
        #split the string into a list of values
        tags_list_split = movie_tags_list.split('|')
        #de-duplicate values
        new_list = list(set(tags_list_split))
        #remove the value that is blank
        new_list.remove('')

        df = pd.DataFrame(columns={'movieId','tags'})
        for row in movie_list.iterrows():
            movieid = row[1]['movieId']
            df_temp = tag_list.loc[tag_list['movieId']==movieid]
            tag_lst= ""
            for tag in df_temp.iterrows():
                tag_lst = tag_lst+ str(tag[1]['tag']) +'|'
            df= df.append({'movieId':movieid,'tags':tag_lst},ignore_index=True)

        combine_movie_tags = pd.merge(movie_list, df, on='movieId')
        #Enriching the movies dataset by adding the various genres columns.
        movies_with_tags = combine_movie_tags.copy()

        #selection of 5000 tag features to prepare data for model
        for tg in new_list[:500] :
            movies_with_tags[tg] = movies_with_tags.apply(lambda _:int(tg in _.tags), axis = 1)

        #Getting the movies list with only genres like Musical and other such columns
        movie_content_df_temp = movies_with_tags.copy()
        movie_content_df_temp.set_index('movieId')
        movie_content_df = movie_content_df_temp.drop(columns = ['movieId','title','genres','tags'])
        movie_content_df = movie_content_df.values
        print(movie_content_df)

        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(movie_content_df,movie_content_df)
        #write model for offline initialization
        np.savetxt('model.txt', cosine_sim)
        #write Movie contents for runtime recommendations
        movie_content_df_temp.to_csv ('movie_content.csv', index = True, header=True)


    def read_model_content_data(self):
        modeldata =np.loadtxt(fname = "model.txt")
        df = pd.read_csv('../resources/movie_content.csv', encoding="Latin1")
        return modeldata, df

    #Gets the top 10 similar movies based on the content
    def get_similar_movies_based_on_tags(self, input_movie_title) :
        cosine_sim, movie_content_df_temp =self.read_model_content_data()
        #create a series of the movie id and title
        indicies = pd.Series(movie_content_df_temp.index, movie_content_df_temp['title'])

        movie_index =indicies[input_movie_title]
        sim_scores = list(enumerate(cosine_sim[movie_index]))
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 5 most similar movies
        sim_scores = sim_scores[1:6]

        movie_sim_scores = [i[1] for i in sim_scores]
        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]
        similar_movies = pd.DataFrame(movie_content_df_temp[['title']].iloc[movie_indices])
        similar_movies =similar_movies.reset_index()
        #similar_movies['score'] = movie_sim_scores
        return similar_movies.to_dict()

# if __name__ == '__main__':
#
#
#     obj= movie_recommendation_by_tags()
#     #obj.offline_initialization('movies.csv','tags.csv')
#     input_movie = 'Up (2009)'
#     recommended_movies_by_genre = obj.get_similar_movies_based_on_tags(input_movie)
#     print(recommended_movies_by_genre)
