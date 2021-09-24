import tweepy
from twitter_creditentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from argument_parser import ArgumentParser


API_TYPE = "basic"
# other option would be "advanced" for full archive search
# in the latter case parameter names should be adjusted accordingly.
# Another way could be continuous or cursor

class CustomStream(tweepy.StreamListener):
    """Stream to get live tweets"""

    def on_status(self, status):
        print(status.text)
        # yield status.text

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False
       
class TweetSearchBot():
    """The class handles communication with twitter using tweepy.
    Its goal is to get tweets from twitter.
    """

    def __init__(self):
        
        self.search_parameters = {}
        self.auth = None
        self.connect_to_api(
            CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)   

    def get_search_parameters(self):
        """Parses arguments using the argument parser class"""
        parser = ArgumentParser()
        self.search_parameters = parser.get_valid_search_parameters()

    def connect_to_api(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Connects to the twitter api with creditentials from the twitter_creditentials.py"""
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth, wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)

    
    def basic_tweet_search_with_cursor(self):

        if not self.api:
            raise Exception('No api to talk to')
        tweet_list = []
        self.dummy(**self.search_parameters)
        for tweet in tweepy.Cursor(self.api.search, q = self.search_parameters['q'], tweet_mode = 'extended').items(10):
            tweet_list.append(tweet)        

        return tweet_list


    def get_live_tweets_with_stream(self):

        twitter_listener = FilteredStream(self.api)
        myStream = tweepy.Stream(auth = self.api.auth, listener=twitter_listener, tweet_mode = 'extended')
        print('Starting the stream')
        myStream.filter(track=["one"], languages = ["en"])
        

if __name__ == '__main__':

    from pprint import pprint

    the_bot = TweetSearchBot()
    the_bot.get_search_parameters()

    if API_TYPE == "basic":
        tweets = the_bot.basic_tweet_search_with_cursor()
    else:
        the_bot.get_live_tweets_with_stream()
        
    for tweet in tweets:
        print('\n\n')
        print('Author: ' + tweet.author.name)
        print('The tweet is truncated: ', tweet.truncated)
        print('The text of tweet:\n' + tweet.full_text)
    print()
    #pprint(tweets[0]._json)

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
        