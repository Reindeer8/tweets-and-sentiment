import argparse
from datetime import datetime
import json

class ArgumentParser:

    def __init__(self):
        self.valid_search_keys: set = {
            'track', 'q', 'locale', 'result_type', 'count', 'until', 'since_id',
            'max_id', 'include_entities', 'mode', 'type'
            }
        self.arguments: dict = {}
        self.valid_parameters: dict = {}
        self.invalid_parameters: dict = {}
        self.parse_arguments()
        
    def parse_arguments(self):
        """Strings together class methods to parse cl arguments and if file
        indicated in those parses also the ones written in the file.
        Cl arguemtns will be overwritten by the ones from the file,
        in case of overlapping parameters.
        """        
        self.parse_cl_arguments()
        if "filename" in self.arguments:
            self.read_search_parameters_from_json(self.arguments["filename"])
            del self.arguments["filename"]
        
        for key, value in self.arguments.items():
            if key in self.valid_search_keys:
                self.valid_parameters[key] = value
            else:
                self.invalid_parameters[key] = value
        if self.invalid_parameters:
            print('There are some unusable parameters provided')

    def read_search_parameters_from_json(self, filename: str) -> None:
        """Reads search parameters from json file"""
        with open(filename, 'r') as json_file:
            the_parameters = json.load(json_file)
        for key, value in the_parameters.items():
            self.arguments[key] = value

        return None
    
    def parse_cl_arguments(self):
        """Parses search parameters. Command line arguments may contain filename of json file with the parameters.
        Parameters in file take precedence over cli arguments.
        """
        parser = argparse.ArgumentParser(description='Indicate the names of the files')  
        
        parser.add_argument( '-f',  '--filename',   dest='filename',    type=str, help='txt file with search parameters', default='parameters.json')
        parser.add_argument( '-k',  '--keywords',   dest='q',           type=str, help='keywords to search by')
        parser.add_argument( '-until', '--until',  dest='until',       type=str, help='end date (format YYYY-mm-dd)')
        # parser.add_argument( '-r',  '--region',     dest='region',      type=str, help='region of tweets')
        parser.add_argument( '-la', '--language',   dest='lang',    type=str, help='language of tweets')

        parser.add_argument( '-c', '--count',   dest='count',    type=str, help='number of tweets')
        
        self.arguments = vars(parser.parse_args())
        
        # removes empty arguments
        self.arguments = dict([[key, value] for key, value in self.arguments.items() if value])

    def get_valid_parameters(self) -> dict:
        return self.valid_parameters

    def get_valid_search_parameters(self) -> dict:
        """Selects search arguments 
        suitable for the search"""
        valid_parameters_names = (
            'geocode', 'locale', 'result_type', 'count', 'until', 
            'since_id', 'max_id', 'include_entities')
        valid_search_parameters = {}
        for name in valid_parameters_names:
            if name in self.arguments:
                valid_search_parameters[name] = self.valid_parameters[name]        
        return valid_search_parameters
    
    def get_only_valid_stream_parameters(self) -> dict:
        """Selects search arguments suitable 
        for the stream filtering"""
        valid_parameters_names = (
            'follow', 'track', 'locations')

        valid_stream_parameters = {}
        for name in valid_parameters_names:
            if name in self.valid_parameters:
                valid_stream_parameters[name] = self.valid_parameters[name]
        return valid_stream_parameters

    def get_q_for_search(self):
        return self.valid_parameters['q']

    def get_track_for_stream(self):
        return self.valid_parameters['track']

    def a(*args,**kwargs):
        #print(args)
        print(kwargs)
        #print(q)

if __name__ == "__main__":

    a = ArgumentParser()
    #print(a.get_valid_search_parameters())
    #print(**a.get_only_valid_search_parameters())
    a.a(**a.get_valid_search_parameters())
    print(a.invalid_parameters)