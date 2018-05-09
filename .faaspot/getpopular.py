import os

from tmdbv3api import TMDb, Movie
from wrapper import endpoint

schema = {
    'properties':  {
        'poster_size': {'type': 'integer'}
    }
}

@endpoint(schema)
def gepopular(args):
    # https://developers.themoviedb.org/3/getting-started/images
    tmdb_api_key = '17142b76281bf2b4b2d12ec1dc0b4eac'
    poster_size = args.get('poster_size', '500')
    tmdb = TMDb()
    tmdb.api_key = tmdb_api_key
    movie = Movie()
    popular_movies = []
    base = 'https://image.tmdb.org/t/p/w{}/'.format(poster_size)
    for m in movie.popular():
        popular_movies.append({
            'title': m.title, 
            'overview': m.overview,
            'popularity': m.popularity,
            'poster_path': os.path.join(base, m.poster_path.strip('/')),
            'release_date': m.release_date,
            'vote_average': m.vote_average})
    return popular_movies
