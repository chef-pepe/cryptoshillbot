import json
import logging
import os
import time

import tweepy


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

with open('bags.json', 'r') as f:
    FIRM_TO_BAGS = json.load(f)


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
        logger.error('error building api')
        raise e

    logger.info('built api')
    return api


def desc_to_bags(desc):
    # TODO: are there other examples? may want to just test this for a bunch of VCs
    tags = [w.lower().rstrip('.,;-!?') for w in desc.split(' ')]

    return dict((tag, FIRM_TO_BAGS[tag]) for tag in tags if tag in FIRM_TO_BAGS)


SHILLBOT_REPO = "https://github.com/chef-pepe/cryptoshillbot"


def empty_bag_tweet(user_name):
    return f"couldn't find any bags being shilled by {user_name}. perhaps their firm isn't being tracked by {os.getenv('SHILLBOT_HANDLE')} yet.\n\nif known bags are missing, submit an issue here: {SHILLBOT_REPO}."


def formatted_bag_tweet(user_name, bags):
    # NOTE: basically the output for the tweet itself
    if len(bags) == 0:
        return empty_bag_tweet(user_name)

    else:
        tweet_lines = [
            f"possible bags held by @{user_name}:",
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

    return formatted_bag_tweet(tweet.user.screen_name, bags)


UNSHILL_TEXT = f"{os.getenv('SHILLBOT_HANDLE')} unshill"


def process_mention(api, mention):
    if mention.in_reply_to_status_id is not None and UNSHILL_TEXT in mention.text:
        bag_tweet = get_bag_tweet(api, mention.in_reply_to_status_id)
        logger.info(f"responding to tweet {mention.id} with {bag_tweet}")
        api.update_status(
            status=bag_tweet,
            in_reply_to_status_id=mention.id
        )


def process_new_mentions(api, since_id):
    # NOTE: should be thoughtful about not re-doing replies!
    new_since_id = since_id
    for mention in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(mention.id, new_since_id)

        process_mention(api, mention)

    return new_since_id


SLEEP_SECS = 30


def process_mention_loop(api, since_id):
    new_since_id = since_id
    while True:
        logger.info(f"processing mentions since tweet {new_since_id}")
        new_since_id = process_new_mentions(api, new_since_id)
        logger.info(f"latest processed mention {new_since_id}")

        logger.info(f"sleeping for {SLEEP_SECS} secs")
        time.sleep(SLEEP_SECS)


def get_latest_replied_id(api):
    latest_id = 1
    for tweet in tweepy.Cursor(api.user_timeline).items():
        if tweet.in_reply_to_status_id is not None:
            latest_id = max(latest_id, tweet.in_reply_to_status_id)

    return latest_id


if __name__ == '__main__':
    api = build_api()
    latest_replied_id = get_latest_replied_id(api)

    process_mention_loop(api, latest_replied_id)
