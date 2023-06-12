import configparser

config = configparser.ConfigParser()
config.read('config.ini')

news_api_org_key = config['Articles']['NEWS_API_ORG_KEY']