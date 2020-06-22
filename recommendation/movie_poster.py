import requests
import re
import random
import unittest

from recommendation.logger_config import logging

from recommendation.decorators import timer

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
        logging.error(f'[{get_image_url.__name__}] - movie_title in parameter is not of type str')
        return None

    logging.debug(f'[{get_image_url.__name__}] - start function with movie title: {movie_title}')

    image_url: str = _title_to_image_url(movie_title=movie_title, comma_check=True)
    json_response = _get_json_response(image_url)

    # comma corrected movie_title did receive a response
    if json_response is not None:
        logging.debug(f'[{get_image_url.__name__}] - json response received with comma correction')
        return json_response
    # try without comma correction
    else:
        logging.debug(f'[{get_image_url.__name__}] - json response received without comma correction')
        image_url = _title_to_image_url(movie_title=movie_title, comma_check=False)
        return _get_json_response(image_url)


def _get_json_response(image_url: str) -> str:
    """
    Transforms the image_url in parameter to a json response
    @param image_url: the image url to be transformed
    @return: the json response of the given url (Note: can be None)
    """
    logging.debug(f'[{_get_json_response.__name__}] - start of function')
    response = requests.get(image_url)
    json_response = response.json()
    # poster url is in the json_response
    if POSTER in json_response:
        return json_response[POSTER]
    else:
        return None


def _title_to_image_url(movie_title: str, comma_check: bool = False) -> str:
    """
    Transforms the given movie title into an image url.
    Removes year and if comma_check is True, also transforms the movie title
    @param movie_title: movie title to be transformed into an image url
    @param comma_check: if True, the comma gets removed and the str part behind the comma appended to the beginning
                        of the movie title
    @return: an image url, where the poster of the movie can be found
    """
    logging.debug(f'[{_title_to_image_url.__name__}] - start of function')
    temp_string: str = _remove_year_from_title(movie_title)
    if comma_check:
        temp_string = _comma_check(temp_string)
    temp_string = temp_string.replace(BLANK, PLUS)
    image_url: str = random.choice(API_KEY_PREFIX) + temp_string
    logging.debug(f'[{_title_to_image_url.__name__}] - image url: {image_url}')
    return image_url


def _remove_year_from_title(movie_title: str) -> str:
    """
    Removes the release year of the movie title given as parameter
    @param movie_title: the movie title, which will be modified
    @return: the movie title without the release year
    """
    logging.debug(f'[{_remove_year_from_title.__name__}] - start of function')
    year_regex = re.compile(YEAR_PATTERN)
    return_string: str = year_regex.subn('', movie_title)[0]
    logging.debug(f'[{_remove_year_from_title.__name__}] - return string: {return_string}')
    return return_string


def _comma_check(movie_title: str) -> str:
    """
    Checks if a comma separates the movie title, usually, if that is the case,
    the part after the comma must be appended to the beginning of the movie_title str
    @param movie_title: will be checked for a comma in the string
    @return: the comma corrected movie title if a comma is found in the string
    """
    logging.debug(f'[{_comma_check.__name__}] - start of function')
    if COMMA in movie_title:
        logging.debug(f'[{_comma_check.__name__}] - comma found in {movie_title}')
        temp_list = movie_title.split(COMMA)
        # remove all blanks before and after a word
        for index, value in enumerate(temp_list):
            temp_list[index] = value.strip()
        temp_str = temp_list.pop()
        temp_list.insert(0, temp_str)
        concatenated_str: str = BLANK.join(temp_list)
        return concatenated_str
    else:
        logging.debug(f'[{_comma_check.__name__}] - comma not found in {movie_title}')
        return movie_title


class Tests(unittest.TestCase):
    TOY_STORY_TITLE: str = 'Toy Story (1995)'
    TOY_STORY_2_TITLE: str = 'Toy Story 2 (1999)'
    LION_KING_TITLE: str = 'Lion King, The'
    MONSTERS_INC_TITLE: str = 'Monsters, Inc. (2001)'

    def test_title_to_image_url(self):
        # http://omdbapi.com/?apikey=f32e08d6&t=Toy+Story
        actual_url: str = _title_to_image_url(self.TOY_STORY_TITLE)
        # prefix of the image url needed for the GET request to OMDb
        self.assertTrue('http://omdbapi.com/?apikey=' in actual_url)
        # t=... denotes the movie title
        # blanks in movie title must be replaced by plus characters
        self.assertTrue('t=Toy+Story' in actual_url)

    def test_comma_check(self):
        # should correct the string to the expected string
        self.assertEqual(_comma_check(self.LION_KING_TITLE), 'The Lion King')

        # A movie title without a comma should not be modified by this function
        movie_title_without_comma: str = 'Some Test Movie Title without a comma'
        self.assertEqual(_comma_check(movie_title_without_comma),
                         movie_title_without_comma)

    def test_remove_year_from_title(self):
        # if the title contains the release year, the release year should be removed
        self.assertEqual(_remove_year_from_title(self.TOY_STORY_TITLE), 'Toy Story')
        self.assertEqual(_remove_year_from_title(self.TOY_STORY_2_TITLE), 'Toy Story 2')
        self.assertEqual(_remove_year_from_title(self.MONSTERS_INC_TITLE), 'Monsters, Inc.')
        # if no release year is in the string, the movie title should stay the same
        self.assertEqual(_remove_year_from_title(self.LION_KING_TITLE), self.LION_KING_TITLE)


if __name__ == '__main__':
    unittest.main()
