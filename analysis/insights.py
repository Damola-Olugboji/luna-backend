from pprint import pprint
import pandas as pd
import spacy
from collections import Counter
import mitie

from pprint import pprint
import pandas as pd
import spacy
from collections import Counter
import mitie


def generate_tweet_insights(tweets):
    nlp = spacy.load("en_core_web_sm")

    df = pd.DataFrame(tweets)

    # Calculate sentiment score
    def classify_sentiment(sentimentScore):
        if sentimentScore > 0.05:
            return "Positive"
        elif sentimentScore < -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    labels_of_interest = {"PERSON", "ORG", "GPE", "EVENT", "FAC", "NORP"}

    ner_model = mitie.named_entity_extractor("/Users/damolaolugboji/Downloads/MITIE-models/english/ner_model.dat")

    def extract_entities(text):
        tokens = mitie.tokenize(text)
        entities = ner_model.extract_entities(tokens)
        
        ranges = [entity[0] for entity in entities]
        
        entity_list = []
        for range in ranges:
            
            entity_list.append(' '.join(text.split()[range.start:range.stop]))
 
        return entity_list

    df["entities"] = df["parsedText"].apply(extract_entities)

    # Count each unique entity across all tweets
    entity_counts = Counter(entity for entities in df["entities"] for entity in entities)

    # Get the top 10 entities with the highest occurrence
    top_entities = dict(entity_counts.most_common(10))

    # Create a new column indicating whether the sentiment is positive, negative, or neutral
    df["sentiment_class"] = df["sentimentScore"].apply(classify_sentiment)

    sentiment_breakdown = df["sentiment_class"].value_counts()

    top_positive = df.nlargest(10, "sentimentScore").round({"sentimentScore": 3})

    top_negative = df.nsmallest(10, "sentimentScore").round({"sentimentScore": 3})

    recent_avg_sentiment = df["sentimentScore"].mean()

    # Combine all insights into a dictionary
    insights = {
        "Average Sentiment": round(recent_avg_sentiment, 3),
        "Sentiment Breakdown": sentiment_breakdown.to_dict(),
        "Most Positive Tweets": top_positive.to_dict(orient="records"),
        "Most Negative Tweets": top_negative.to_dict(orient="records"),
        "Entity Counts": top_entities,
    }
    
    def sanitize_field_paths(data):
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(key, str) and key.strip():  # Check if key is a non-empty string
                sanitized_data[key] = sanitize_field_paths(value) if isinstance(value, dict) else value
        return sanitized_data

    insights = sanitize_field_paths(insights)

    return insights


def generate_article_insights(articles):
    nlp = spacy.load("en_core_web_sm")
    df = pd.DataFrame(articles)

    df["publishedAt"] = pd.to_datetime(df["publishedAt"])

    # Calculate sentiment score

    # Define a function to classify sentiment
    def classify_sentiment(sentimentScore):
        if sentimentScore > 0.05:
            return "Positive"
        elif sentimentScore < -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    labels_of_interest = {"PERSON", "ORG", "GPE", "EVENT", "FAC", "NORP"}

    ner_model = mitie.named_entity_extractor("/Users/damolaolugboji/Downloads/MITIE-models/english/ner_model.dat")

    def extract_entities(text):
        tokens = mitie.tokenize(text)
        entities = ner_model.extract_entities(tokens)
        
        ranges = [entity[0] for entity in entities]
        
        entity_list = []
        for range in ranges:
            
            entity_list.append(' '.join(text.split()[range.start:range.stop]))
 
        return entity_list

    df["entities"] = df["parsedText"].apply(extract_entities)

    # Count each unique entity across all articles
    entity_counts = Counter(entity for entities in df["entities"] for entity in entities)

