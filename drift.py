#!/usr/bin/python3

import os
import gensim

# constants
window_len = 1
input_dir = "./input"

# map each time window to a sentence list and an embedding model
sentence_sets = {}
models = {}

# read input files
print("reading...")
for filename in os.listdir(input_dir) :
	input = open(filename).read()
	
	# split year data off
	year = int(input[:4])
	input = input[5:]
	
	# split by sentences
	input = input.replace("!", ".")
	input = input.replace("?", ".")
	sentences = input.split(".")
	
	# add these sentences to every set in the time window
	for y in range(year, year + window_len) :
		if sentence_sets[y] == None : # `if ... not in ...` ?
			sentence_sets[y] = []
		sentence_sets[y] += sentences

print("making models...")
for year in sentence_sets :
	print(year + "\r")
	# turn sentence sets into embedding models
	model = Word2Vec(sentence_sets[year], size=100, window=5, min_count=5, workers=4)
	
	# save the models just in case
	model.save(str(year) + "-" + str(window_len) + ".word2vec")
	
	# associate compact model with year
	models[year] = model.wv
	
# consider only words that are in all models
print("finding overlap...")
base = models[[m for m in models][0]] # there is probably a better way to do this but this gets the first model
wordlist = []
for word in base :
	add = True
	for model in models :
		if word not in model :
			add = False
			break
	if add :
		wordlist += [word]

# go through all candidate words
print("building neighbor lists...")
word_scores = {}
for word in wordlist :
	top_tens_union = set()
	for model in models : # generate the set union over all models of the top ten lists
		top_tens_union |= set(model.most_similar(positive=[word], topn=10))
	
	# test metric: union cardinality
	word_scores[word] = len(top_tens_union)

# sort list
print("sorting...")
drifters = sorted(word_scores, key=word_scores.get)

print()
print("best:")
for word in drifters[:30] :
	print(word)