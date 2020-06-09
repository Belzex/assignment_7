import requests
import re

URL_PREFIX = 'http://omdbapi.com/?apikey=56197bb3&t='


# if the first one expires
# URL_PREFIX = 'http://omdbapi.com/?apikey=f32e08d6&t='

def get_image_url(movie_title: str) -> str:
    year_reg = re.compile(' \(....\)')
    movie_title = year_reg.subn("", movie_title)[0]
    movie_title = movie_title.replace(" ", "+")

    image_url: str = URL_PREFIX + movie_title
    response = requests.get(image_url)
    json_response = response.json()

    if 'Poster' in json_response:
        return json_response['Poster']

# if __name__ == '__main__':
#     get_image_url('Toy Story 2 (2000)')
