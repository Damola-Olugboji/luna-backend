import re
from spellchecker import SpellChecker

class BasePreprocessor:
    spell = SpellChecker()
    # lemmatizer = WordNetLemmatizer()
    # stop_words = set(stopwords.words("english"))

    @staticmethod
    def remove_special_chars(text):
        """Removes special characters from a string"""
        return re.sub('[^A-Za-z0-9]+', ' ', text)

    @staticmethod
    def remove_urls(text):
        return re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    @staticmethod
    def lower_case(text):
        """Converts a string to lower case"""
        return text.lower()

    @staticmethod
    def strip_whitespace(text):
        """Removes leading and trailing whitespace from a string"""
        return text.strip()

    @staticmethod
    def spellcheck(text):
        words = text.split()
        corrected_words = []
        for word in words:
            if BasePreprocessor.spell.unknown([word]):
                corrected_word = BasePreprocessor.spell.correction(word)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        return ' '.join(corrected_words)

    # @staticmethod
    # def lemmatize(tokens):
    #     return [BasePreprocessor.lemmatizer.lemmatize(token) for token in tokens]

    # @staticmethod
    # def remove_stopwords(tokens):
    #     return [token for token in tokens if token not in BasePreprocessor.stop_words]

    @staticmethod
    def preprocess_text(text):
        text = BasePreprocessor.remove_urls(text)
        text = BasePreprocessor.remove_special_chars(text)
        text = BasePreprocessor.lower_case(text)
        text = BasePreprocessor.strip_whitespace(text)
        # text = BasePreprocessor.spellcheck(text)
        # tokens = word_tokenize(text)
        # tokens = BasePreprocessor.remove_stopwords(tokens)
        # tokens = BasePreprocessor.lemmatize(tokens)
        return text
