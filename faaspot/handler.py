# https://pypi.python.org/pypi/tmdbv3api

# Implement your function here.
# The function will get the event as the first parameter with query/body properties:
# The function should return a Dictionary
import os
import json

from tmdbv3api import TMDb, Movie


def getinfo(event, context):
    query_params = event.get("query", {})
    body_params = event.get("body", {})

    tmdb_api_key = os.environ.get('tmdb_api_key')
    info = _get_movie_info(tmdb_api_key, query_params.get('movie'))

    return {
        'statusCode': 200,
        'body': json.dumps(info),
        'headers': {"Content-Type": "application/json"}
    }


def getrating(event, context):
    query_params = event.get("query", {})
    body_params = event.get("body", {})

    tmdb_api_key = os.environ.get('tmdb_api_key')
    info = _get_movie_info(tmdb_api_key, query_params.get('movie'),
                           filter_fields=['title', 'vote_average'])

    return {
        'statusCode': 200,
        'body': json.dumps(info),
        'headers': {"Content-Type": "application/json"}
    }


def _get_movie_info(api_key, movie_name, filter_fields=None):
    def round_num(num):
        return '{0:.2f}'.format(num)

    if not movie_name:
        return {'error': 'missing movie name'}

    tmdb = TMDb()
    tmdb.api_key = api_key
    movie = Movie()
    search = movie.search(movie_name)
    if len(search) == 0:
        return {'error': 'missing movie: {0}'.format(movie_name)}

    if not filter_fields:
        filter_fields = ['id', 'title', 'vote_average', 'popularity', 'imdb_id',
                         'release_date', 'genres']
    results = []
    sorted_movies = sorted(search, key=lambda x: x.release_date, reverse=True)
    for item in sorted_movies:
        info = movie.details(item.id)
        genres = [x['name'] for x in info.genres]
        info_dict = {'id': item.id,
                     'title': info.title,
                     'vote_average': round_num(info.vote_average),
                     'popularity': round_num(info.popularity),
                     'imdb_id': info.imdb_id,
                     'release_date': info.release_date,
                     'genres': genres}
        info_to_add = dict()
        for field in filter_fields:
            info_to_add[field] = info_dict[field]
        results.append(info_to_add)

    return results


# print main({'query': {'movie': 'ferdinand'}}, {}).get('body')
