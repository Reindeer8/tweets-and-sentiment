from sentiment_analyzer import SentimentAnalyzer
import tweepy
from twitter_creditentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from argument_parser import ArgumentParser
from time import time
import logging


API_TYPE = "search"
# other option would be "advanced" for full archive search
# in the latter case parameter names should be adjusted accordingly.
# Another way could be continuous or cursor


class TweetSentimentBot:
    
    class StreamSentiment(tweepy.Stream):
        """The class handles communication with twitter using tweepy, 
        analyzes the sentiment and outputs the result.    
        """
        def __init__(self, the_bot, *args):
            super().__init__(*args)
            self.the_bot = the_bot            
            self.time_of_last_print = None            
            self.interval_between_outputs = 10
            self.tweet_limit = 100
            self.tweet_counter = 0
            print('Initializing stream')

        def on_status(self, status):

            text = status.text
            # determines sentiment
            sentiment = self.the_bot.analyzer.determine_sentiment(text)            
            self.the_bot.tweets_with_sentiment.append([text, sentiment])
            
            # Updates counters
            self.the_bot.ratio[sentiment] += 1
            self.the_bot.ratio["Total"] += 1
            mpt = self.the_bot.most_popular_tweet
            # check if the current tweet author has the most followers
            if not mpt or mpt['Followers count'] <= status.user.followers_count:
                self.the_bot.most_popular_tweet = {
                    "Text": text,
                    "Sentiment": sentiment,
                    "Followers count": status.user.followers_count
                }
                mpt = self.the_bot.most_popular_tweet
                # print(mpt)
                # print(mpt['Text'])
                # print()
                # print()
            if not self.time_of_last_print:
                self.time_of_last_print = time()
            current_time = time()
            if self.interval_between_outputs <= current_time - self.time_of_last_print :
                
                self.time_of_last_print = current_time
                self.the_bot.print_stream_snapshot()
            
            self.tweet_counter += 1            
            if self.tweet_counter > self.tweet_limit:
                raise Exception('Max tweet limit is reached')
     
        def on_error(self, status_code):
            if status_code == 420:
                print("Error occured while streaming")
                return False
    
    def __init__(self):
        self.tweets_with_sentiment:list = []
        self.ratio:dict = {
            "Positive": 0,
            "Negative": 0,
            "Total"   : 0 
        }
        self.most_popular_tweet: dict = {}
        self.auth = None
        self.analyzer = SentimentAnalyzer()
            
    def run(self):

        self.get_search_parameters()
        if not self.search_parameters:
            raise Exception('No parameters provided')
        self.analyzer.train_naive_Bayes_classificator()
        if API_TYPE == "basic":
            tweets = self.basic_tweet_search_with_cursor()
            for tweet in tweets:
                print('\n\n')
                print('Author: ' + tweet.author.name)
                print('The tweet is truncated: ', tweet.truncated)
                print('The text of tweet:\n' + tweet.full_text)
            print()
        else:            
            self.auth = None            
            self.get_live_tweets_with_stream()
            
    def create_nested_stream(self, *args):
        return self.StreamSentiment(self, *args)
            
    def get_search_parameters(self):
        """Parses arguments using the argument parser class"""
        parser = ArgumentParser()
        self.search_parameters = parser.get_valid_search_parameters()

    def connect_to_api(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Connects to the twitter api with creditentials from the twitter_creditentials.py"""
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(
            auth, 
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)
    
    def basic_tweet_search_with_cursor(self):

        if not self.api:
            raise Exception('No api to talk to')
        tweet_list = []
        for tweet in tweepy.Cursor(self.api.search, q = self.search_parameters['q'], tweet_mode = 'extended').items(10):
            tweet_list.append(tweet)        

        return tweet_list

    def print_stream_snapshot(self):
        mpt = self.most_popular_tweet
        ratio = self.ratio
        print()
        print()
        print()
        print(mpt["Text"])
        print()
        print("Followers count:", mpt["Followers count"])
        print("Sentiment:", mpt["Sentiment"])
        print()
        print()
        num_of_pluses = round(20 * ratio["Positive"] / ratio["Total"])
        num_of_minuses = 20 - num_of_pluses
        print(f"P {ratio['Positive']} |" + "+" * num_of_pluses + " " + "-" * num_of_minuses + f"| {ratio['Negative']} N")
        print('Total number of tweets:', ratio['Total'])
        print()

        # yield status.text

    def get_live_tweets_with_stream(self):

        # twitter_listener = TweetSentimentBot.StreamSentiment(self.api)
        self.stream = self.create_nested_stream(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.stream.filter(track = [self.search_parameters['q']], languages=['en'])
        print('Starting the stream')
        

if __name__ == '__main__':

    
    the_bot = TweetSentimentBot()
    the_bot.run()
    """
    the_bot.get_search_parameters()

    if API_TYPE == "basic":
        tweets = the_bot.basic_tweet_search_with_cursor()
    else:
        the_bot.create_nested_class(the_bot, the_bot.StreamSentiment)
        the_bot.get_live_tweets_with_stream()
        
    for tweet in tweets:
        print('\n\n')
        print('Author: ' + tweet.author.name)
        print('The tweet is truncated: ', tweet.truncated)
        print('The text of tweet:\n' + tweet.full_text)
    print()
    #pprint(tweets[0]._json)
    """

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
        