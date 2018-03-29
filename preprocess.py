#!/usr/bin/python3

import xml.etree.ElementTree as etree
import os

directory_path = "./directory"
input_path = "./input"
output_path = "./preprocessed"

# go through all the directory files
for filename in os.listdir(directory_path) :
	directory_file = open(directory_path + filename, "r")
	
	# each line specifies a text snippet; not all files are from one specific year
	for line in directory_file.read().split("\n") :
		# ? filename_identifier ? ? yyyy_mm_dd ? party title
		fields = line.split()
		id = fields[2].split("_")
		year_str = fields[4].split("_")[0]
		
		# parse tree of src doc and open target year file
		source_tree = etree.parse(input_path + id[0])
		root = source_tree.getroot()
		aggregate_file = open(output_path + "/" + year_str + ".txt", "a")
		
		# find element by id using XPath
		ns = {"xsi" : "http://www.w3.org/2001/XMLSchema-instance"}
		element = root.find(".//*[@id=" + id[0] + "-" + id[1] + "]", ns)
		
		# if the element exists, add its contents to the aggregate (with a delimiter in case one is not already present)
		if element != None :
			aggregate_file.write(element.text)
			aggregate_file.write("\n")
		
		close(aggregate_file)
	
	close(directory_file)