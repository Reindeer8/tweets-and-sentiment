# In large part this implementation of sentiment analysis was inspired by
# this article: 
# https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk

import nltk
import re 
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
# nltk.download('stopwords')
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import classify, NaiveBayesClassifier
from random import shuffle
from nltk.corpus import wordnet
# nltk.download('wordnet')

class SentimentAnalyzer:

    def __init__(self, text:str = None):
        self.classifier = self.train_naive_Bayes_classificator()
        self.text = text
        if text:
            self.tokenize(text)
            return
        else:
            self.text = None
    
    def clean_tokens_and_lemmetize(self, tweet_tokens:list, stop_words:tuple=()):
        cleaned_tokens = []

        pos_dict = {'V':'v', 'N':'n'}
        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]\
                +[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\
                    \.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]\
                    {2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', '', token)
            token = re.sub('(@[A-Za-z0-9_]+)', '', token)
            pos = pos_dict.get(tag[0], 'a')
    
            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            if len(token) > 1 and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())

        return cleaned_tokens

    def train_naive_Bayes_classificator(self):

        stop_words = stopwords.words('english')

        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []


        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(self.clean_tokens_and_lemmetize(tokens, stop_words))

        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(self.clean_tokens_and_lemmetize(tokens, stop_words))

        print('\nThis is the cleaned tokens list\n')
        print(positive_cleaned_tokens_list[:10])

        # puts all tokens in one pile, in dict format, where key is token followed by True
        positive_tokens_for_model = self.format_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = self.format_tweets_for_model(negative_cleaned_tokens_list)

        print(list(positive_tokens_for_model)[:10])
        positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]

        negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]

        dataset = positive_dataset + negative_dataset

        shuffle(dataset)
        print()
        print(type(dataset))
        print(len(dataset))

        self.train_data = dataset[:4000]
        self.test_data = dataset[4000:]

        return NaiveBayesClassifier.train(self.train_data)


    def format_tweets_for_model(self, cleaned_tokens_list):
        # reformats cleaned tokens in a format appropriate for the model
        for tweet_tokens in cleaned_tokens_list:
            yield dict([token, True] for token in tweet_tokens)
            
        
    def determine_sentiment(self, x:str = ''):


        custom_tweets = ["I do not think Apple is a good company. Even more I belevie next quarter won't be their best",
        "Trust I seek and I am finding you",
        "This time it looks like lovely bag of shit",
        "The new gadget from Xtime is the shit"]

        custom_tokens = [self.clean_tokens_and_lemmetize(word_tokenize(custom_tweet)) for custom_tweet in custom_tweets]

        for tweet_num, custom_tweet in enumerate(custom_tweets):
            custom_tokens = tweet_analyzer.clean_tokens_and_lemmetize(word_tokenize(custom_tweet)) 
            print(custom_tweet) 
            print()
            print('With NaiveBayesClassifier...')
            print(self.classifier.classify(dict([token, True] for token in custom_tokens[tweet_num])), sep = '\n')
            print()

    def accuracy_info(self):
        return classify.accuracy(self.classifier, self.test_data)

if __name__ == "__main__":

    stopwords.ensure_loaded()
    print(type(stopwords)) 
    tweet_analyzer = SentimentAnalyzer()
    
    
    custom_tweets = [
        "I do not think Apple is a good company. Even more I belevie next quarter won't be their best",
        "Trust I seek and I am finding you",
        "This time it looks like lovely bag of shit",
        "The new gadget from Xtime is the shit",
        "I do not like company Apple, but I do love Iphone"
        ]

    print('Accuracy is:', tweet_analyzer.accuracy_info())

    # sid = SentimentIntensityAnalyzer()
    for custom_tweet in custom_tweets:
        print(custom_tweet)
        print(tweet_analyzer.determine_sentiment(custom_tweet))