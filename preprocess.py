#!/usr/bin/python3

import xml.etree.ElementTree as etree
import os

directory_path = "./input/directory/"
input_path = "./input/input/"
output_path = "./preprocessed/"
ns = {"xsi" : "http://www.w3.org/2001/XMLSchema-instance"} # namespace for all of the XML files

blacklist = {""} # blacklist failed files; don't retry opening them
last_file = ""

# go through all the directory files
for filename in os.listdir(directory_path) :
	directory_file = open(directory_path + filename, "r")
	
	# each line specifies a text snippet; not all files are from one specific year
	i = 1
	p = 0
	lines = directory_file.read().split("\n")
	print("Processing %s (0%%)" % (filename), end = "\r")
	for line in lines :	
		# ? filename_identifier ? house yyyy_mm_dd ? party title
		fields = line.split()
		
		if len(fields) <= 4 or len(fields[1].split("_")) <= 1 :
			continue
		
		id = fields[1].split("_")
		year_str = fields[4].split("_")[0]
		
		if id[0] not in blacklist :
			try :
				if id[0] != last_file : # so that the same file isn't always closed and reopened
					# parse tree of src doc and open target year file
					source_tree = etree.parse(input_path + id[0] + ".xml")
					root = source_tree.getroot()
					last_file = id[0]
				
				aggregate_file = open(output_path + year_str + ".txt", "a")
				
				# find element by id using XPath
				element = root.find(".//*[@id='" + id[0] + "-" + id[1] + "']", ns)
				
				# if the element exists, add its contents to the aggregate (with a delimiter in case one is not already present)
				if element != None :
					text = ""
					
					# recursively check elements (depth-first; retains intended order and is most pythonic)
					elements = [element]
					while elements :
						e = elements.pop()
						if e.text != None :
							text += e.text
						elements += e.findall(".//", ns)
					
					aggregate_file.write(text)
					aggregate_file.write("\n")
				
				aggregate_file.close()
			except :
				blacklist |= {id[0]}
		
		i += 1
		if (100 * i // len(lines)) > p :
			p = (100 * i // len(lines))
			print("Processing %s (%d%%)" % (filename, p), end = "\r")
	print("Processing %s (done)" % (filename))
	
	directory_file.close()
