from preprocessing.preprocess import BasePreprocessor

class ArticlePreprocessor(BasePreprocessor):
    @staticmethod
    def preprocess_articles(articles):
        cleaned_articles = []
        for article in articles:
            full_text = f'{article["title"]} {article["description"]}'
            try:
                parsed_text = BasePreprocessor.preprocess_text(full_text)
                article["parsedText"] = parsed_text
                cleaned_articles.append(article)
            except Exception as e:
                '''
                Check out wtf is going on here and why some aren't working with the preprocess methods
                '''
                # article["parsedText"] = article['title']
                # cleaned_articles.append(article)
                continue
        
        return cleaned_articles
