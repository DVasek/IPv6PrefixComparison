#!/usr/bin/env python3

###########################################
#	resitel: Marian Lorenc                #
#	e-mail:  xloren09@stud.fit.vutbr.cz   #
#	vedouci: Ing. Jiri Matousek           #
###########################################

import getopt
import os
import sys
import ipaddress
import random
import shutil
import glob

# delka pole pro ukladani statistickych dat
# 129 pro IPv6, 33 pro IPv4
arrayLength = 129
# nastaveni vykreslovani krafu
v = False

# tisk napovedy
def printHelp():
	help = """Program ipv6TableGen slouzi ke generovani ipv6 tabulek na zaklade realnych tabulek.
	
Pouziti:
    -h                  napoveda

  Povinne parametry:
    --input='soubor'    zdrojova soubor obsahujici IPv6 prefixy ve formatu 
                        IPv6prefix/delka prefixu. Napr. 2620:104:2001::/48
    --output='soubor'   nazev soubor, ktery bude obsahovat vyslednou
                        tabulku
    -n 'cislo'          udava pocet generovanych prefixu

  Nepovinne parametry:
    -s                  do adresare STATS ulozi statistiky rozlozeni
                        bitu v prefixech a ze statistik vykresli grafy do *.png souboru
    -v                  grafy se místo do *.png uloží jako vektorový *.eps soubor"""
	
	print(help)

# vypis chyby  
def error(errNum):
	if(errNum == 1):
		sys.stderr.write("Chybne parametry!\n")
	elif(errNum == 2):
		sys.stderr.write("Chybny vstupni soubor!\n")
	elif(errNum == 3):
		sys.stderr.write("Vstupni soubor neexistuje!\n")
	elif(errNum == 4):
		sys.stderr.write("Zadejte nazev vstupniho souboru!\n")
	elif(errNum == 5):
		sys.stderr.write("Zadejte nazev vystupniho souboru!\n")
	elif(errNum == 6):
		sys.stderr.write("Zadejte pozadovany pocet prefixu!\n")
		
		
	else:
		sys.stderr.write("Neznama chyba!\n")
		
	cleanUp()
	sys.exit(1)

# zpracovani parametru.
# navraci hodnoty parametru	
def params():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hsvn:", ["input=", "output="])
	except getopt.GetoptError as err:
		error(1)

	input = None
	output = None
	n = None
	s = False
	v = False
	
	for o, a in opts:
		if o in ("-h"):
			printHelp()
			sys.exit(0)
		elif o in ("--input"):
			input = a
		elif o in ("--output"):
			output = a
		elif o in ("-s"):
			s = True
		elif o in ("-v"):
			s = True
			v = True
		elif o in ("-n"):
			n = a
			try:
				n = int(n)
			except:
				error(6)
		else:
			error(1)

	return input, output, n, s, v

# smaze docasne soubory
def cleanUp():
	if os.path.exists("__pycache__"):
		shutil.rmtree("__pycache__")

# prevadi spoctena statisticka data na procentualni vyjadreni jejich poctu v sade
def toPercent(statBits, statPref, statBitsPerPrefixLen, count):
	for i in range(1, arrayLength):
		if statPref[i] > 0:
			for j in range(1, arrayLength):
				statBitsPerPrefixLen[i][j] = 100 - (float(statBitsPerPrefixLen[i][j])/statPref[i] * 100)
		statBits[i] = 100 - (float(statBits[i])/count * 100)
		statPref[i] = float(statPref[i])/count * 100

	return statBits, statPref, statBitsPerPrefixLen

# zapisuje statisticka data do souboru
def writeStats(statBits, statPref, statBitsPerPrefixLen, fileName):
	if not os.path.exists(fileName):
		os.makedirs(fileName)
	try:
		file1 = open(fileName + "/BIT_STATS",'w')
		file2 = open(fileName + "/PREF_STATS",'w')
	except:
		print("chybny vystupni soubor")
		sys.exit()

	for i in range(1, arrayLength):
		file1.write(str(statBits[i]) + "\n")		
		file2.write(str(statPref[i]) + "\n")
		
		if statPref[i] > 0:
			file3 = open(fileName + "LEVELS/LEVEL_" + str(i),'w')
			for j in range(1, arrayLength):
				file3.write(str(statBitsPerPrefixLen[i][j]) + "\n")
			file3.close()
	file1.close()
	file2.close()

# vytvori skript pro gnuplot
# nastaveni pro grafy jednotlivych delek prefixu
def gnuplotIn(path):
	commands=open("gnuplot_in", 'w')
	
	format = ""
	ext=""
	
	if(v):
		format = "set terminal postscript eps color"
		ext = ".eps\""
	else:
		format = "set terminal png size 1024, 768"
		ext = ".png\""
	
	print("""#!/usr/bin/gnuplot
reset
""" + format + """
set title "IPv6 table prefix value distribution at each bit"
set key off
set grid
set style data linespoints
set ylabel 'percentage of 0(%)'
set xlabel 'bit level'
set xtics 4
set ytics 5
set xrange [0:64]
set yrange [0:100]""", file=commands)
	
	for datafile in glob.glob(path + "/*"):
		print('set output "' + datafile + ext.format( output=datafile ), file=commands )
		print('plot [1:64] "' + datafile + '" u ($0+1):1 w lp'.format( output=datafile ), file=commands )
	commands.close()

