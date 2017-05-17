#!/n/eddyfs01/home/npcarter/.conda/envs/my_python/bin/python
import sys
import os
import glob
import csv
import numpy

def stripHeaderFooter(fileName):
	retList = []
	with open(fileName, "r") as f:
		for line in f:
			# strip return and newline characters
			if line[-1] == '\n':  
				line = line[:-1]
			if line[-1] == '\r':
				line = line[:-1]

			words = line.split(" ")
			if words[0]!="Using" and words[0] != "Hit" and words[0] != "Exiting" and words[0]!= "HMM,Time":
				#This line has data we care about
				if line[-1] == "\n" or line[-1] == '\r':
					retList = retList + [line[:-1]]
				else:
					retList = retList + [line]
	return retList

def parseDataFile(baseValues, fileName, database):
	nodes = 0
	cores = 0
	version = "none"
	fileWords = fileName.split("/")

	if fileWords[0][0:2] == "h3":
		version = "HMMER3"
	if fileWords[0][0:2] == "h4":
		version = "HMMER4"

	if version == "none":
		print "Couldn't determine version from data path"
		exit(0)

	fileWords = fileName.split("_")
	#compute the number of nodes and cores that this test ran on
	for word in fileWords:
		if word[-5:] == 'nodes':
			nodes = int(word[:-5])
		if word[-9:] == 'cores.csv':
			cores = int(word[:-9])

	totalCores = 0
	if nodes > 1:
		totalCores = nodes * 36
	else:
		totalCores = cores
	timeList = []
	retList = []
	lines = stripHeaderFooter(fileName)
	for line in lines:
		fields = line.split(",")
		hmm = fields[0]
		time = float(fields[1])
		timeList = timeList + [time]
		speedup = baseValues[hmm]/time
		item = [hmm, version, database, totalCores, time, speedup]
		retList += [item]

#special case the mean, median, and stdev
	timeArray = numpy.array(timeList)
	median = numpy.median(timeArray)
	speedup = baseValues["median"]/median
	item = ["median", version, database, totalCores, median, speedup]
	retList += [item]

	stdev = numpy.std(timeArray)
	speedup = baseValues["stdev"]/stdev
	item = ["stdev", version, database, totalCores, stdev, speedup]
	retList += [item]

	mean = numpy.mean(timeArray)
	speedup = baseValues["mean"]/mean
	item = ["mean", version, database, totalCores, mean, speedup]
	retList += [item]

	return retList

# Main function starts here

baseValues = sys.argv[1]

# Figure out which database we're searching against
baseFile =os.path.basename(baseValues)
words = baseFile.split("_")

#Complete hack based on knowing the formats of the database names I'm using.   Will fail miserably if that format changes
#i.e., if we have a database that has a one-word name
database = words[0] + "_" + words[1]

#Construct a dictionary of HMM names with corresponding runtimes
baseTimes = {}
timeList = []
strippedBase = stripHeaderFooter(baseValues)
for line in strippedBase:
	fields = line.split(",")
	hmm = fields[0]
	time = float(fields[1])
	baseTimes[hmm] = time
	timeList = timeList + [time]

timeArray = numpy.array(timeList)
median = numpy.median(timeArray)
stdev = numpy.std(timeArray)
mean = numpy.mean(timeArray)

baseTimes["mean"] = mean
baseTimes["median"] = median
baseTimes["stdev"] = stdev

#collect the set of data files to process	
dirString = sys.argv[2]

if dirString[-1] != '/':
	#need to add a trailing /
	dirString = dirString + '/'

dirString = dirString+database+"*.csv"
print dirString
files = glob.glob(dirString)

#set up the output file
outFileName = sys.argv[3]
outFile = open(outFileName, "w")
outFileWriter = csv.writer(outFile)
outFileWriter.writerow(["Hmm", "Version", "Database", "Cores", "Runtime", "Speedup"])
print files
for file in files:
	parsedList = parseDataFile(baseTimes, file, database)
	for line in parsedList:
		outFileWriter.writerow(line)



