import tweepy
from twitter_creditentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from datetime import datetime
from pprint import pprint
from argument_parser import argument_parser


API_TYPE = "basic" 
# other option would be "advanced" for full archive search
# in the latter case parameter names should be adjusted accordingly

class tweet_search_bot:    

    def __init__(self):

        self.search_parameters = {}
        self.api = None    

    def get_search_parameters(self):
        """
        Parses arguments using the argument parser class
        """
        parser = argument_parser()
        self.search_parameters = parser.get_parameters()

    def connect_to_api(self, consumer_key, consumer_secret, access_token, access_token_secret):

        auth = tweepy.OAuthHandler( consumer_key, consumer_secret)
        auth.set_access_token( access_token, access_token_secret)

        self.api = tweepy.API(auth)

    def basic_search_for_tweets(self):
        if not self.api:
            raise Exception('No api to talk to') 
        q = self.search_parameters['keywords']
        try:
            tweets = self.api.search(q, count = 20, tweet_mode = 'extended')
        except :
            print('Something wrong with search request')
        return tweets

if __name__ == '__main__':
    the_bot = tweet_search_bot()
    the_bot.get_search_parameters()
    the_bot.connect_to_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    if API_TYPE == "basic":
        tweets = the_bot.basic_search_for_tweets()
    else:
        pass
    for tweet in tweets:
        print('\n\n')  
        print('Author: ' + tweet.author.name)
        print('The tweet is truncated: ', tweet.truncated)
        print('The text of tweet:\n' + tweet.full_text)

    '''
    auth = tweepy.OAuthHandler( CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token( ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    with open('output.txt', 'w', encoding='utf-8') as writer:
        for tweet in public_tweets:
            print(tweet.text)
            print()
            print()
            writer.write('This is the full tweet: \n')
            writer.write(str(tweet) + '\n\n')
            writer.write('Thisis the text of the tweet: \n')
            writer.write(tweet.text + '\n\n\n')
    '''     
        