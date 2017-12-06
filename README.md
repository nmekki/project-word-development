# word development

Not yet certain, but the idea is to have a chain of roughly three components. The first (and most interesting) step is synonym clustering.  Then by filtering out words that are orthographically/phonetically dissimilar it should be possible to restrict the groups to only variants of the same words. Maybe it would be possible to put them in order by finding the path through them with the lowest total edit distance/most feature similarity.

## Motivation, method, hypotheses

This might be interesting as a way of finding sound correspondences through the history of a word, or possibly for etymology research. Also, since spelling was not/is not always standardized, this could help with searching texts that are not normalized (and be more accurate than a naïve fuzzy search).

## Relevant literature 

[A Minimally Supervised Approach for Synonym Extraction with Word Embeddings (Leeuwenberg et al., 2016)](https://ufal.mff.cuni.cz/pbml/105/art-leeuwenberg-et-al.pdf)

## Available data, tools, resources

## Project members

- Peter Schoener (peterr-s)
