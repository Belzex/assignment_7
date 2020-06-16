import requests
import re
import random

COMMA: str = ','
BLANK: str = ' '
PLUS: str = '+'
POSTER: str = 'Poster'
YEAR_PATTERN: str = ' \(....\)';

API_KEY_PREFIX: list = ['http://omdbapi.com/?apikey=56197bb3&t=', 'http://omdbapi.com/?apikey=f32e08d6&t=']


def get_image_url(movie_title: str) -> str:
    """
    @param movie_title: the movie title for which an image url will be retrieved from OMDb
    @return: the image url, where the poster of the movie can be found. Note: Can be of type None.
    """
    if type(movie_title) is not str:
        return None

    image_url: str = _title_to_image_url(movie_title=movie_title, comma_check=True)
    json_response = _get_json_response(image_url)

    # comma corrected movie_title did receive a response
    if json_response is not None:
        return json_response
    # try without comma correction
    else:
        image_url = _title_to_image_url(movie_title=movie_title, comma_check=False)
        return _get_json_response(image_url)


def _get_json_response(image_url: str) -> str:
    """
    Transforms the image_url in parameter to a json response
    @param image_url: the image url to be transformed
    @return: the json response of the given url (Note: can be None)
    """
    response = requests.get(image_url)
    json_response = response.json()
    # poster url is in the json_response
    if POSTER in json_response:
        return json_response[POSTER]
    else:
        return None


def _title_to_image_url(movie_title: str, comma_check: bool) -> str:
    """
    Transforms the given movie title into an image url.
    Removes year and if comma_check is True, also transforms the movie title
    @param movie_title: movie title to be transformed into an image url
    @param comma_check: if True, the comma gets removed and the str part behind the comma appended to the beginning
                        of the movie title
    @return: an image url, where the poster of the movie can be found
    """
    year_regex = re.compile(YEAR_PATTERN)
    temp_string: str = year_regex.subn('', movie_title)[0]
    if comma_check:
        temp_string = _comma_check(temp_string)
    temp_string = temp_string.replace(BLANK, PLUS)
    image_url: str = random.choice(API_KEY_PREFIX) + temp_string
    return image_url


def _comma_check(movie_title: str) -> str:
    """
    Checks if a comma separates the movie title, usually, if that is the case,
    the part after the comma must be appended to the beginning of the movie_title str
    @param movie_title: will be checked for a comma in the string
    @return: the comma corrected movie title if a comma is found in the string
    """
    if COMMA in movie_title:
        temp_list = movie_title.split(COMMA)
        # remove all blanks before and after a word
        for index, value in enumerate(temp_list):
            temp_list[index] = value.strip()
        temp_str = temp_list.pop()
        temp_list.insert(0, temp_str)
        concatenated_str: str = BLANK.join(temp_list)
        return concatenated_str
    else:
        return movie_title


# if __name__ == '__main__':
#     print(get_image_url('Lion King, The'))
#     print(get_image_url('Monsters, Inc. (2001)'))
