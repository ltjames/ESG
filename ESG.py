import os
import json
import numpy as np
import tweepy

def get_api():
	# get access tokens from environment variable
	consumer_key = os.getenv("ESG_CONSUMER_KEY")
	consumer_secret = os.getenv("ESG_CONSUMER_SECRET")
	access_token = os.getenv("ESG_ACCESS_TOKEN")
	access_token_secret = os.getenv("ESG_ACCESS_TOKEN_SECRET")

	if (consumer_key is None
		or consumer_secret is None
		or access_token is None
		or access_token_secret is None):
		raise Exception('access tokens have not been set properly')

	# Creating the authentication object
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	# Setting your access token and secret
	auth.set_access_token(access_token, access_token_secret)
	# Creating the API object while passing in auth information
	api = tweepy.API(auth) 
	return api

def load_sciences():
	''' read in list of sciences from file'''
	fpath = os.path.join(__location__, 'list_of_sciences_wiki.txt')
	scifile = open(fpath,'r',encoding='UTF-8')
	sciences = []
	for line in scifile:
		lsplit = line.split(']] &ndash; ')
		if len(lsplit) > 1:
			name = lsplit[0][4:]
			desc = lsplit[1].rstrip()
			sciences.append((name,desc))
	scifile.close()

	return sciences

def process_adjectives():
	''' convert scientific category dictionaries into file
		of scientific adjectives + definitions'''

	dpath = os.path.join(__location__, 'dict')
	discs = os.listdir(dpath)
	apath = os.path.join(__location__, 'adjectives.txt')
	adjfile = open(apath,'w',encoding='UTF-8')

	for disc in discs:
		# read in all terms for discpline
		fpath = os.path.join(__location__, 'dict', disc)
		f = open(fpath,'r')
		disc_terms = [json.loads(line) for line in f]
		f.close()

		# filter adjectives and store word + defn
		for dt in disc_terms:
			if dt['pos'] == 'adj':
				word = dt['word']
				try: 
					defn = dt['senses'][0]['glosses'][0]
				except:
					print('gloss not found for',word)
				else:
					adjfile.write('{}::{}::{}\n'.format(disc[:-5],word,defn))

	adjfile.close()

def load_adjectives():
	''' read in list of adjectives from file'''

	fpath = os.path.join(__location__, 'adjectives.txt')
	adjfile = open(fpath,'r',encoding='UTF-8')
	adjectives = []
	for line in adjfile:
		lsplit = line.split('::')
		adjectives.append((lsplit[0],lsplit[1],lsplit[2].rstrip()))
	adjfile.close()

	return adjectives

def load_history():
	''' read in pair history from file'''

	fpath = os.path.join(__location__, 'history.txt')
	fhist = open(fpath,'r',encoding='UTF-8')
	history = [line.rstrip() for line in fhist]
	fhist.close()
	return history

def save_history(history):
	''' write pair history to file'''

	fpath = os.path.join(__location__, 'history.txt')
	fhist = open(fpath,'w',encoding='UTF-8')
	for pair in history:
		fhist.write(pair + '\n')
	fhist.close()

def load_pool():
	''' read in pool from file'''

	fpath = os.path.join(__location__, 'pool.txt')
	fpool = open(fpath,'r',encoding='UTF-8')
	pool = []
	for line in fpool:
		lsplit = line.split('::')
		pool.append((lsplit[0],lsplit[1].rstrip()))
	fpool.close()
	return pool
	
def save_pool(pool):
	''' write pool to file'''

	fpath = os.path.join(__location__, 'pool.txt')
	fpool = open(fpath,'w',encoding='UTF-8')
	for dat in pool:
		fpool.write(dat[0] + '::' + dat[1] + '\n')
	fpool.close()

def generate_pair(sciences, adjectives):
	''' match sciences and adjectives'''

	j = np.random.randint(0,len(sciences)-1)
	k = np.random.randint(0,len(adjectives)-1)
	sciname,scidef = sciences[j]
	adjcat,adj,adjdef = adjectives[k]

	newterm = adj[0].upper() + adj[1:] + ' ' + sciname
	newdef = scidef[0].upper() + scidef[1:] + ' ' + adjdef[0].lower() + adjdef[1:]
	return (newterm, newdef)

def topup_pool():
	''' generate pairs until there are 1000 in the pool'''

	# load in file data
	sciences = load_sciences()
	adjectives = load_adjectives()
	history = load_history()
	pool = load_pool()

	# top up pool
	while len(pool) < 1000:
		newterm, newdef = generate_pair(sciences, adjectives)
		if newterm not in history:
			pool.append((newterm,newdef))
			history.append(newterm)

	# write data to file
	save_history(history)
	save_pool(pool)


def tweet(api):
	''' tweet out the first pair in the pool'''

	pool = load_pool()
	tweet_text = '{}: {}'.format(pool[0][0],pool[0][1]) 
	api.update_status(tweet_text)
	pool.pop(0)
	save_pool(pool)

if __name__ == '__main__':
	__location__ = os.path.realpath(
		os.path.join(os.getcwd(), os.path.dirname(__file__)))
	api = get_api()
	topup_pool()
	tweet(api)