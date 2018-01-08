# https://pypi.python.org/pypi/tmdbv3api

# Implement your function here.
# The function will get the event as the first parameter with query/body properties:
# The function should return a Dictionary
import os
import json
import urlparse

from box import Box
from tmdbv3api import TMDb, Movie
from slackclient import SlackClient


def getinfo(event, context):
    query_params = event.get("query", {})
    info = _get_movie_info(os.environ.get('tmdb_api_key'),
                           query_params.get('movie'))
    return _build_response(info)


def getrating(event, context):
    query_params = event.get("query", {})
    info = _get_movie_info(os.environ.get('tmdb_api_key'),
                           query_params.get('movie'),
                           filter_fields=['title', 'vote_average'])
    return _build_response(info)


def latest(event, context):
    query_params = event.get("query", {})
    info = _get_now_playing(query_params.get('movie'))
    return _build_response(info)


def slackcommand(event, context):
    body = event.get("body", "{}")
    response = _handle_slack_challenge(body)
    if response:
        return response
    slack_event = urlparse.parse_qs(body)
    failure = _verify_slack_command(slack_event)
    if failure:
        return failure
    slack_event = Box(slack_event, default_box_attr=None, default_box=True)
    if slack_event.text[0] == 'help':
        return _build_slack_response('Supported command options: [now_playing]', visible_all=False)
    if slack_event.text[0] == 'now_playing':
        text = _format_slack_message(_get_now_playing())
        return _build_slack_response(text)
    return _build_slack_response('Supported command options: [now_playing]', visible_all=False)


def slackbot(event, context):
    body = event.get("body", "{}")
    body_params = json.loads(body)
    response = _handle_slack_challenge(body)
    if response:
        return response

    slack_token = os.environ.get('slack_api_token')
    if not slack_token:
        return _build_response({'error': 'missing slack token'})

    slack_event = body_params.get('event')
    if not slack_event:
        return _build_response({'error': 'missing slack event'})

    slack_event = Box(slack_event, default_box_attr=None, default_box=True)
    if slack_event.bot_id or not(slack_event.user and slack_event.type == "message"):
        return _build_response({'error': 'we handle only user messages'})

    if slack_event.text.startswith('imdb info for'):
        movie = slack_event.text[len('imdb info for'):].strip()
        tmdb_api_key = os.environ.get('tmdb_api_key')
        info = _get_movie_info(tmdb_api_key, movie,
                               filter_fields=['title', 'vote_average'])
        sc = SlackClient(slack_token)
        sc.api_call("chat.postMessage", channel=slack_event.channel, text=json.dumps(info))
    elif slack_event.text.startswith('imdb latest'):
        info = _get_now_playing()
        sc = SlackClient(slack_token)
        sc.api_call("chat.postMessage", channel=slack_event.channel, text=_format_slack_message(info))

    return _build_response({'got': slack_event.text})


def _handle_slack_challenge(body):
    body_params = json.loads(body)
    if 'challenge' in body_params:
        response = _handle_slack_verification(body_params)
        return _build_response(response)
    return None


def _verify_slack_command(slack_event):
    if not slack_event or 'command' not in slack_event:
        return _build_response({'error': 'not a slack command'})
    # _verify_request_from_slack()
    return None


def _verify_request_from_slack(body_params, slack_token):
    # Verify that the webhook request came from Slack.
    # The app token can be retrieved from the app page (https://api.slack.com/apps/)
    # Basic Information ==> App Credentials ==> Verification Token
    pass


def _get_now_playing(movie=None):
    tmdb_api_key = os.environ.get('tmdb_api_key')
    info = _get_movie_info(tmdb_api_key,
                           movie_name=movie,
                           filter_fields=['title', 'vote_average'],
                           now_playing=True)
    return info


def _build_slack_response(text, visible_all=True):
    response_type = 'in_channel' if visible_all else 'ephemeral'
    response = {
        "response_type": response_type,
        'text': text
    }
    return _build_response(response)


def _build_response(response, stringify=True):
    response = json.dumps(response) if stringify else response
    return {
        'statusCode': 200,
        'body': response,
        'headers': {"Content-Type": "application/json"}
    }


def _handle_slack_verification(body_params):
    token = body_params.get('token')
    challenge = body_params.get('challenge')
    response = {"challenge": challenge}
    return response


def _format_slack_message(results):
    text = ''
    for record in results:
        text += '*{0}* (rating: {1})\n'.format(record['title'], record['vote_average'])
    return text


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

