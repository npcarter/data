#!/n/eddyfs01/home/npcarter/.conda/envs/my_python/bin/python
import pexpect
import sys
import optparse
import os
import glob 
import csv 

# default values
nodes = 0
cpus = 0

parser = optparse.OptionParser()
parser.add_option('-n', action="store", default = 1, dest="nodes", type="int")
parser.add_option('-c', action="store", default = 35, dest = "cpus", type="int")
opts, args = parser.parse_args(sys.argv[1:])


if len(args) != 3:
	print "Usage: "+sys.argv[0]+" -n <# of worker nodes, default 1> -c <#of worker cores/node, default 35> <input sequence db> <directory of input hmms> <output directory>"
	sys.exit(2)

#if we get here, argument parsing has succeeded

seqdb = args[0]
seqdbPath = os.path.abspath(seqdb)  # get full path to the sequence database so srun doesn't have issues
hmmdb = args[1]
hmmdbPath = os.path.abspath(hmmdb)+"/*.hmm"  # ditto for hmm file
outDir = args[2]

seqName = os.path.basename(seqdbPath)
seqName = seqName.split('.')[0]
hmmName = os.path.basename(os.path.abspath(hmmdb))

if outDir[-1:] != "/":
	outDir = outDir + "/"   

outFileName = outDir+seqName+"_"+hmmName+"_"+str(opts.nodes)+"nodes_"+str(opts.cpus)+"cores.csv"
outFile = open(outFileName, "w")
outFileWriter = csv.writer(outFile) 
outFileWriter.writerow(["HMM", "Time"])
masterstring = '/n/eddyfs01/home/npcarter/hmmer/hmmer/src/hmmpgmd --master --seqdb '+seqdbPath

master = pexpect.spawn(masterstring)
master.expect("Master is ready.",timeout=None)

workerString = "srun -n "+str(opts.nodes)+" -c "+str(opts.cpus)+" --exclusive --mem 60000 -t 0 -p eddy /n/eddyfs01/home/npcarter/hmmer/hmmer/src/hmmpgmd --worker 10.242.44.36"
workers = pexpect.spawn(workerString)
for worker in range(opts.nodes):
	workers.expect("Worker is ready.", timeout=None)

child = pexpect.spawn('/n/eddyfs01/home/npcarter/hmmer/hmmer/src/hmmc2')
child.delaybeforesend = 0.0

hmmfiles = glob.glob(hmmdbPath)
for file in hmmfiles:
	with open(file) as infile:
		child.expect('Enter next sequence:')
		child.sendline('@--seqdb 1')
		hmmName = ""
		for line in infile:
			child.sendline(line)
			words = line.split(" ")
			if words[0] == "NAME":
				hmmName = words[2][:-1]

		child.expect('Elapsed Time: ', timeout=None)
		retval =child.readline()[:-1]
		outRow = [hmmName, str(retval)[:-1]]
		outFileWriter.writerow(outRow)
		master.expect("Hits:")  #Use this to flush master's output
		for worker in range(opts.nodes):
			workers.expect("Bytes:") #ditto for workers

outFile.close()
sys.exit(2)