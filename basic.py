# xvasek06@vutbr.cz
# this file contains functions for basic prefix tests

import collections
import sys
import IPv6PrefixComparison
import math

ipv6prefix = 64

# removes duplicates from input prefix file and gathers statistics about duplicates
def no_duplicates(inputfile, test_id, basics):
	# reads input file and using collections function and counts unique values
	x = ""
	y = collections.Counter()
	with open(inputfile, 'r') as infile:
		x = infile.readlines()
		y = collections.Counter(x)
	# if basic tests are enabled writes informations about duplicities
	if basics == True:
		with open(IPv6PrefixComparison.stats_path + "duplicates.out", "a") as duplicates:
			total_sum = (sum(y.values()))
			# gets number of keys (unique values)
			unique_sum = (len(list(y)))
			duplicates.write(str(test_id) + "\t" + str((total_sum - unique_sum) / total_sum * 100) + "\t" + str(total_sum) + "\t" + str(unique_sum) + "\n")
	# writes output containing only unique values
	outjoin = ''.join(list(y))
	with open(IPv6PrefixComparison.stats_path + "filtered_input_" + str(test_id) + ".out", 'w') as outfile:
		outfile.write(outjoin)

# calculates binary distribution for each depth
def bin_distribution(inputfile, test_id):
	# gets each prefix which is transformed into binary representation and sliced based on length
	output = ""
	with open(inputfile, 'r') as infile:
		for prefix in infile:
			prefix, length = prefix.split("/")
			length = int(length)
			current_length = 0
			prefix = prefix.split(":")
			binary = ""
			for block in prefix:
				if block == "":
					binary += "0000000000000000"
				else:
					binary += "{0:016b}".format(int(block, 16))
				current_length += 16
				if current_length >= length:
					binary = binary[0:length]
					break
			output += str(binary) + "\n"
	# goes through each prefix in binary representation and calculates no. of zeros and total for each depth
	binlist = []
	binlist = output.splitlines()
	no_zeros = [0]*(ipv6prefix)
	no_total = [0]*(ipv6prefix)
	distribution = [0]*(ipv6prefix)
	for line in binlist:
		for position, char in enumerate(line):
			if position < ipv6prefix:
				if char == "0":
					no_zeros[position] += 1
				no_total[position] += 1
			else:
				break
	# calculates percentage distribution for each depth
	for position in range(0, ipv6prefix):
		if (no_total[position] > 0):
			distribution[position] = no_zeros[position] / no_total[position] * 100
		else:
			distribution[position] = 0
	# writes results
	final_output = ""
	for record, total in enumerate(no_total):
		final_output += str(total) + "\t" + str(no_zeros[record]) + "\t" + str(distribution[record]) + "\n"
	with open(IPv6PrefixComparison.stats_path + "binary_distribution_" + str(test_id) + ".out", 'w') as outfile:
		outfile.write(final_output)

# calculates distribution of prefix length
def prefix_length(inputfile, test_id):
	# calculates number of prefixes on each line
	output = [0]*(ipv6prefix+1)
	with open(inputfile, 'r') as infile:
		for line in infile:
			prefix = int(line.split("/")[1])
			if prefix <= ipv6prefix:
				output[prefix] += 1
	suma = sum(output)/100	
	output2 = [0]*(ipv6prefix+1)
	# calculates percentage representation
	for i, value in enumerate(output):
		output2[i-1] = value/suma
	# writes data
	with open(IPv6PrefixComparison.stats_path + "prefix_length_" + str(test_id) + ".out", 'w') as outfile:
		for i in range(1,65):
			outfile.write(str(i) + "\t" + str(output[i]) + "\t" + str(output2[i-1])+ "\n")
