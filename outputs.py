#!/usr/bin/env python

import gzip
import json
import os
from sets import *
import urlparse

import boto
import oauth2 as oauth
from random import choice
import requests
from tumblr import Api
from tumblpy import Tumblpy

import app_config


def generate_new_oauth_tokens():
    """
    Script to generate new OAuth tokens.
    Code from this gist: https://gist.github.com/4219558
    """
    consumer_key = 'Cxp2JzyA03QxmQixf7Fee0oIYaFtBTTHKzRA0AveHlh094bwDH'
    consumer_secret = os.environ['TUMBLR_APP_SECRET']

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "POST")
    if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    print

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    accepted = 'n'
    while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
            oauth_verifier = raw_input('What is the OAuth Verifier? ')

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above."
    print


def write_mr_president_test_posts():
    """
    Writes test posts to our test blog as defined by app_config.py
    """

    # This is how many posts will be written.
    TOTAL_NUMBER = 15

    def clean(string):
        """
        Formats a string all pretty.
        """
        return string.replace('-', ' ').replace("id ", "I'd ").replace("didnt", "didn't").replace('i ', 'I ')

    t = Tumblpy(
            app_key=app_config.TUMBLR_KEY,
            app_secret=os.environ['TUMBLR_APP_SECRET'],
            oauth_token=os.environ['TUMBLR_OAUTH_TOKEN'],
            oauth_token_secret=os.environ['TUMBLR_OAUTH_TOKEN_SECRET'])

    tags = ['ivotedforyou', 'idrathernotsayhowivoted', 'ididntvoteforyou', 'ididntvote']

    images = ['data/images/1.png', 'data/images/2.png', 'data/images/3.png', 'data/images/4.png']

    n = 0
    while n < TOTAL_NUMBER:
        tag = choice(tags)
        caption = u"""<p class='intro'>Dear Mr. President,</p>
        <p class='voted' data-vote-type='%s'>%s.</p>
        <p class='message'>This is a test post.</p>
        <p class='signature-name'>Signed,<br/>Test from Test, Test</p>""" % (
            tag,
            clean(tag),
        )

        filename = choice(images)

        with open(filename, 'rb') as f:
            tumblr_post = t.post('post', blog_url=app_config.TUMBLR_URL, params={
                'type': 'photo',
                'caption': caption,
                'tags': tag,
                'data': f
            })

        print n, tumblr_post['id']

        n += 1


def dump_tumblr_json():
    t = Tumblpy(
            app_key=app_config.TUMBLR_KEY,
            app_secret=os.environ['TUMBLR_APP_SECRET'],
            oauth_token=os.environ['TUMBLR_OAUTH_TOKEN'],
            oauth_token_secret=os.environ['TUMBLR_OAUTH_TOKEN_SECRET'])

    limit = 10
    pages = range(0, 20)

    for page in pages:
        offset = page * limit
        posts = t.get('posts', blog_url=app_config.TUMBLR_URL, params={'limit': limit, 'offset': offset})

        with open('data/backups/tumblr_prod_%s.json' % page, 'w') as f:
            f.write(json.dumps(posts))

##
## One-time use. Don't use this.
##

# def update_mr_president_posts():
#     """
#     Runs through the Dear Mr. President posts and updates the captions.
#     """
#     t = Tumblpy(
#             app_key=app_config.TUMBLR_KEY,
#             app_secret=os.environ['TUMBLR_APP_SECRET'],
#             oauth_token=os.environ['TUMBLR_OAUTH_TOKEN'],
#             oauth_token_secret=os.environ['TUMBLR_OAUTH_TOKEN_SECRET'])

#     unique_posts = set([])

#     new_text = u'<p class="footnote">What do <em>you</em> want President Obama to remember in his second term? Share your message at <a href="http://inauguration2013.tumblr.com/">NPR\'s Dear Mr. President</a>.</p>'

#     limit = 10
#     pages = range(0, 20)

#     for page in pages:
#         offset = page * limit
#         posts = t.get('posts', blog_url=app_config.TUMBLR_URL, params={'limit': limit, 'offset': offset})

#         for post in posts['posts']:
#             unique_posts.add(post['id'])

#     if len(unique_posts) > 0:
#         print 'There are %s posts to check!\n' % len(unique_posts)
#         for post in unique_posts:
#             p = t.get('posts', blog_url=app_config.TUMBLR_URL, params={'id': int(post)})

#             caption = p['posts'][0]['caption']
#             if u'<p class="footnote">' in caption:
#                 print '.'
#             else:
#                 caption += new_text
#                 u = t.post('post/edit', blog_url=app_config.TUMBLR_URL, params={'id': int(post), 'caption': caption})
#                 print u['id']
#     else:
#         print 'No posts ... something wrong!'


