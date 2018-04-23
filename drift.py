#!/usr/bin/python3

import os
import sys
import argparse
import gensim.models
import pickle
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy

# parse command line args
parser = argparse.ArgumentParser(description = "Processes semantic drift over time.")
parser.add_argument("--input", "-i", default = "./preprocessed/", help = "the directory containing the text files", metavar = "input_dir")
parser.add_argument("--output", "-o", default = "./output/", help = "the directory into which to place the embedding and result files", metavar = "output_dir")
parser.add_argument("--smoothing", "-s", type = int, default = 1, help = "the amount of smoothing, in years")
parser.add_argument("--topn", "-t", type = int, default = 10, help = "the amount of smoothing, in years")
parser.add_argument("--csv", "-c", type = bool, default = False, help = "output .csv files with detailed information on each word")
parser.add_argument("--dimensionality", "-d", type = int, default = 50, help = "dimensionality to use for embeddings")
parser.add_argument("start_year", type = int, help = "the year from which to start calculating drift")
parser.add_argument("end_year", type = int, help = "the year until which to calculate drift")
ns = parser.parse_args()
start_year = ns.start_year
end_year = ns.end_year
window_len = ns.smoothing
input_dir = ns.input
output_dir = ns.output
dimensionality = ns.dimensionality
csv = ns.csv
top_n = ns.topn

# map each time window to a sentence list and an embedding model
sentence_sets = {}
models = {}

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
		model.save("%s%d+%dx%d.word2vec" % (output_dir, year, window_len, dimensionality))
		models[year] = model.wv
		
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
		# model = gensim.models.Word2Vec.load("%s%d+%dx%d.word2vec" % (output_dir, year, window_len, dimensionality))
		# models[year] = model.wv
		# del(model)
		# print("Loading models (%d - %d)" % (start_year, year), end = "\r")
	# except :
		# print("Fatal: No model found for %d (%s%d+%dx%d.word2vec)" % (year, output_dir, year, window_len, dimensionality), file = sys.stderr)
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
output = open(output_dir + "overlap-%d-%d+%dx%d" % (start_year, end_year, window_len, dimensionality), "wb")
pickle.dump(wordset, output)
output.close()

i = 1
p = 0
dict_metric = dict()
for word in wordset :
	union = set()
	rows = dict()
	for year in range(start_year, end_year + 1) :
		similar = models[year].most_similar(positive = [word], topn = top_n)
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
	dict_metric[word] = numpy.sum([numpy.std(row) for row in numpy.rot90(cols)])
	
	# write exhaustive data to csv
	if csv :
		try :
			with open("%s%s-%s-%s+%sx%dt%d.csv" % (output_dir, word, start_year, end_year, window_len, dimensionality, top_n), "w") as output :
				print(",%s" % (",".join(map(str, range(start_year, end_year + 1)))), file = output)
				for word in union :
					print(word, file = output, end = ",")
					print(",".join(map(str, [rows[year][word] for year in range(start_year, end_year + 1)])), file = output)
				print("", file = output)
				output.close()
		except :
			print("Error: could not write file %s%s-%s-%s+%sx%dt%d.csv; skipping" % (output_dir, word, start_year, end_year, window_len, dimensionality, top_n), file = sys.stderr)
	
	i += 1
	if (100 * i // len(wordset)) > p :
		p = (100 * i // len(wordset))
		print("Calculating drift (%d%%)" % (p), end = "\r")
print()

# sort list
print("Sorting...", end = "\r")
drifters = sorted(dict_metric, key = dict_metric.get)
#del(dict_metric)
print("Sorted    ")

# save sorted list
output = open(output_dir + "sorted-%s-%s+%sx%dt%d" % (start_year, end_year, window_len, dimensionality, top_n), "wb")
pickle.dump(drifters, output)
output.close()

print()
print("Best:")
for word in drifters[:30] :
	print("\t%s" % word)
