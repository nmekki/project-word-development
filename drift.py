#!/usr/bin/python3

import os
import sys
import gensim.models
import pickle
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy

# constants
window_len = 1
input_dir = "./preprocessed/"
output_dir = "./output/"
dimensionality = 50

# map each time window to a sentence list and an embedding model
sentence_sets = {}
models = {}

# parse args
if len(sys.argv) <= 3 :
	print("Usage: %s [start_year] [end_year] [window_len]" % sys.argv[0], file = sys.stderr)
	sys.exit(3)
start_year = int(sys.argv[1])
end_year = int(sys.argv[2])
window_len = int(sys.argv[3])

if end_year < start_year :
	print("Fatal: End year must be after start year", file = sys.stderr)
	sys.exit(2)

# make models
print("Making models...", end = "\r")
year_range = end_year + 1 - start_year
i = 1
for year in range(start_year, end_year + 1) :
	try :
		input = open(input_dir + str(year) + ".txt")
		
		# normalize, split by sentences
		text = input.read()
		text = text.lower()
		sentences = sent_tokenize(text)
		sentences = [word_tokenize(sent) for sent in sentences]
		
		# add these sentences to every set in the time window
		for y in range(year, year + window_len) :
			if y not in sentence_sets :
				sentence_sets[y] = []
			sentence_sets[y] += sentences
	
	except :
		print("Could not find data for %d (%d.txt); skipping" % (year, year))

	# make embedding model regardless of whether data for this year was found (use windows)
	# however, there must be something in the set or else this won't work; fail if empty
	if len(sentence_sets[year]) == 0 :
		print("Fatal: No data in window for %d" % (year), file = sys.stderr)
		sys.exit(1)
	else :
		model = gensim.models.Word2Vec(sentence_sets[year], size = dimensionality, window = 5, min_count = 5, workers = 4)
		model.save("%s%d+%sx%d.word2vec" % (output_dir, year, sys.argv[3], dimensionality))
		
	# clear sentence set from memory
	del(sentence_sets[year])
	
	print("Making models (%d/%d)" % (i, year_range), end = "\r")
	i += 1
print()
del(sentence_sets)

# # intermittent load due to errors
# print("Loading models...", end = "\r")
# for year in range(start_year, end_year + 1) :
	# try :
		# model = gensim.models.Word2Vec.load("%s%d+%sx%d.word2vec" % (output_dir, year, sys.argv[3], dimensionality))
		# models[year] = model.wv
		# del(model)
		# print("Loading models (%d - %d)" % (start_year, year), end = "\r")
	# except :
		# print("Fatal: No model found for %d (%s%d+%sx%d.word2vec)" % (year, output_dir, year, sys.argv[3], dimensionality), file = sys.stderr)
		# sys.exit(4)
# print()

# consider only words that are in all models
print("Finding overlap...", end = "\r")
base = list(models.values())[0].vocab
wordset = set()
i = 1
p = 0
for word in base :
	add = True
	for model in models.values() :
		if word not in model :
			add = False
			break
	if add :
		wordset.add(word)
	
	i += 1
	if (100 * i // len(base)) > p :
		p = 100 * i // len(base)
		print("Finding overlap (%d%%; %d words)" % (p, len(wordset)), end = "\r")
print()

# save overlap set
output = open(output_dir + "overlap-%s-%s+%sx%d" % (sys.argv[1], sys.argv[2], sys.argv[3], dimensionality), "wb")
pickle.dump(wordset, output)
output.close()

i = 1
p = 0
dict_metric2 = dict()
for word in wordset :
	union = set()
	rows = dict()
	for year in range(start_year, end_year + 1) :
		similar = models[year].most_similar(positive = [word], topn = 10)
		union |= set([e[0] for e in similar])
		rows[year] = dict(similar)
	for year in rows :
		for w in union :
			if w not in rows[year] :
				if w in models[year] :
					rows[year][w] = models[year].similarity(word, w)
				else :
					rows[year][w] = 0
	cols = numpy.array([[row[val] for val in sorted(row)] for row in list(rows.values())])
	dict_metric2[word] = numpy.sum([numpy.std(row) for row in numpy.rot90(cols)])
	
	# write exhaustive data to csv
	try :
		with open("%s%s-%s-%s+%sx%d.csv" % (output_dir, word, sys.argv[1], sys.argv[2], sys.argv[3], dimensionality), "w") as output :
			print(",%s" % (",".join(map(str, range(start_year, end_year + 1)))), file = output)
			for word in union :
				print(word, file = output, end = ",")
				print(",".join(map(str, [rows[year][word] for year in range(start_year, end_year + 1)])), file = output)
			print("", file = output)
			output.close()
	except :
		print("Error: could not write file %s%s-%s-%s+%sx%d.csv; skipping" % (output_dir, word, sys.argv[1], sys.argv[2], sys.argv[3], dimensionality), file = sys.stderr)
	
	i += 1
	if (100 * i // len(wordset)) > p :
		p = (100 * i // len(wordset))
		print("Calculating drift (%d%%)" % (p), end = "\r")
print()

# sort list
print("Sorting...", end = "\r")
drifters = sorted(dict_metric2, key = dict_metric2.get)
#del(dict_metric2)
print("Sorted    ")

# save sorted list
output = open(output_dir + "sorted-%s-%s+%sx%d" % (sys.argv[1], sys.argv[2], sys.argv[3], dimensionality), "wb")
pickle.dump(drifters, output)
output.close()

print()
print("Best:")
for word in drifters[:30] :
	print("\t%s" % word)
