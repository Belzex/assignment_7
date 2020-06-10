import requests
import re
import random

COMMA: str = ','
BLANK: str = ' '
SPECIAL_CASES: list = ['Monsters, Inc.']

API_PREFIX: list = ['http://omdbapi.com/?apikey=56197bb3&t=', 'http://omdbapi.com/?apikey=f32e08d6&t=']


def get_image_url(movie_title: str) -> str:
    """
    :param: movie_title the movie title for which an image url will be retrieved from omdb
    """
    if type(movie_title) is not str:
        return None

    year_reg = re.compile(' \(....\)')
    movie_title = year_reg.subn("", movie_title)[0]
    movie_title = _comma_check(movie_title)
    movie_title = movie_title.replace(" ", "+")

    image_url: str = random.choice(API_PREFIX) + movie_title
    response = requests.get(image_url)
    json_response = response.json()

    if 'Poster' in json_response:
        return json_response['Poster']


def _comma_check(movie_title: str) -> str:
    """
    Checks if a comma separates the movie title, usually, if that is the case,
    the part after the comma must be appended to the beginning of the movie_title str
    :param movie_title: will be checked for a comma in the string
    """
    if movie_title in SPECIAL_CASES:
        return movie_title
    if COMMA in movie_title:
        temp_list = movie_title.split(COMMA)
        for index, value in enumerate(temp_list):
            temp_list[index] = value.strip()
        temp_str = temp_list.pop()
        temp_list.insert(0, temp_str)
        concatenated_str: str = BLANK.join(temp_list)
        return concatenated_str
    else:
        return movie_title


# if __name__ == '__main__':
#     print(get_image_url('New Hope'))
#     print(get_image_url('New Hope, A'))
#     print(get_image_url('Lion King, The'))
