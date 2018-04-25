# semantic shifts

This project has pivoted slightly following the class discussion on Leeuwenberg et al.; the goal is now detection of semantic shifts.

## Motivation

In order to better understand older texts, especially those in which familiar words are used in unfamiliar ways, it is important to keep track of the correspondences between words' meanings over time. An example for an application of this might be a thesaurus which, rather than providing several synonyms, suggests only a few modern terms based on the time of writing of the query word. This sort of analysis could also shed light on possible future developments, either of a particular word or in terms of general tendencies.

## Method

The method is roughly as described in the paper by Kutuzov and Kuzmenko. To recap: they trained embedding models for each of several literary genres and compared the lists of the five most similar words in each embedding model for a given word. My plan is to build on this slightly by quantifying the magnitude of the shift as the sum of squares of differences in cosines over the union of these. This metric will not only increase with movement relative to the reference words, but will jump when more are added.

As a baseline, it should also be interesting to see how much variation can be expected between two parts of a split corpus from one isolated time period.

I will be using the Hansard Corpus of British political speeches since it spans about 200 years and is large enough that even the earlier years should be densely enough populated to get decent models. Still, I expect that I will need to smooth by training each model on a multi-year interval (with these intervals overlapping and representing their respective midpoints) in order to get accurate enough embeddings.

## Hypotheses

I'll be rather tentative about my predictions and say that words which, through established linguistic processes, have their meaning diluted or intensified will not be the most noticeably flagged by this system, nor will those whose meaning is reversed; these words will keep roughly the same contexts and thus not be picked up as different by an embedding model. I expect it to pick up mainly on changes for things that are replaced or influenced by technological developments or simply drift to unrelated or indirectly related meanings.

## Relevant literature 

[A Minimally Supervised Approach for Synonym Extraction with Word Embeddings (Leeuwenberg et al., 2016)](https://ufal.mff.cuni.cz/pbml/105/art-leeuwenberg-et-al.pdf)

Semantic Shifts and Word Embeddings: 2 Case Studies (Kutuzov and Kuzmenko, c. 2017, not published in this form)

[Exploration of Register-Dependent Word Semantics Using Word Embeddings (Kutuzov, Kuzmenko, and Markasova, 2016)](http://www.aclweb.org/anthology/W16-4005)

## Available data, tools, resources

The corpus used here is the Hansard corpus; though there were smaller corpora that would also have worked (e.g. CoHA), this one is free. It can be downloaded manually [here](http://www.hansard-archive.parliament.uk) but for scraping refer to [here](https://andrewwhitby.com/2013/10/26/uk-hansard-archive-urls/). The latter will only scrape the House of Commons texts, but these make up the majority of the immense corpus anyway. This results in about 4 GB of zipped XML, which is closer to 14 GB when unzipped.

[Online interaction with the Hansard corpus](https://corpus.byu.edu)

Because it takes so long to download, decompress, and preprocess, I have included the preprocessed data in the repo. Essentially, all of the dated text is stripped of XML and associated with its year.

This project uses Word2Vec/[gensim](https://radimhurek.com/gensim/index.html) for the embedding models.

## Project members

- Peter Schoener (peterr-s)
