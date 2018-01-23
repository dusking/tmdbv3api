# https://pypi.python.org/pypi/tmdbv3api

# Implement your function here.
# The function will get the event as the first parameter with query/body properties:
# The function should return a Dictionary
import os
import json
from tmdbv3api import TMDb, Movie


def latest(event, context):
    tmdb_api_key = event.get('tmdb_api_key', '')
    info = _get_movie_info(tmdb_api_key,
                           filter_fields=['title', 'vote_average'],
                           now_playing=True)
    info = {'result': info}
    return {
        'statusCode': 200,
        'body': json.dumps(info),
        'headers': {"Content-Type": "application/json"}
    }


def _get_movie_info(api_key, movie_name=None, filter_fields=None, now_playing=False):
    def round_num(num):
        return '{0:.2f}'.format(num)

    if not movie_name and not now_playing:
        print ('missing movie name')
        return {'error': 'missing movie name'}

    if movie_name:
        print ('retrieving info for: {0}'.format(movie_name))
    else:
        print ('retrieving info for movies that are now playing')
    tmdb = TMDb()
    tmdb.api_key = api_key
    movie = Movie()
    if now_playing:
        search = movie.now_playing()
    else:
        search = movie.search(movie_name)
        if len(search) == 0:
            return {'error': 'missing movie: {0}'.format(movie_name)}

    if not filter_fields:
        filter_fields = ['id', 'title', 'vote_average', 'popularity', 'imdb_id',
                         'release_date', 'genres']
    results = []
    sorted_movies = sorted(search, key=lambda x: x.release_date, reverse=True)
    for item in sorted_movies:
        if now_playing and movie_name and movie_name not in info.title:
            continue
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

