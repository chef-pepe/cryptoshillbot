import os

import tweepy


def build_api():
    consumer_key = os.getenv('SHILLBOT_CONSUMER_KEY')
    consumer_secret = os.getenv('SHILLBOT_CONSUMER_SECRET')
    access_token = os.getenv('SHILLBOT_ACCESS_TOKEN')
    access_token_secret = os.getenv('SHILLBOT_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        print('error building api')
        raise e

    print('built api')
    return api


if __name__ == '__main__':
    api = build_api()
