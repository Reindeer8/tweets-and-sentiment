import tweepy
import argparse
from twitter_creditentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import json
from datetime import datetime
from pprint import pprint


API_TYPE = "basic" 
# other option would be "advanced" for full archive search
# in the latter case parameter names should be adjusted accordingly

class tweet_search_bot:    

    def __init__(self):
        self.search_parameters = {}
        self.parse_arguments(self)

    def read_search_parameters_from_json(self, filename: str) -> None:

        with open(filename, 'r') as json_file:
            search_parameters = json.load(json_file)
        
        return None

    def fill_in_missing_date(self, search_parameters: dict) -> None:
        """
        If starting date indicated and no end date provided, then end date will be set to now.
        If no start date indicated, then date of first tweet will be filled in.    
        """
        first_tweet_date = '2006-03-01'

        if 'date_from' in self.search_parameters and 'date_till' not in self.search_parameters:
            self.search_parameters['date_till'] = datetime.today().strftime('%Y-%m-%d')

        if 'date_from' not in self.search_parameters and 'date_till' not in self.search_parameters:
            self.search_parameters['date_from'] = first_tweet_date
    
    def parse_arguments(self):
        """
        Parses search parameters. Command line arguments may contain filename of json file with the parameters.
        Parameters in file take precedence over cli arguments.
        """
        
        parser = argparse.ArgumentParser(description='Indicate the names of the files')  
        
        parser.add_argument( '-f',  '--filename',   dest='filename',    type=str, help='txt file with search parameters', default='parameters.json')
        parser.add_argument( '-k',  '--keywords',   dest='keywords',    type=str, help='keywords to search by')
        parser.add_argument( '-df', '--date_from',  dest='date_from',   type=str, help='start date')
        parser.add_argument( '-dt', '--date_till',  dest='date_till',   type=str, help='end_date')
        parser.add_argument( '-r',  '--region',     dest='region',      type=str, help='region of tweets')
        parser.add_argument( '-la', '--language',   dest='language',    type=str, help='language of tweets')
        
        the_arguments = vars(parser.parse_args())
        
        # removes empty arguments
        the_arguments = dict([[key, value] for key, value in the_arguments.items() if value])    

        # reads arguments from json file
        if the_arguments['filename']:
            json_arguments = self.read_search_parameters_from_json(the_arguments['filename'])
            del the_arguments['filename']
        
        # assigns json arguments to the main argument dictionary
        for json_key, json_value in json_arguments.items():
            the_arguments[json_key] = json_value
        
        the_arguments = self.fill_in_missing_date(the_arguments)
        print(the_arguments)
        self.search_parameters = the_arguments
        return the_arguments


    def connect_to_api(self, consumer_key, consumer_secret, access_token, access_token_secret):

        auth = tweepy.OAuthHandler( consumer_key, consumer_secret)
        auth.set_access_token( access_token, access_token_secret)

        api = tweepy.API(auth)
        return api

    def search_for_tweets_basic(self, api, search_parameters):
        
        q = search_parameters['keywords']
        try:
            tweets = api.search(q, count = 20, tweet_mode = 'extended')
        except :
            print('Something wrong with search request')
        return tweets

if __name__ == '__main__':

    search_parameters = parse_arguments()
    api = connect_to_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    if API_TYPE == "basic":
        tweets = search_for_tweets_basic(api, search_parameters)
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
        