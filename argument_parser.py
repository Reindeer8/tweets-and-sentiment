import argparse
from datetime import datetime
import json

class ArgumentParser:

    def __init__(self):
        self.valid_search_keys = {'q', 'locale', 'result_type', 'count', 'until', 'since_id', 'max_id', 'include_entities', 'mode'}
        self.all_search_parameters = {}
        self.valid_search_parameters= {}
        self.invalid_search_parameters = {}
        
    def parse_parameters(self):
        """
        Strings together class methods to parse cl arguments and if file indicated in those 
        parses also the ones written in the file. Cl arguemtns will be overwritten by the ones from the file,
        in case of overlapping parameters.
        """        
        self.parse_cl_arguments()
        if "filename" in self.search_parameters:
            self.read_search_parameters_from_json(self.search_parameters["filename"])
            del self.search_parameters["filename"]

        for key, value in self.search_parameters.items():
            if key in self.valid_search_keys:
                self.valid_search_parameters[key] = value
            else:
                self.invalid_search_parameters[key] = value

    def read_search_parameters_from_json(self, filename: str) -> None:
        """Reads search parameters from json file"""
        with open(filename, 'r') as json_file:
            the_parameters = json.load(json_file)
        for key, value in the_parameters.items():
            self.search_parameters[key] = value

        return None
    
    def parse_cl_arguments(self):
        """
        Parses search parameters. Command line arguments may contain filename of json file with the parameters.
        Parameters in file take precedence over cli arguments.
        """
        parser = argparse.ArgumentParser(description='Indicate the names of the files')  
        
        parser.add_argument( '-f',  '--filename',   dest='filename',    type=str, help='txt file with search parameters', default='parameters.json')
        parser.add_argument( '-k',  '--keywords',   dest='q',           type=str, help='keywords to search by')
        parser.add_argument( '-until', '--until',  dest='until',       type=str, help='end date (format YYYY-mm-dd)')
        # parser.add_argument( '-r',  '--region',     dest='region',      type=str, help='region of tweets')
        parser.add_argument( '-la', '--language',   dest='lang',    type=str, help='language of tweets')

        parser.add_argument( '-c', '--count',   dest='count',    type=str, help='number of tweets')
        
        self.search_parameters = vars(parser.parse_args())
        
        # removes empty arguments
        self.search_parameters = dict([[key, value] for key, value in self.search_parameters.items() if value])

    def get_valid_search_parameters(self) -> dict:
        self.parse_parameters()
        return self.valid_search_parameters


if __name__ == "__main__":

    a = ArgumentParser()
    print(a.get_parameters())