#!/usr/bin/python3

import xml.etree.ElementTree as etree
import os

directory_path = "./directory/"
input_path = "./input/"
output_path = "./preprocessed/"
ns = {"xsi" : "http://www.w3.org/2001/XMLSchema-instance"} # namespace for all of the XML files

blacklist = {""} # blacklist failed files; don't retry opening them
last_file = ""

# go through all the directory files
for filename in os.listdir(directory_path) :
	directory_file = open(directory_path + filename, "r")
	print("reading " + filename)
	
	# each line specifies a text snippet; not all files are from one specific year
	for line in directory_file.read().split("\n") :	
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
					# get all descendants; content may be nested deeper
					if element.text != None :
						text = element.text
					else :
						text = ""
					for descendant in element.findall(".//", ns) :
						if descendant.text != None :
							text += " " + descendant.text
					
					aggregate_file.write(text)
					aggregate_file.write("\n")
				
				aggregate_file.close()
			except :
				blacklist |= {id[0]}
	
	directory_file.close()