import argparse
from datetime import datetime
import json

class ArgumentParser:

    def __init__(self):
        
        self.search_parameters = {}
        
    def parse_parameters(self):    
        """
        Strings together class methods to parse cl arguments and if file indicated in those 
        parses also the ones written in the file. Cl arguemtns will be overwritten by the ones from file,
        in case of overlapping parameters.
        """
        self.parse_cl_arguments()
        if "filename" in self.search_parameters:
            self.read_search_parameters_from_json(self.search_parameters["filename"])
            del self.search_parameters["filename"]
        
        self.fill_in_missing_date()
        print(self.search_parameters)

    def read_search_parameters_from_json(self, filename: str) -> None:
        """
        Reads search parameters from json file
        """
        with open(filename, 'r') as json_file:
            the_parameters =  json.load(json_file)
        for key, value in the_parameters.items():
            self.search_parameters[key] = value

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
        
        self.search_parameters = vars(parser.parse_args())
        
        # removes empty arguments
        self. search_parameters = dict([[key, value] for key, value in self.search_parameters.items() if value])

    def get_parameters(self) -> dict:
        self.parse_parameters()
        return self.search_parameters

if __name__ == "__main__":

    a = ArgumentParser()
    print(a.get_parameters())