def write_mr_president_json():
    """
    Writes the JSON for Dear Mr. President to www.
    """

    #
    # First, handle stuff from the V1 API. This is fetching the posts by tag.
    #
    print "V1: Starting."
    TUMBLR_FILENAME = 'www/live-data/misterpresident.json'
    TUMBLR_MAX_POSTS = 10000
    MAX_PER_CATEGORY = 100
    api = Api(app_config.TUMBLR_BLOG_ID)
    print "V1: API call made."
    posts = list(api.read(max=TUMBLR_MAX_POSTS))

    print "V1: Fetched %s posts." % len(posts)
    print "V1: Starting to render."

    output = {
        'idrathernotsayhowivoted': [],
        'ivotedforyou': [],
        'ididntvoteforyou': [],
        'ididntvote': [],
        'mostpopular': []
    }

    for post in posts:
        simple_post = {
            'id': post['id'],
            'url': post['url'],
            'text': post['photo-caption'],
            'photo_url': post['photo-url-100'],
            'photo_url_250': post['photo-url-250'],
            'photo_url_500': post['photo-url-500'],
            'photo_url_1280': post['photo-url-1280'],
            'timestamp': post['unix-timestamp']
        }

        for tag in post['tags']:
            try:
                if len(output[tag]) <= MAX_PER_CATEGORY:
                    output[tag].append(simple_post)
            except KeyError:
                pass
    print "V1: Rendering finished."

    #
    # Now, fetch the most popular posts using the V2 API.
    #
    print "V2: Starting."
    # Set constants
    base_url = 'http://api.tumblr.com/v2/blog/inauguration2013.tumblr.com/posts/photo'
    key_param = '?api_key=Cxp2JzyA03QxmQixf7Fee0oIYaFtBTTHKzRA0AveHlh094bwDH'
    limit_param = '&limit=20'
    limit = 20
    new_limit = limit
    post_list = []

    # Figure out the total number of posts.
    r = requests.get(base_url + key_param)
    total_count = int(json.loads(r.content)['response']['total_posts'])
    print "V2: %s total posts available." % total_count

    # Do the pagination math.
    pages_count = (total_count / limit)
    pages_remainder = (total_count % limit)
    if pages_remainder > 0:
        pages_count += 1
    pages = range(0, pages_count)
    print "V2: %s pages required." % len(pages)

    # Start requesting pages.
    # Note: Maximum of 20 posts per page.
    print "V2: Requesting pages."
    for page in pages:

        # Update all of the pagination shenanigans.
        start_number = new_limit - limit
        end_number = new_limit
        if end_number > total_count:
            end_number = total_count
        new_limit = new_limit + limit
        page_param = '&offset=%s' % start_number
        page_url = base_url + key_param + limit_param + page_param

        # Actually fetch the page URL.
        r = requests.get(page_url)
        posts = json.loads(r.content)

        for post in posts['response']['posts']:
            try:
                note_count = post['note_count']
                post_list.append(post)
            except KeyError:
                pass

    # Sort the results first.
    print "V2: Finished requesting pages."
    print "V2: Sorting list."
    post_list = sorted(post_list, key=lambda post: post['note_count'], reverse=True)

    # Render the sorted list, but slice to just 24 objects per bb.
    print "V2: Rendering posts from sorted list."
    for post in post_list[0:24]:
        default_photo_url = post['photos'][0]['original_size']['url']
        simple_post = {
            'id': post['id'],
            'url': post['post_url'],
            'text': post['caption'],
            'timestamp': post['timestamp'],
            'note_count': post['note_count'],
            'photo_url': default_photo_url,
            'photo_url_250': default_photo_url,
            'photo_url_500': default_photo_url,
            'photo_url_1280': default_photo_url
        }

        # Handle the new photo assignment.
        for photo in post['photos'][0]['alt_sizes']:
            if int(photo['width']) == 100:
                simple_post['photo-url-100'] = photo['url']
            if int(photo['width']) == 250:
                simple_post['photo_url_250'] = photo['url']
            if int(photo['width']) == 500:
                simple_post['photo_url_500'] = photo['url']
            if int(photo['width']) == 1280:
                simple_post['photo_url_1280'] = photo['url']
        output['mostpopular'].append(simple_post)

    # Ensure the proper sort on our output list.
    print "V2: Ordering output."
    output['mostpopular'] = sorted(output['mostpopular'], key=lambda post: post['note_count'], reverse=True)

    # Write the JSON file.
    print "All: Producing JSON file at %s." % TUMBLR_FILENAME
    json_output = json.dumps(output)
    with open(TUMBLR_FILENAME, 'w') as f:
        f.write(json_output)
    print "All: JSON file written."

    if app_config.DEPLOYMENT_TARGET:
        with gzip.open(TUMBLR_FILENAME + '.gz', 'wb') as f:
            f.write(json_output)

        for bucket in app_config.S3_BUCKETS:
            conn = boto.connect_s3()
            bucket = conn.get_bucket(bucket)
            key = boto.s3.key.Key(bucket)
            key.key = '%s/live-data/misterpresident.json' % app_config.DEPLOYED_NAME
            key.set_contents_from_filename(
                TUMBLR_FILENAME + '.gz',
                policy='public-read',
                headers={
                    'Cache-Control': 'max-age=5 no-cache no-store must-revalidate',
                    'Content-Encoding': 'gzip'
                }
            )

        os.remove(TUMBLR_FILENAME + '.gz')
