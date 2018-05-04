import os
import json
import urlparse
import requests
import threading

import jsonschema
from functools import wraps
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


def unpad(data):
    return data[0:-ord(data[-1])]


def decrypt(hex_data):
    key = 'WmFKzhC3YRmEU4dPY3hza8HUu7653Gg3'
    iv = 'ZS9ATh5Wz4jUN895'
    data = ''.join(map(chr, bytearray.fromhex(hex_data)))
    aes = AES.new(key, AES.MODE_CBC, iv)
    data = unpad(aes.decrypt(data))
    return base64.b64decode(data)


def validate_token(token):
    user_data = ''
    if not token:
        return {'error': "missing user token"}
    try:
        user_data = decrypt(token.replace('Basic ', ''))
        print ("user_data: {0}".format(user_data))
    except ValueError:
        return {'error': '`{}` does not appear to be a valid token'.format(token)}
    return {'user_data': user_data}


def callPost(body):    
    print ('going to send `google-bigquery` request.. body: {}'.format(body))
    headers = {"Content-Type":"application/json", "Token":"Basic 62646018047677d2f204ffae7dac388bc4cb227d963b729d"}    
    send_message_url = 'https://us-central1-faaspotit.cloudfunctions.net/google-bigquery'
    requests.post(send_message_url, data=json.dumps(body), headers=headers)


def update_usage(user_id, user_ip_addr, function_id, function_name):
    body = {"user_id": user_id, 'source_ip': user_ip_addr, 'function_id': function_id, 'function_name': function_name}
    th = threading.Thread(target=callPost, args=[body])
    th.daemon = True
    th.start()

fix_text = {
    '{} is not valid under any of the given schemas':
    'missing input'
}

def endpoint(schema=None):
    def endpoint_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            event, context = args
            print ("event: {0}".format(event))
            print ("context: {0}".format(context))
            body = event.get("body")
            body = body or '{}'  # for some reason, event.get("body", '{}') doesn't work
            
            try:
                body = json.loads(body)
            except ValueError:
                body = urlparse.parse_qs(body)  
                body = {k: v[0] for k, v in body.iteritems()}

            if schema:
                try:
                    validate(body, schema)
                except (ValidationError, SchemaError) as ex:
                    element = '{} - '.format(ex.path[0]) if len(ex.path) else ''
                    message = ex.message
                    err_message = '{}{}'.format(element, message).strip()                    
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': err_message}),
                        'headers': {"Content-Type": "application/json"}
                    }
                
            headers = event.get("headers", {})        
            token = headers.get('Token')    
            user_ip = headers.get('X-Forwarded-For')

            result = validate_token(token)
            err = result.get('error')
            if err:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': err}),
                    'headers': {"Content-Type": "application/json"}
                }
            user_data = result.get('user_data')
            user_id = user_data.split(':')[0]
            function_name = event.get('uri').split('/')[-1]
            function_id = context.get('functionId')
            update_usage(user_id, user_ip, function_id, function_name)
            
            try:
                response = json.dumps(func(body))    
            except Exception as ex:
                return {
                        'statusCode': 400,
                        'body': json.dumps({'error': str(ex)}),
                        'headers': {"Content-Type": "application/json",
                        }
                    }
            return {
                'statusCode': 200,
                'body': response,
                'headers': {"Content-Type": "application/json"}
            }
        return wrapper
    return endpoint_wrapper

