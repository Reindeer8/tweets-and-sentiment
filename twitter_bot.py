import tweepy
from sentiment_analyzer import TweetSentimentAnalyzer
from twitter_creditentials import (
    CONSUMER_KEY, 
    CONSUMER_SECRET, 
    ACCESS_TOKEN, 
    ACCESS_TOKEN_SECRET
    )
from argument_parser import ArgumentParser
from time import time
import logging


DEFAULT_LOOKUP_TYPE = 'cursor'
DEFAULT_LANGUAGE = 'en'
DEFAULT_NUMBER_OF_TWEETS = 100

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
            self.interval_between_outputs = 10.0
            print('Initializing stream')

        def on_status(self, status):
            """Processess the new tweet received on stream"""
            self.the_bot.process_new_tweet(status)
            if not self.time_of_last_print:
                self.time_of_last_print = time()

            current_time = time()
            if self.interval_between_outputs <= current_time - self.time_of_last_print:
                self.time_of_last_print = current_time
                self.the_bot.print_sentiment_snapshot()
            
            if len(self.the_bot.tweets_with_sentiment) > self.the_bot.max_tweet_number:
                self.the_bot.print_sentiment_snapshot()
                self.disconnect()
                print('Retrieved the tweets and stream is closed now')
    
    def __init__(self):
        self.tweets_with_sentiment: list = []
        # number of potitive and negative tweets
        self.ratio: dict = {
            "Positive": 0,
            "Negative": 0,
            "Total"   : 0 
        }
        
        # it will store also the most retweeted tweet
        self.most_retweeted_tweet: dict = {}
        self.most_followed_tweet: dict = {}
        self.auth = None
        self.analyzer = TweetSentimentAnalyzer()

    def process_new_tweet(self, status):
        """Processess the newly retrieved tweet and
        adjust properties accordingly
        """
        try:
            text = status.extended_tweet["full_text"]
            print('Extended_tweet')
        except AttributeError:
            text = status.text
            print('Regular_tweet')

        # determines sentiment
        sentiment = self.analyzer.determine_sentiment(text)            
        self.tweets_with_sentiment.append([text, sentiment])
        
        # updates counters
        self.ratio[sentiment] += 1
        self.ratio["Total"] += 1
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

        self.get_search_parameters()
        if not self.search_parameters:
            raise Exception('No search parameters provided')

        # in case some crucial search parameters are not provided..
        self.max_tweet_number = self.search_parameters.get('count', DEFAULT_NUMBER_OF_TWEETS)
        self.type = self.search_parameters.get('type', DEFAULT_LOOKUP_TYPE)

        # trains Bayes classifier
        self.analyzer.train_naive_Bayes_classificator()

        if self.type == "cursor":
            tweets = self.search_with_cursor()
            for tweet in tweets:
                print('\n\n')
                print('Author: ' + tweet.author.name)
                print('The tweet is truncated: ', tweet.truncated)
                print('The text of tweet:\n' + tweet.full_text)

        elif self.type == 'stream':
            self.auth = None            
            self.get_live_tweets_with_stream()
            
    def create_nested_stream(self, *args):
        """Creates nested class, while passing as parameters the outer class,
        so the inner class would have access or the outer class methods and properties.
        It is needed for streaming option.
        Other, potentially better way, would be asyncronous processing of the incoming tweets
        """
        return self.StreamSentiment(self, *args)
            
    def get_search_parameters(self):
        """Parses arguments using the argument parser class"""
        parser = ArgumentParser()
        self.search_parameters = parser.get_valid_search_parameters()

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
            ACCESS_TOKEN_SECRET
            )
        for tweet in tweepy.Cursor(
            self.api.search_tweets, q=self.search_parameters['q']).items(self.max_tweet_number):

            #print(tweet)        
            self.process_new_tweet(tweet)

        self.print_sentiment_snapshot(most_followers=True, most_retweeted=True)

        return tweet_list

    def filter_with_stream(self):
        """Streams live tweets using modified tweepy stream."""        
        self.stream = self.create_nested_stream(
            CONSUMER_KEY, 
            CONSUMER_SECRET, 
            ACCESS_TOKEN, 
            ACCESS_TOKEN_SECRET
            )
        self.stream.filter(
            track = [self.search_parameters['q']],
            languages=['en']
            ) # language of interest must be en for sentiment analysis to work
        print('Starting the stream')
    
    def print_sentiment_snapshot(
        self, 
        most_retweeted = False,
        most_followers = False,
        summary = True
        ):
        
        """Prints snapshot of the sentiment in tweets accumulated"""
        if any([most_retweeted, most_followers, summary]):
            print()
            print()
            print()

        if most_followers:
            mpt = self.most_followed_tweet
            print(mpt["text"])
            print()
            print("Followers count:", mpt["followers count"])
            print("Sentiment:", mpt["sentiment"])
            print()
            print()
        
        if most_retweeted:
            mrt = self.most_retweeted_tweet
            print(mpt["text"])
            print()
            print("Retweet count:", mpt["retweets count"])
            print("Sentiment:", mpt["sentiment"])
            print()
            print()

        if summary:
            ratio = self.ratio
            num_of_pluses = round(20 * ratio["Positive"] / ratio["Total"])
            num_of_minuses = 20 - num_of_pluses
            print(f"P {ratio['Positive']} |" + "+" * num_of_pluses + " " + "-" * num_of_minuses + f"| {ratio['Negative']} N")
            print('Total number of tweets:', ratio['Total'])
            print()


if __name__ == '__main__':
    
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.info('It starts')
    the_bot = TweetSentimentBot()
    the_bot.run()