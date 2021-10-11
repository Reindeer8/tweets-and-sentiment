import tweepy
from sentiment_analyzer import TweetSentimentAnalyzer
from twitter_creditentials import (
    CONSUMER_KEY, 
    CONSUMER_SECRET, 
    ACCESS_TOKEN, 
    ACCESS_TOKEN_SECRET)
from argument_parser import ArgumentParser
from time import time
import logging


DEFAULT_ACTION_TYPE = 'cursor'
DEFAULT_LANGUAGE = 'en'
DEFAULT_NUMBER_OF_TWEETS = 10
DEFAULT_INTERVAL_BETWEEN_SNAPSHOTS = 10

class TweetSentimentBot:
    """The class that jugles all the elements to get tweets, 
    analyze sentiment and print results"""

    # The next class is an ugly way to implement streaming    

    class StreamSentiment(tweepy.Stream):
        """The class handles communication with twitter using tweepy,
        analyzes the sentiment and outputs the result.
        """
        def __init__(self, the_bot, *args):
            super().__init__(*args)
            self.the_bot = the_bot
            self.time_of_last_print = time()
            # time period between sentiment summary print
            self.interval_between_outputs = DEFAULT_INTERVAL_BETWEEN_SNAPSHOTS 
            print('Initializing stream')

        def on_status(self, status):
            """Processess the new tweet received on stream"""
            self.the_bot.process_tweet(status)
            if not self.time_of_last_print:
                self.time_of_last_print = time()

            current_time = time()
            if self.interval_between_outputs <= current_time - self.time_of_last_print:
                self.time_of_last_print = current_time
                self.the_bot.print_sentiment_snapshot(most_followers=True)

            if len(self.the_bot.tweets_with_sentiment) > self.the_bot.tweet_count_limit:
                self.disconnect()

    def __init__(self):
        self.tweets_with_sentiment: list = []
        # number of potitive and negative tweets
        self.ratio: dict = {
            "positive": 0,
            "negative": 0,
            "total"   : 0 
        }

        # it will store also the most retweeted tweet
        self.most_retweeted_tweet: dict = {}
        self.most_followed_tweet: dict = {}
        self.auth = None
        self.analyzer = TweetSentimentAnalyzer()

    def process_tweet(self, status):
        """Processess the newly retrieved tweet and
        adjust properties accordingly
        """
        if hasattr(status, 'full_text'):
            text = status.full_text
        elif hasattr(status, 'extended_tweet'):
            text = status.extended_tweet['full_text']
        elif hasattr(status, 'text'):
            text = status.text

        # determines sentiment
        sentiment = self.analyzer.determine_sentiment(text)            
        self.tweets_with_sentiment.append([text, sentiment])
        
        # updates counters
        self.ratio[sentiment] += 1
        self.ratio["total"] += 1
        mrt = self.most_retweeted_tweet  # mpt stands for Most Popular Tweet
        mft = self.most_followed_tweet  # mft - Most Followed Tweet

        # check if the current tweet author has the most followers
        if not mft or mft['followers count'] <= status.user.followers_count:
            self.most_followed_tweet = {
                "text": text,
                "sentiment": sentiment,
                "followers count": status.user.followers_count
            }

        if not mrt or mrt['retweet count'] <= status.retweet_count:
            self.most_retweeted_tweet = {
                "text": text,
                'sentiment': sentiment,
                'retweet count': status.retweet_count
            }

    def run(self):
        """Fetches tweets according to given search parameters, 
        analyzes sentiment and outputs results."""

        self.get_parameters()
        if not self.parameters:
            raise Exception('No search parameters provided')
        
        # in case some crucial search parameters are not provided..
        self.tweet_count_limit = self.parameters.get('count', DEFAULT_NUMBER_OF_TWEETS)
        self.type = self.parameters.get('action_type', DEFAULT_ACTION_TYPE)

        # trains Bayes classifier
        self.analyzer.train_naive_Bayes_classificator()

        if self.type == "cursor":
            self.search_with_cursor()
            
        elif self.type == 'stream':
            self.auth = None            
            self.filter_with_stream()
            
    def create_nested_stream(self, *args):
        """Creates nested class, while passing as parameters the outer class,
        so the inner class would have access to the outer class methods and properties.
        It is needed for streaming option.
        Other, potentially better way, would be asyncronous processing of the incoming tweets
        """
        return self.StreamSentiment(self, *args)
            
    def get_parameters(self):
        """Parses arguments using the argument parser class"""
        self.parser = ArgumentParser()
        self.parameters = self.parser.get_valid_parameters()

    def connect_to_api(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Connects to the twitter api with creditentials from the twitter_creditentials.py"""
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth, wait_on_rate_limit=True)
    
    def search_with_cursor(self):
        """Searches for the tweets using cursor"""
        self.connect_to_api(
            CONSUMER_KEY, 
            CONSUMER_SECRET, 
            ACCESS_TOKEN, 
            ACCESS_TOKEN_SECRET)

        for tweet in tweepy.Cursor(
            self.api.search_tweets, self.parser.get_q_for_search(), **self.parser.get_valid_search_parameters()).items(self.tweet_count_limit):
        
            self.process_tweet(tweet)

        self.print_sentiment_snapshot(most_followers=True, most_retweeted=True)

    def filter_with_stream(self):
        """Streams live tweets using modified tweepy stream."""        
        self.stream = self.create_nested_stream(
            CONSUMER_KEY, 
            CONSUMER_SECRET, 
            ACCESS_TOKEN, 
            ACCESS_TOKEN_SECRET)
        
        self.stream.filter(
            **self.parser.get_valid_stream_parameters()) # language of interest must be en for sentiment analysis to work
        self.print_sentiment_snapshot(most_followers=True, most_retweeted=True)

    def generate_sentiment_snapshot(self, most_retweeted=False, most_followers=False, summary=True):

        output = ''
        if any([most_retweeted, most_followers, summary]):
            output += '\n'*3

        if most_followers:
            mft = self.most_followed_tweet
            if mft:
                output += mft['text'] + '\n'*3 + 'Followers count: ' + str(mft['followers count']) +\
                    '\n' + 'Sentiment: ' + mft['sentiment'] + '\n'*3
            else:
                output+= 'No most followed author\'s tweet'
        
        if most_retweeted:
            mrt = self.most_retweeted_tweet
            if mrt:
                output += mrt['text'] + '\n'*3 
                output += 'Retweet count: ' + str(mrt['retweet count']) + '\n' + \
                    'Sentiment: ' + str(mrt['sentiment']) + '\n'*3
            else:
                output += 'There is no most retweeted tweet'

        if summary:
            ratio = self.ratio
            num_of_pluses = round(20 * ratio['positive'] / ratio['total'])
            num_of_minuses = 20 - num_of_pluses
            output +=f'P {ratio["positive"]} |{"+" * num_of_pluses} {"-" * num_of_minuses} | {ratio["negative"]} N'
            output += '\n'*2 + 'Total number of tweets:' + str(ratio['total']) + '\n'

        return output

    def print_sentiment_snapshot(
        self, most_retweeted=False, most_followers=False, summary=True):
        """Prints sentiment snapshot"""
        print(self.generate_sentiment_snapshot(most_retweeted=most_retweeted,  most_followers=most_followers, summary= summary))
        return
        

if __name__ == '__main__':
    
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.info('It starts')
    the_bot = TweetSentimentBot()
    the_bot.run()