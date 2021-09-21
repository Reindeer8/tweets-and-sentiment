# In large part this implementation of sentiment analysis was inspired by
# this article: 
# https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk

import re 

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import classify, NaiveBayesClassifier
from random import shuffle
# from nltk.corpus import wordnet

class SentimentAnalyzer:

    def __init__(self):

        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.train_naive_Bayes_classificator()
            
    def clean_tokens_and_lemmetize(self, tweet_tokens:list) -> list:
        """Removes hyperlinks, mentions, adds positional tag and then lemmatizes tweet tokens"""

        cleaned_tokens = []

        pos_dict = {'V':'v', 'N':'n'}
        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]\
                +[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\
                    \.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]\
                    {2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', '', token)
            token = re.sub('(@[A-Za-z0-9_]+)', '', token)
            pos = pos_dict.get(tag[0], 'a')
    
            token = self.lemmatizer.lemmatize(token, pos)

            if len(token) > 1 and token.lower() not in self.stop_words:
                cleaned_tokens.append(token.lower())

        return cleaned_tokens

    def format_tweets_for_model(self, cleaned_tokens_list:list):
        """Reformats cleaned tokens in a format appropriate for the model"""

        for tweet_tokens in cleaned_tokens_list:
            yield dict([token, True] for token in tweet_tokens)

    def train_naive_Bayes_classificator(self):        
        """ Tokenizes, cleans and lemmetizes nltk tweet samples 
        and uses those to train naive Bayes classificator
        """
        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []

        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(self.clean_tokens_and_lemmetize(tokens))
        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(self.clean_tokens_and_lemmetize(tokens))

        negative_dataset = [(token, "Negative") for token in self.format_tweets_for_model(negative_cleaned_tokens_list)]
        positive_dataset = [(token, "Positive") for token in self.format_tweets_for_model(positive_cleaned_tokens_list)]

        dataset = positive_dataset + negative_dataset

        shuffle(dataset)

        self.train_data = dataset[:8000]
        self.test_data = dataset[8000:]

        self.classifier = NaiveBayesClassifier.train(self.train_data)
    
    def determine_sentiment(self, x:str = ''):

        custom_tokens = self.clean_tokens_and_lemmetize(word_tokenize(x))
        return self.classifier.classify(dict([token, True] for token in custom_tokens))

    def accuracy_info(self):
        """Calculates accuracy of the classifier 
        based on 20% of nltk sample tweets
        """
        return classify.accuracy(self.classifier, self.test_data)

if __name__ == "__main__":
    
    tweet_analyzer = SentimentAnalyzer()
    
    custom_tweets = [
        "I do not think Apple is a good company. Even more I believe next quarter won't be their best",
        "Trust I seek and I am finding you",
        "This time it looks like very interesting",
        "The new gadget from Xtime is the shit",
        "I do not like company Apple, but I do love Iphone",
        "This accuracy is very bad",
        "This accuracy is decent",
        "This accurary is good"
        ]

    print('Accuracy is:', tweet_analyzer.accuracy_info())

    for custom_tweet in custom_tweets:
        print(custom_tweet)
        print(tweet_analyzer.determine_sentiment(custom_tweet))