from concurrent.futures import ThreadPoolExecutor
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
import text2emotion as te

class SentimentAnalyzer:
    def __init__(self) -> None:
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english",
        )
        self.emotion_pipeline = pipeline(
            "text-classification", model="cardiffnlp/twitter-roberta-base-emotion"
        )
        self.analyzer = SentimentIntensityAnalyzer()

    # def add_sentiment(self, data):
    #     parsed_data = []
    #     for item in data:
    #         text = item["parsedText"]
    #         sentiment = self.get_text_sentiment(text)
    #         item['sentimentScore'] = sentiment['sentimentScore']
    #         item['subjectivity'] = sentiment['subjectivity']
    #         item['emotions'] = sentiment['emotions']
    #         item['emotion2'] = sentiment['emotion2']
    #         parsed_data.append(item)
    #     return parsed_data
    
    def add_sentiment_to_item(self, item):
        try:
            text = item["parsedText"]
            sentiment = self.get_text_sentiment(text)
            item['sentimentScore'] = sentiment['sentimentScore']
            item['subjectivity'] = sentiment['subjectivity']
            item['emotions'] = sentiment['emotions']
            item['emotion2'] = sentiment['emotion2']
            return item
        except Exception as e:
            print(f"Error with get_text_sentiment: {e}")
            print(f"Skipping text: {item['parsedText']}")
            return None  # Return None to indicate that this item was skipped
        
    def add_sentiment(self, data):
        with ThreadPoolExecutor() as executor:
            parsed_data = list(filter(None, executor.map(self.add_sentiment_to_item, data)))  # Filter out None values
        return parsed_data


    # def process_item(self, item):
    #     text = item["parsedText"]
    #     sentiment = self.get_text_sentiment(text)
    #     item['sentimentScore'] = sentiment['sentimentScore']
    #     item['subjectivity'] = sentiment['subjectivity']
    #     item['emotions'] = sentiment['emotions']
    #     item['emotion2'] = sentiment['emotion2']
    #     return item

    def get_text_sentiment(self, text):
        text_blob = TextBlob(text)
        textblob_sentiment_score = text_blob.sentiment.polarity
        subjectivity = text_blob.sentiment.subjectivity

        # For distilbert sentiment score
        try:
            sentiment_result = self.sentiment_pipeline(text)[0]
            distilbert_sentiment_score = (
                sentiment_result["score"]
                if sentiment_result["label"].lower() == "positive"
                else -sentiment_result["score"]
            )
        except Exception:
            distilbert_sentiment_score = textblob_sentiment_score

        # For vader sentiment score
        try:
            vader_result = self.analyzer.polarity_scores(text)
            vader_sentiment_score = vader_result["compound"]
        except Exception:
            vader_sentiment_score = textblob_sentiment_score

        combined_sentiment_score = (
            distilbert_sentiment_score + vader_sentiment_score + textblob_sentiment_score
        ) / 3

        # For text2emotion result
        try:
            emotion_result = self.get_emotion(text)
        except Exception:
            emotion_result = {"Unknown": 1.0}  # or some other default value

        # For deep learning emotion result
        try:
            emotion2 = self.get_emotion_deep_learning(text)
        except Exception:
            emotion2 = "Unknown"  # or some other default value

        return {
            "sentimentScore": round(combined_sentiment_score, 3),
            "subjectivity": round(subjectivity, 3),
            "emotions": emotion_result,
            "emotion2": emotion2,
        }


    def get_emotion(self, text):
        emotion_dict = te.get_emotion(text)
        emotion_dict = {k: v for k, v in emotion_dict.items() if v > 0}
        sorted_emotions = sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        top_3_emotions = dict(sorted_emotions)
        return top_3_emotions

    def get_emotion_deep_learning(self, text):
        result = self.emotion_pipeline(text)
        return result[0]["label"]
