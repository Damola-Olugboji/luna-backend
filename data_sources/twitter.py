import tweepy
from apify_client import ApifyClient


class TwitterFetcher:

    @staticmethod
    def fetch_tweets_by_keyword(keyword, pageSize = 25):
        bearer_token = "AAAAAAAAAAAAAAAAAAAAALCeRwEAAAAA0nyKJaaJb7nUaAVbTbhA%2FyR%2FzSk%3DVVExeaxyDHDbwTDnHFC7Bq2DKRmEZTW3v9balXHsWYviHNc06R"

        client = tweepy.Client(bearer_token)

        query = keyword
        response = client.search_recent_tweets(query, max_results=pageSize,)
        tweet_objects = response.data
        tweets = [{'id': tweet.id, 'full_text': tweet.text} for tweet in tweet_objects]
        attributes = [attr for attr in dir(tweet_objects[0]) if not attr.startswith('__')]

        # for attr in attributes:
        #     print(f"{attr}: {getattr(tweet_objects[0], attr)}")
        return tweets
    
    @staticmethod
    def fetch_user_tweets(handle, tweetsDesired = 10, ):
        payload = {
            "addUserInfo": True,
            "handle": [handle],
            "tweetsDesired": tweetsDesired,
            "mode": "replies",
            "addTweetViewCount": True,
            "skipRetweets": False,
            "startUrls": [],
            "searchMode": "live",
            "profilesDesired": 10,
            "useCheerio": True,
            "relativeToDate": "",
            "relativeFromDate": "",
            "useAdvancedSearch": False,
            "proxyConfig": {"useApifyProxy": True},
            "extendOutputFunction": "async ({ data, item, page, request, customData, Apify }) => {\n  return item;\n}",
            "extendScraperFunction": "async ({ page, request, addSearch, addProfile, _, addThread, addEvent, customData, Apify, signal, label }) => {\n \n}",
            "customData": {},
            "handlePageTimeoutSecs": 500,
            "maxRequestRetries": 6,
            "maxIdleTimeoutSecs": 60,
            "debugLog": False,
        }
        apify_client = ApifyClient("apify_api_8auUHEz0ShssyMJDraUM9lNl4YDKYW2wQoVo")

        actor_call = apify_client.actor("quacker~twitter-scraper").call(
            run_input=payload, memory_mbytes=4096
        )

        tweets = (
            apify_client.dataset(actor_call["defaultDatasetId"]).list_items()
        ).items
        
        user_info = []
        extracted_tweets = []
        
        user = tweets[0].get('user', {})
        user_info = {
            'screen_name': user.get('screen_name'),
            'followers_count': user.get('followers_count'),
            'name': user.get('name'),
            'profile_image_url_https': user.get('profile_image_url_https')
        }

        for tweet in tweets:
            # Extract tweet info
            extracted_tweets.append({
                'full_text': tweet.get('full_text'),
                'url': tweet.get('url'),
                'view_count': tweet.get('view_count'),
                'quote_count': tweet.get('quote_count'),
                'retweet_count': tweet.get('retweet_count'),
                'favorite_count': tweet.get('favorite_count'),
                'reply_count': tweet.get('reply_count'),
                'created_at': tweet.get('created_at')
            })
        
        return user_info, extracted_tweets

