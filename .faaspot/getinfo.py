import os
import json
import urlparse

from box import Box
from tmdbv3api import TMDb, Movie
from slackclient import SlackClient
from utils import _get_movie_info, _build_response

def getinfo(event, context):
    """Return the info about a given movie."""
    print ("event: {}".format(json.dumps(event)))
    query_params = event.get("query", {})
    tmdb_api_key = context.get_doc('tmdb_api_key')
    info = _get_movie_info(tmdb_api_key, query_params.get('movie'))
    return _build_response(info)