import os
import json
import urlparse

from box import Box
from tmdbv3api import TMDb, Movie
from slackclient import SlackClient
from utils import _get_movie_info, _build_response


def latest(event, context):    
    tmdb_api_key = context.get_doc('tmdb_api_key')
    info = _get_movie_info(tmdb_api_key, now_playing=True,
                           filter_fields=['title', 'vote_average'])
    return _build_response(info)