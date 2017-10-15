# tmdbv3api
Python wrapper for The Movie Database (TMDb) API.

To use this wrapper you will need to get an API key from TMDb.

Register an account:
https://www.themoviedb.org/account/signup

Check out the API documentation: 
https://docs.themoviedb.apiary.io

### Install

```
pip install tmdbv3api
```

### Examples

Get the list of popular movies on The Movie Database. This list refreshes every day.

```python

from tmdbv3api import TMDb, Movie, TV, Person, Discover
tmdb = TMDb(debug=False, lang="en")
tmdb.api_key = 'YOUR_API_KEY'

movie = Movie()
popular = movie.popular()

for p in popular:
    print p.id
    print p.title
    print p.overview
    print p.poster_path
            
```

Get the primary information about a movie.

```python
m = movie.get_movie(343611)
print m.title
print m.overview
print m.popularity
```

Search for movies by title.

```python
search = movie.search('Mad Max')

for res in search:
    print res.id
    print res.title
    print res.overview
    print res.poster_path
    print res.vote_average
```

Get the similar movies for a specific movie id.

```python
similar = movie.similar(777)

for result in similar:
    print result.title
    print result.overview
```

Search for TV shows by title.

```python
tv = TV()
show = tv.search_tv('Breaking Bad')

for result in show:
    print result.name
    print result.overview
```

Get the similar TV shows for a specific tv id.

```python
similar = tv.similar_shows(1396)

for show in similar:
    print show.name
    print show.overview
```

Get the general person information for a specific id.

```python
person = Person()
p = person.get_person(12)

print p.name
print p.biography
```

Discover movies by different types of data like average rating, number of votes, genres and certifications. 

```python

# What movies are in theatres?

discover = Discover()
movie = discover.discover_movies({
    'primary_release_date.gte': '2017-01-20',
    'primary_release_date.lte': '2017-01-25'
})

# What are the most popular movies?

movie = discover.discover_movies({
    'sort_by': 'popularity.desc'
})

# What are the most popular kids movies?

movie = discover.discover_movies({
    'certification_country': 'US',
    'certification.lte': 'G',
    'sort_by': 'popularity.desc'
})

```

Discover TV shows by different types of data like average rating, number of votes, genres, the network they aired on and air dates.

```python
# What are the most popular TV shows?

show = discover.discover_tv_shows({
    'sort_by': 'popularity.desc'
})

# What are the best dramas?

show = discover.discover_tv_shows({
    'with_genres': 18,
    'sort_by': 'vote_average.desc',
    'vote_count.gte': 10
})

```

### Supported Methods

#### Movies
- **/movie/latest** 
- **/movie/now_playing**
- **/movie/top_rated**
- **/movie/upcoming**
- **/movie/id**
- **/movie/id/similar**
- **/movie/id/recommendations**
- **/movie/id/videos**
- **/movie/id/reviews**
- **/movie/id/lists**


#### TV

- **/tv/id**
- **/tv/latest**
- **/tv/id/similar** 
- **/tv/top_rated**
- **/tv/popular**

#### People

- **/person/id**

#### Search

- **/search/movie**
- **/search/tv**
- **/search/person**

#### Discover

- **/discover/movie**
- **/discover/tv**
