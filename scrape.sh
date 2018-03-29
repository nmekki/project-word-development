#!/bin/sh

# credit to Andrew Whitby for the URL list
# https://github.com/econandrew/uk-hansard-archive-urls/blob/master/urls.txt

wget -i urls.txt
mkdir input
unzip "*.zip" -d input