# vytvori skript pro gnuplot
# nastaveni pro grafy cele sady	
def gnuplotIn2(path):
	commands=open("gnuplot_in", 'w')
	format = ""
	ext=""
	
	if(v):
		format = "set terminal postscript eps color"
		ext = ".eps\""
	else:
		format = "set terminal png size 1024, 768"
		ext = ".png\""	
	
	print("""#!/usr/bin/gnuplot

reset
""" + format + """
set title "Synthesized IPv6 table prefix value distribution at each bit"
set key off
set grid
set style data linespoints
set xtics 4
set ytics 5
set ylabel 'percentage of 0(%)'
set xlabel 'bit level'
set xrange [0:64]
set yrange [0:100]
""", file=commands)

	print('set output "' + path + 'BIT_STATS' + ext, file=commands )
	print('plot [1:64] "' + path + 'BIT_STATS" u ($0+1):1 w lp', file=commands )


	print("""reset
""" + format + """

set title "Prefix length distribution of a synthesized IPv6 table."
set key off
set grid
set style data linespoints
set xtics 2
set ytics 5
set ylabel 'prefix length distribution (%)'
set xlabel 'prefix-length'
set xrange [0:64]
set yrange [0:50]
set boxwidth 0.75 absolute
set style fill solid 0.25 border
""", file=commands)

	print('set output "' + path + 'PREF_STATS' + ext, file=commands )
	print('plot [1:64] "' + path + 'PREF_STATS" u ($0+1):1 w boxes', file=commands )
	commands.close()

# provede analyzu predlozene sady a zajisti ulozeni a vykresleni
# vysledku do souboru
def doStats(inputFile, enableWriteStats):
	try:
		file = open(inputFile,'r')
	except:		
		raise FileExistsError
	prefixes = file.readlines()
	file.close()		
	
	try:	
		prefix = ipaddress.ip_address(prefixes[0][:prefixes[0].rfind('/', 0)])
	except:
		raise TypeError()
	
	statBits = [0] * arrayLength
	statPref = [0] * arrayLength
	statBitsPerPrefixLen = [[0 for x in range(arrayLength)] for y in range(arrayLength)]
	prefixCounter = 0

	# iterace nad prefixy a jejich analyza
	for i in prefixes:
		try:
			prefix = ipaddress.ip_address(i[:i.rfind('/', 0)])
		except:
			raise TypeError()
		if(type(prefix) != ipaddress.IPv6Address):
			raise TypeError()
		prefix = bin(int(prefix))[2:].zfill(arrayLength)
		prefixLen = int(i[i.rfind('/', 0)+1:])
		
		if(prefixLen > arrayLength):
			continue
		
		counter = 0
		
		for j in str(prefix):
			if(j == "1"):
				statBits[counter] += 1
				statBitsPerPrefixLen[prefixLen][counter] += 1
			counter += 1

		statPref[prefixLen] += 1
		prefixCounter += 1

	statBits, statPref, statBitsPerPrefixLen = toPercent(statBits, statPref, statBitsPerPrefixLen, prefixCounter)

	# zapis dat a vykresleni grafu
	if(enableWriteStats):
		index = inputFile.find("/")
		if(index == len(inputFile)):
			index = -1
		outputDir = inputFile[index+1:] + "_STATS/"
		filePath = outputDir + "LEVELS"
		if os.path.exists(outputDir):
			shutil.rmtree(outputDir)
		os.makedirs(outputDir)
		os.makedirs(filePath)
		
		writeStats(statBits, statPref, statBitsPerPrefixLen, outputDir)

		gnuplotIn(filePath)
		os.system("gnuplot <gnuplot_in")
		os.remove("gnuplot_in")
		gnuplotIn2(outputDir)
		os.system("gnuplot <gnuplot_in")
		os.remove("gnuplot_in")
	
	return statBitsPerPrefixLen, statPref		

# hlavni cast generatoru
# podle vstupni sady generuje nove prefixy	
def generator(stats, statPref, n):
	prefixLengths = []
	prefixes = []
	remainingPrefixes = n
	
	for i in range(1, arrayLength):
		if statPref[i] > 0:
			prefixLengths += [[i, statPref[i]]]
			
	prefixLengths.sort(key=lambda prefLen: prefLen[1])

	percent = 0
	for i in prefixLengths:
		i[1] += percent
		percent = i[1]
	
	# cyklus se opakuje pro kazdy prefic, dokud neni vygenerovan pozadovany pocet
	while(True):
		while(remainingPrefixes > 0):
			prefix = ""
			rnd = random.random() * 100
			for i in prefixLengths:
				if(rnd < i[1]):
					for j in range(1, i[0]):
						rnd = random.random() * 100
						if(rnd < stats[i[0]][j]):
							prefix += "0"
						else:
							prefix += "1"
					# print(prefix.ljust(arrayLength-1, '0')  + "/" + str(i[0]))
					prefix = (str(ipaddress.ip_address(int(prefix.ljust(arrayLength-1, '0') , 2))) + "/" + str(i[0]))
					
					prefixes += [prefix]
					remainingPrefixes -= 1
					break

		prefixes = list(set(prefixes))
		if(len(prefixes) == n):
			break
		else:
			remainingPrefixes = n - len(prefixes)

	return prefixes
	
###################################
#       HLAVNI TELO PROGRAMU      #
###################################

inputFile, outputFile, n, s, v = params()

if(inputFile == None):
	error(4)
if(outputFile == None):
	error(5)
if(n == None):
	error(6)
try:
	stats, statPref = doStats(inputFile, s)
except FileExistsError:
	error(3)
except TypeError:
	error(2)

prefixes = generator(stats, statPref, n)

file = open(outputFile,'w')
for prefix in sorted(prefixes):
	file.write(prefix + "\n")
file.close

if(s or v):
	doStats(outputFile, s)

cleanUp()