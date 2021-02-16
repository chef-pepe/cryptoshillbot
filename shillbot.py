import os

import tweepy

FIRM_TO_BAGS = {
    '@paradigm': [
        'uniswap',
        'optimism',
        'argent',
        'starkware',
        'cosmos',
        'compound'
    ],
    '@multicoincap': [
        'algorand',
        'arweave',
        'dfinity',
        'near',
        'skale',
        'solana',
    ],
    '@dragonfly_cap': [
        '1inch',
        'celo',
        'cosmos',
        'compound',
        'dydx',
        'opyn',
        'uma'
    ],
    '@variantfund': [
        'uniswap',
        'reflexer',
        'cozy finance',
    ],
    '@polychain': [
        '0x',
        'ava labs',
        'celo',
        'compound',
        'dydx',
        'dfinity',
        'cosmos'
    ]
}

SHILLBOT_REPO = "https://github.com/chef-pepe/cryptoshillbot"


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


def empty_bag_tweet(user_name):
    return f"couldn't find any bags being shilled by {user_name}. perhaps their firm isn't being tracked by {os.getenv('SHILLBOT_HANDLE')} yet.\n\nif known bags are missing, submit an issue here: {SHILLBOT_REPO}."


def formatted_bag_tweet(user_name, bags):
    # NOTE: basically the output for the tweet itself
    if len(bags) == 0:
        return empty_bag_tweet(user_name)

    else:
        tweet_lines = [
            f"possible bags held by {user_name}:",
        ]
        for firm, bags in bags.items():
            tweet_lines += [
                f"\t{firm}:",
            ]
            tweet_lines += [f"\t- {bag}" for bag in bags]

        tweet_lines += [f"\nif these bags are wrong, submit an issue here: {SHILLBOT_REPO}."]

        return '\n'.join(tweet_lines)


def get_bag_tweet(api, tweet_id):
    tweet = api.get_status(tweet_id)

    bags = desc_to_bags(tweet.user.description)

    return formatted_bag_tweet(tweet.user, bags)


UNSHILL_TEXT = f"{os.getenv('SHILLBOT_HANDLE')} unshill"


def get_mentions(api, since_id=1):
    # NOTE: should be thoughtful about not re-doing replies!
    mentions = []
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        # TODO: if tweet.text == UNSHILL_TEXT: get_shill(api, int(tweet.in_reply_to_status_id_str)), etc.
        # also, only do it if tweet text should've changed! log here which ones we do as well
        mentions.append(tweet)
    return mentions


if __name__ == '__main__':
    api = build_api()
