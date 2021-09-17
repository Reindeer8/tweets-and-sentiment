from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import re 
import string
import random
from nltk.corpus import wordnet

# In large part this implementation of sentiment analysis was inspired by
# this article: 
# https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk

class SentimentAnalyzer:

    def __init__(self, text:str = None):

        self.text = text
        if text:
            self.tokenize(text)
            return
        else:
            self.text = None

    def clean(text: str):

    def tokenize(text):

        return word_tokenize(text)

    def normalize():
        pass
    
    def remove_noise(tweet_tokens, stop_words = ()):

        cleaned_tokens = []

        pos_dict = {'J':wordnet.ADJ, 'V':wordnet.VERB, 'N':wordnet.NOUN, 'R':wordnet.ADV}
        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]\
                +[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\
                    \.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]\
                    {2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})','', token)
            token = re.sub('(@[A-Za-z0-9_]+)','', token)
            pos = pos_dict[tag[0]]            
    
            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())

        return cleaned_tokens
    def train_naive_Bayes_classificator():
    def get_all_words(cleaned_tokens_list):
        for tokens in cleaned_tokens_list:
            for token in tokens:
                yield token

    def get_tweets_for_model(cleaned_tokens_list):
        for tweet_tokens in cleaned_tokens_list:
            yield dict([token, True] for token in tweet_tokens)
        
    def do_sentiment():    

        stop_words = stopwords.words('english')

        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []

        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

        all_pos_words = get_all_words(positive_cleaned_tokens_list)

        freq_dist_pos = FreqDist(all_pos_words)
        print(freq_dist_pos.most_common(10))
        positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

        positive_dataset = [(tweet_dict, "Positive")
                            for tweet_dict in positive_tokens_for_model]

        negative_dataset = [(tweet_dict, "Negative")
                            for tweet_dict in negative_tokens_for_model]

        dataset = positive_dataset + negative_dataset

        random.shuffle(dataset)

        train_set, test_set = dataset[:7000], dataset[7000:]

        classifier = NaiveBayesClassifier.train(train_set)

        print("Accuracy is:", classify.accuracy(classifier, test_set))

        print(classifier.show_most_informative_features(20))

        custom_tweets = ["I do not think Apple is a good company. Even more I belevie next quarter won't be their best",
        "Trust I seek and I am finding you",
        "This time it looks like lovely bag of shit",
        "The new gadget from Xtime is the shit"]

        custom_tokens = [remove_noise(word_tokenize(custom_tweet)) for custom_tweet in custom_tweets]

        sid = SentimentIntensityAnalyzer()
        for tweet_num, custom_tweet in enumerate(custom_tweets):
            print(custom_tweet) 
            print()
            print('With NaiveBayesClassifier...')
            print(classifier.classify(dict([token, True] for token in custom_tokens[tweet_num])), sep = '\n')
            print()
            print('With Vader...')
            print(sid.polarity_scores(custom_tweet))


if __name__ == "__main__":
    stopwords.ensure_loaded()
    
    print(dir(wordnet))
    print(wordnet.ADJ)
    #do_sentiment()