# Get the top 10 entities with the highest occurrence
    top_entities = dict(entity_counts.most_common(10))
    # pprint(entity_counts)

    # Create a new column indicating whether the sentiment is positive, negative, or neutral
    df["sentiment_class"] = df["sentimentScore"].apply(classify_sentiment)

    avg_sentiment_by_source = (
        df.groupby("sourceName")["sentimentScore"].mean().round(3)
    )
    avg_subjectivity_by_source = df.groupby("sourceName")["subjectivity"].mean().round(3)  # Added

    sentiment_breakdown = df["sentiment_class"].value_counts()

    top_positive = df.nlargest(10, "sentimentScore").round({"sentimentScore": 3})

    top_negative = df.nsmallest(10, "sentimentScore").round({"sentimentScore": 3})

    top_recent = df.sort_values(by="publishedAt", ascending=False).head(10)
    source_count = df["sourceName"].value_counts()

    articles_by_date = df["publishedAt"].dt.date.value_counts().sort_index()

    avg_sentiment_by_date = (
        df.groupby(df["publishedAt"].dt.date)["sentimentScore"].mean().round(3)
    )

    rolling_sentiment_7d = (
        df.set_index("publishedAt")["sentimentScore"].rolling(7).mean().round(3)
    )


    # rolling_sentiment_14d = df.set_index("publishedAt")["sentimentScore"].rolling(14).mean().round(3)

    # weights = df.sort_values(by="publishedAt", ascending=False).head(7).groupby("sourceName")["sentimentScore"].count()

    # weighted_sentiments = df.sort_values(by="publishedAt", ascending=False).head(7).groupby("sourceName")["sentimentScore"].mean().round(3)

    recent_avg_sentiment = df["sentimentScore"].mean()

    # Combine all insights into a dictionary
    insights = {
        "Average Sentiment": round(recent_avg_sentiment, 3),
        "Average Sentiment by Source": avg_sentiment_by_source.to_dict(),
        "Average Subjectivity by Source": avg_subjectivity_by_source.to_dict(),  # Added
        "Sentiment Breakdown": sentiment_breakdown.to_dict(),
        "Most Positive Articles": top_positive.to_dict(orient="records"),
        "Most Negative Articles": top_negative.to_dict(orient="records"),
        "Most Recent Articles": top_recent.to_dict(orient="records"),
        "Distribution of Articles by Source": source_count.to_dict(),
        "Distribution of Articles by Date": {
            k.strftime("%Y-%m-%d"): v for k, v in articles_by_date.to_dict().items()
        },
        "Average Sentiment Score by Date": {
            k.strftime("%Y-%m-%d"): round(v, 3)
            for k, v in avg_sentiment_by_date.to_dict().items()
        },
        "7-Day Rolling Sentiment": {
            k.strftime("%Y-%m-%d"): v
            for k, v in rolling_sentiment_7d.dropna().to_dict().items()
        },
        "Entity Counts": top_entities,  # Added this line

        # "14-Day Rolling Sentiment": {
        #     k.strftime("%Y-%m-%d"): v
        #     for k, v in rolling_sentiment_14d.dropna
        # }
    }

    return insights

def aggregate_sentiment(article_insights, tweet_insights, article_weight=0.5, tweet_weight=0.5):
    """
    This function takes the average sentiment from article_insights and tweet_insights,
    and returns a dictionary containing the weighted average sentiment score.
    
    Args:
        article_insights (dict): The output from the generate_article_insights function.
        tweet_insights (dict): The output from the generate_tweet_insights function.
        article_weight (float): The weight to assign to the article sentiment.
        tweet_weight (float): The weight to assign to the tweet sentiment.

    Returns:
        dict: A dictionary containing the weighted average sentiment score.
    """
    # Ensure the weights sum up to 1.0
    assert article_weight + tweet_weight == 1.0, "The weights should sum up to 1.0"

    article_sentiment = article_insights["Average Sentiment"]
    tweet_sentiment = tweet_insights["Average Sentiment"]

    # Calculate the weighted average sentiment
    weighted_average_sentiment = article_sentiment * article_weight + tweet_sentiment * tweet_weight
    
    insights = {"weighted Average Sentiment": round(weighted_average_sentiment, 3)}
    
    return insights

