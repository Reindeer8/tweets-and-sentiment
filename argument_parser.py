import argparse
from datetime import datetime
import json

class argument_parser:

    search_parameters = {}

    def __init__(self):
        self.parse_cl_arguments()
        self.read_search_parameters_from_json()
        self.fill_in_missing_date()

    def read_search_parameters_from_json(self, filename: str) -> None:

        with open(filename, 'r') as json_file:
            search_parameters = json.load(json_file)
        
        return None

    def fill_in_missing_date(self: dict) -> None:
        """
        If starting date indicated and no end date provided, then end date will be set to now.
        If no start date indicated, then date of first tweet will be filled in.    
        """
        first_tweet_date = '2006-03-01'

        if 'date_from' in self.search_parameters and 'date_till' not in self.search_parameters:
            self.search_parameters['date_till'] = datetime.today().strftime('%Y-%m-%d')

        if 'date_from' not in self.search_parameters and 'date_till' not in self.search_parameters:
            self.search_parameters['date_from'] = first_tweet_date
    
    def parse_cl_arguments(self):
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

        print(the_arguments)

        # reads arguments from json file
        if the_arguments['filename']:
            json_arguments = self.read_search_parameters_from_json(the_arguments['filename'])
            del the_arguments['filename']
        print(the_arguments)
        # assigns json arguments to the main argument dictionary
        for json_key, json_value in json_arguments.items():
            the_arguments[json_key] = json_value
        
        the_arguments = self.fill_in_missing_date(the_arguments)
        print(the_arguments)
        self.search_parameters = the_arguments
        return the_arguments

    def get_parameters() -> dict:
        return self.search_

if __name__ == "__main__":

    a = argument_parser()
    print(a.get_parameters())