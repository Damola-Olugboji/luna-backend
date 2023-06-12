import emoji
from preprocessing.preprocess import BasePreprocessor

class TweetPreprocessor(BasePreprocessor):
    @staticmethod
    def preprocess_tweets(tweets):
        cleaned_tweets = []
        for tweet in tweets:
            try:
                full_text = tweet['full_text']
                full_text = TweetPreprocessor.remove_urls(full_text)
                full_text = TweetPreprocessor.lower_case(full_text)
                full_text = TweetPreprocessor.strip_whitespace(full_text)
                parsed_text = TweetPreprocessor.handle_emojis(full_text)
                
                tweet["parsedText"] = parsed_text
                cleaned_tweets.append(tweet)
                
            except Exception as e:
                print(e)
                
            
        return cleaned_tweets
    
    @staticmethod
    def handle_emojis(text):
        translated_text = emoji.demojize(text)
        return translated_text
