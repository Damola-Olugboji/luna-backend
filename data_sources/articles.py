from config import news_api_org_key
import requests
import logging
'''
Still need to handle error in fetch_from_news_org
'''

class ArticleFetcher:
    
    @staticmethod
    def fetch_from_news_org(keyword, pageSize=20, language="en"):
        url = "https://newsapi.org/v2/everything"
        query = f"{keyword}"

        params = {
            "q": query,
            "language": language,
            "apiKey": news_api_org_key,
            "pageSize": pageSize,
            # "sortBy": self.sortBy,
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                articles = response.json()["articles"]
                extracted_articles = [
                    {
                        "author": article["author"],
                        "url": article["url"],
                        "urlToImage": article["urlToImage"],
                        "description": article["description"],
                        "publishedAt": article["publishedAt"],
                        "sourceName": article["source"]["name"],
                        "title": article["title"],
                    }
                    for article in articles
                ]
                return extracted_articles
            else:
                error_message = f"Error {response.status_code}: {response.text}"
                logging.error(error_message)
                return None
        except requests.exceptions.RequestException as e:
            error_message = f"RequestException occurred: {e}"
            logging.error(error_message)
            return None
        except Exception as e:
            error_message = f"An error occurred: {e}"
            logging.error(error_message)
            return None
        
        

        
        
    