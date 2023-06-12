from xml.dom.minidom import Entity
from analysis.insights import aggregate_sentiment, generate_article_insights, generate_tweet_insights
from data_sources.articles import ArticleFetcher
from data_sources.entities import EntityIntake
from data_sources.twitter import TwitterFetcher
from database.cloud_database_manager import CloudDatabaseManger
from preprocessing.preprocess_article import ArticlePreprocessor
from preprocessing.preprocess_tweets import TweetPreprocessor
from sentiment_analysis.sentiment_analyzer import SentimentAnalyzer
import pprint
from concurrent.futures import ThreadPoolExecutor
import time
import os
'''
Generate config files for each of the data collection classes
'''

debug = bool(int(os.getenv('DEBUG', '0')))


def upload_entites():
    db = CloudDatabaseManger()
    entityIntake = EntityIntake()
    
    for entity in entityIntake.load_entities():
        db.store_data_firestore(entity['name'], "entities", {"entity": entity['full_name'], "data": entity})
    

def process_articles(entity):
    name = entity['name']
    db = CloudDatabaseManger()
    analyzer = SentimentAnalyzer()
    
    pageSize = 10 if debug else 100
    articles = ArticleFetcher.fetch_from_news_org(keyword=name, pageSize=pageSize)
    articles = ArticlePreprocessor.preprocess_articles(articles)
    articles = analyzer.add_sentiment(articles)
    
    if not debug:
        db.store_data_firestore(name, "articles", { "entity": name, "articles": articles})
        
    return articles

def process_tweets(entity):
    name = entity['name']
    handle = entity['twitter_handle']
    db = CloudDatabaseManger()
    analyzer = SentimentAnalyzer()
    
    pageSize = 25 if debug else 100

    # user_stats, user_tweets = TwitterFetcher.fetch_user_tweets(handle)
    relevant_tweets = TwitterFetcher.fetch_tweets_by_keyword(name, pageSize)
    # user_tweets = TweetPreprocessor.preprocess_tweets(user_tweets)
    relevant_tweets = TweetPreprocessor.preprocess_tweets(relevant_tweets)
    relevant_tweets = analyzer.add_sentiment(relevant_tweets)
    
    db.store_data_firestore(name, "tweets", { "entity": name, "relevantTweets": relevant_tweets})
    
    return relevant_tweets

def main():
    entityIntake = EntityIntake()
    entities = entityIntake.load_entities()
    
    start_time = time.time()  # Start measuring the execution time
    
    for entity in entities:
        articles = process_articles(entity)
        relevant_tweets = process_tweets(entity)
        
        # pprint.pprint(articles)
        # pprint.pprint(relevant_tweets)
        
        article_insights = generate_article_insights(articles)
        tweet_insights = generate_tweet_insights(relevant_tweets)
        
        aggregate_insights = aggregate_sentiment(article_insights, tweet_insights)
        
        # pprint.pprint(article_insights)
        # pprint.pprint(tweet_insights)
        pprint.pprint(aggregate_insights)

        
        db = CloudDatabaseManger()
        db.store_data_firestore(entity['name'], 'insights', {'articleInsights': article_insights, 'tweetInsights': tweet_insights, 'aggregateInsights': aggregate_insights})
        
        

    end_time = time.time()  # Stop measuring the execution time
    execution_time = end_time - start_time
    
    print(f"Execution time: {execution_time} seconds")

        


if __name__ == "__main__":
    main()
    # upload_entites()