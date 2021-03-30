import sys
import subprocess
import os
from os import listdir
import argparse
from datetime import datetime

#directory walk the local directory (or specified directory) to identify and store the files in a list to "scan"
def getFiles(directory, stringfile):
	files = []

	for path, subdirs, localfiles in os.walk(directory):
		for filename in localfiles:
			f = os.path.join(path, filename)
			files.append(f)
	files = list(set(files))

	deletefiles = [string for string in files if stringfile in string or "scanner.py" in string]
	for removefile in deletefiles:
		#print "Removing ", removefile
		files.remove(removefile)

	return files

#read malicious strings from specified file and store them in a list
def getStrings(stringfile):
	with open(stringfile, 'rUb') as sfile:
		strings = sfile.readlines()
	strings = [string.lower() for string in strings]
	strings = [string.rstrip() for string in strings]
	strings = list(set(strings))

	return strings

#read malicious hashes from specified file and store them in a list
def getHashes(hashfile):
	with open(hashfile) as hfile:
		hashcontent = hfile.readlines()

	hashes = []
	for line in hashcontent:
		hashvalue = line.split(None, 1)[0]
		hashvalue = hashvalue.lower()
		hashes.append(hashvalue)
	hashes = list(set(hashes))

	return hashes

#search for strings from the strings file to the strings within the identified files
def checkStrings(strings,files):
	print ("Scanning files against strings")
	badFiles = []

	for f in files:
		print ("Scanning: "), f
		with open(f, 'rUb') as singlefile:
			filecontent = singlefile.readlines()
		filecontent = [line.lower() for line in filecontent]
		#print filecontent
		for s in strings:
			s = s.rstrip()
			#print "Checking against string: ", s
			if any(s in string for string in filecontent):
				print ("\tMALICIOUS STRING DETECTED - "), s
				badFiles.append(f)
	print ("")

	return badFiles


#compare the hashes from the hashes file to the hashes of the identified files
def checkHash(hashes,files):
	print ("Scanning files against hashes")
	badFiles = []

	for f in files:
		print ("Scanning: "), f

		command = "md5sum " + f + " | awk '{ print $1 }'"
		fileHash = subprocess.check_output(command, shell=True)
		fileHash = fileHash.rstrip()
		
		for h in hashes:
			#print "Checking against hash: ", h
			if h == fileHash:
				print ("\tMALICIOUS HASH DETECTED - "), h
				badFiles.append(f)
			'''
			#analyze each line of the file to check for malicious hash content, store file in list if a hash matches
			else:
				with open(f, 'rUb') as filecontent:
					filelines = filecontent.readlines()
				for line in filelines:
					with open('temp.txt', 'w') as tempfile:
						tempfile.write(line)
					command = "md5sum temp.txt | awk '{ print $1 }'"
					lineHash = subprocess.check_output(command, shell=True)
					lineHash = lineHash.rstrip()
					os.system("rm temp.txt")
					if h == lineHash:
						print "\tMALICIOUS HASH CONTENT DETECTED - ", h
						badFiles.append(f)
			'''
	print (" ")
	return badFiles

def main():
	startTime = datetime.now()
	print ("Malware scanner")
	print ("")

	parser = argparse.ArgumentParser(description = "Scan for malicious files")
	parser.add_argument("stringfile", type=str, help="File containing a list of malicious strings from known malicious files")
	parser.add_argument("-H", "--hashfile", type=str, help="File containing a list of MD5 hashes from known malicious files")
	parser.add_argument("-D", "--directory", type=str, help="The directory to scan; the default scan directory is the local directory", default= os.getcwd())
	args = parser.parse_args()

	#set the strings file,  hashes file, and directory (if the user specificied a directory) variable locations
	stringfile = args.stringfile
	hashfile = args.hashfile
	directory = args.directory

	#print the list of files identified
	files = getFiles(directory, stringfile)
	print ("Files identified: "), len(files)
	print ("-----")
	for f in files:
		print (f)
	print ("")

	#print the list of loaded strings
	strings = getStrings(stringfile)
	print ("Malicious strings loaded: "), len(strings)
	print ("-----")
	for s in strings:
		print (s)
	print ("")

	badStringFiles = checkStrings(strings,files)

	#print the list of loaded hashes
	if args.hashfile is not None:
		hashes = getHashes(hashfile)
		print ("Malicous hashes loaded: "), len(hashes)
		print ("-----")
		for line in hashes:
			print (line)
		print ("")

		badHashFiles = checkHash(hashes,files)


	#print the list of identified malicious files
	if args.hashfile is not None:
		badFiles = badStringFiles + badHashFiles
	else:
		badFiles = badStringFiles
	badFiles = list(set(badFiles))
	print ("Malicious files identified: "), len(badFiles)
	print ("-----")
	if len(badFiles) == 0:
		print ("No malware found")
	for f in badFiles:
		print (f)
	print ("")

	print ("Time taken to run scan: "), datetime.now() - startTime

if __name__ == "__main__":
	main()