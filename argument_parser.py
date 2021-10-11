import argparse
import json


class ArgumentParser:

    def __init__(self):
        self.valid_search_keys: set = {
            'track', 'q', 'locale', 'result_type', 'count',
            'until', 'since_id', 'max_id', 'include_entities', 
            'mode', 'action_type'}
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
    
    def parse_cl_arguments(self):
        """Parses search parameters. Command line arguments may contain filename of json file with the parameters.
        Parameters in file take precedence over cli arguments.
        """
        parser = argparse.ArgumentParser(description='Parameters to be used in looking up the tweets')  
        
        parser.add_argument('-f', '--filename', dest='filename', type=str, help='json file with search parameters', default='parameters.json', metavar = '')
        parser.add_argument('-k', '--keywords', dest='q', type=str, help='keywords to search by', metavar='')
        parser.add_argument('-until', '--until',  dest='until', type=str, help='end date (format YYYY-mm-dd)', metavar = '')
        parser.add_argument('-la', '--language', dest='lang', type=str, help='language of tweets', metavar='')
        parser.add_argument('-c', '--count', dest='count', type=int, help='number of tweets to be retrieved', metavar='')
        parser.add_argument('-a', '--action_type', dest='action_type', type=str, help='action type - cursor or stream', metavar='')

        self.arguments = vars(parser.parse_args())

        # removes empty arguments
        self.arguments = dict([[key, value] for key, value in self.arguments.items() if value])

    def get_valid_parameters(self) -> dict:
        return self.valid_parameters

    def get_valid_search_parameters(self) -> dict:
        """Selects search parameters
        suitable for the search"""
        valid_parameters_names = { 
            'geocode', 'locale', 'result_type', 'count', 'until', 
            'since_id', 'max_id', 'include_entities'}
        valid_search_parameters = {}
        for name in valid_parameters_names:
            if name in self.arguments:
                valid_search_parameters[name] = self.valid_parameters[name]

        # for sentiment analysis language needs to be English
        valid_search_parameters.update({'lang': 'en', 'tweet_mode': 'extended'})        
        return valid_search_parameters

    def get_valid_stream_parameters(self) -> dict:
        """Selects search parameters suitable
        for the stream filtering"""
        valid_parameters_names = ['follow', 'track', 'locations']

        valid_stream_parameters = {}
        for name in valid_parameters_names:
            if name in self.valid_parameters:
                valid_stream_parameters[name] = self.valid_parameters[name]
        # for sentiment analysis language needs to be English\
        if type(valid_stream_parameters['track']) != 'list':
            valid_stream_parameters['track'] = [valid_stream_parameters['track']]

        valid_stream_parameters['languages'] = ['en']
        return valid_stream_parameters

    def get_q_for_search(self):
        """Returns keyword value for filtering the live stream.
        It is needed as the first argument for search is positional
        """
        if 'q' in self.valid_parameters:
            q = self.valid_parameters['q']
        elif 'track' in self.valid_parameters:
            q = self.valid_parameters['track']
        return q

    def get_track_for_stream(self):
        """Returns keyword value for filtering the live stream.
        Unlike in case of search, stream's arguments all are keyword parameters
        """
        if 'track' in self.valid_parameters:
            track = self.valid_parameters['track']
        elif 'q' in self.valid_parameters:
            track = self.valid_parameters['q']
        return track 


if __name__ == "__main__":

    a = ArgumentParser()
    print(a.get_valid_parameters())
    print(a.get_valid_stream_parameters())