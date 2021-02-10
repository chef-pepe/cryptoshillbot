import os

import tweepy

FIRM_TO_BAGS = {
    '@paradigm': {
        'uniswap',
        'optimism',
        'argent',
        'starkware',
        'cosmos',
        'compound',
        'opyn'
    },
    '@multicoincap': {
        'algorand',
        'arweave',
        'dfinity',
        'dune analytics',
        'dfinity',
        'near',
        'nervos',
        'skale',
        'solana',
        'the graph'
    },
    '@dragonfly_cap': {
        '1inch',
        'celo',
        'cosmos',
        'compound',
        'dydx',
        'maker',
        'opyn',
        'uma'
    },
    '@variantfund': {
        'uniswap',
        'reflexer',
        'cozy finance',
        'goldfinch'
    },
    '@polychain': {
        '0x',
        'aleo',
        'ava labs',
        'celo',
        'compound',
        'dydx',
        'dfinity',
        'maker',
        'cosmos'
    }
}


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


def desc_to_bags(desc):
    # TODO: are there other examples?
    tags = [w.lower().rstrip('.,;-!?') for w in desc.split(' ')]

    return dict((tag, FIRM_TO_BAGS[tag]) for tag in tags if tag in FIRM_TO_BAGS)


def formatted_bag_tweet(user, bags):
    # NOTE: basically the output for the tweet itself
    if len(bags) == 0:
        return f"couldn't find any bags being shilled by {user.screen_name}. perhaps their firm isn't being tracked by @shillbot yet"

    else:
        # TODO: format this output nicely
        ...


def get_bags(api, tweet_id):
    tweet = api.get_status(tweet_id)

    bags = desc_to_bags(tweet.user.description)
    # TODO: format bag text

    return bags


UNSHILL_TEXT = f"{os.getenv('SHILLBOT_HANDLE')} unshill"


def get_mentions(api, since_id=1):
    # NOTE: should be thoughtful about not re-doing replies!
    mentions = []
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        # TODO: if tweet.text == UNSHILL_TEXT: get_shill(api, int(tweet.in_reply_to_status_id_str)), etc.
        mentions.append(tweet)
    return mentions


if __name__ == '__main__':
    api = build_api()
