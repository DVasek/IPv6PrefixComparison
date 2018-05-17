# xvasek06@vutbr.cz
# for usage please read README

import argparse
import sys
import os
import math
import re
import collections
import time
import subprocess
import resource
import shutil
import random
######
import basic
import tree
import gnuplot

stats_path = "././data/"
graph_path = "./graphs/"
records = 0

# argument parser
def arg_parse():
	global argparsed
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', help="Input file", default="")
	parser.add_argument('--gen', help="Arguments to run generator", default="")
	parser.add_argument('--name', help="Specify name of generator", default="")
	parser.add_argument('--rmse', help="Calculates root mean square error takes 2 values: id of expected and id of results", default="")
	parser.add_argument('-clean', help="Deletes all outputs", action='store_true')
	parser.add_argument('-png', help="Graphs generated as png", action='store_true')
	parser.add_argument('-g', help="Create graphs", nargs='?', const="last", default="")
	parser.add_argument('-e', help="Create RMSE graphs", nargs='?', const="last", default="")
	parser.add_argument('-m', help="Runs generators including specified tests 10 times", nargs='?', const="10", default="")
	parser.add_argument('-t', help="Tests over binary tree", action='store_true')
	parser.add_argument('-r', help="Add resource graph", action='store_true')
	parser.add_argument('-b', help="Basic tests", action='store_true')
	# in case of wrong arguments
	try:
		args = parser.parse_args()
	except SystemExit:
		sys.stderr.write("error: wrong argument.\n")
		exit(1)	
	del sys.argv[0]
	argparsed = parser.parse_args(sys.argv)

# gets id for current operations
def id_set():
	# check if necessary folders are created
	if not os.path.exists(stats_path):
		os.makedirs(stats_path)
	if not os.path.exists(graph_path) and (argparsed.g or argparsed.e):
		os.makedirs(graph_path)

	last_id = 0
	last_sample = "@"
	# get current id and sample
	if os.path.exists(stats_path + "test_id.out"):
		with open(stats_path + "test_id.out", "r") as id_file:
			for line in id_file:
				column = line.split("\t")
				last_id = column[0]
				# check if name of current run is set, otherwise create own name
				if argparsed.name == "":
					if re.search("^Sample (.$)", column[1]) != None:
						last_sample = re.search("^Sample (.$)", column[1]).group(1)
	# if current run creates new tests, write new id
	if argparsed.input != "" or argparsed.gen != "":
		current_id = int(last_id) + 1
		current_sample = chr(ord(last_sample) + 1)
		with open(stats_path + "test_id.out", "a") as id_file:
			if argparsed.name != "":
				id_file.write(str(current_id) + "\t" + str(argparsed.name) + "\t\n")
			else:
				id_file.write(str(current_id) + "\tSample " + str(current_sample) + "\t\n")
		return current_id
	# no new generation is set
	else:
		return last_id

# runs generator and gathers basic info about run
def generator_resoures(test_id, past_run, arguments):
	start = time.time()
	global records
	# start generator
	proc = subprocess.call(arguments)
	# cpu usertime + systemtime
	cputime2 = time.time() - start
	cputime = sum(resource.getrusage(resource.RUSAGE_CHILDREN)[0:2])
	current_run = cputime
	cputime = cputime - past_run[0]
	# memory usage
	memory = sum(resource.getrusage(resource.RUSAGE_CHILDREN)[2:6])
	# disk usage
	disk = sum(resource.getrusage(resource.RUSAGE_CHILDREN)[9:11])
	current_disk = disk
	disk = current_disk - past_run[1]
	past_run[1] = current_disk
	# append info about generator
	# calculate number of generated prefixes
	if (past_run[0] == 0.0):
		records = sum(1 for line in open(argparsed.input))
	past_run[0] = current_run
	with open(stats_path + "resources_raw.out", "a") as res:
		res.write(str(test_id) + "\t" + str(records) + "\t" + str(cputime) + "\t" + str(memory) + "\t" + str(disk) + "\n")
	return past_run

# gather info about specified samples and calculate percentage diferences between them
def recalculate_resources(ids):
	resource_data = []
	with open(stats_path + "resources_raw.out", "r") as res:
		timemax = 0
		memmax = 0
		diskmax = 0
		# gather maximum values of specified samples
		for line in res:
			column = line.split("\t")
			if column[0] in ids:
				if (float(column[2]) / float(column[1])) > timemax:
					timemax = (float(column[2]) / float(column[1]))
				if (float(column[3]) / float(column[1])) > memmax:
					memmax = (float(column[3]) / float(column[1]))
				if (float(column[4]) / float(column[1])) > diskmax:
					diskmax = (float(column[4]) / float(column[1]))
		res.seek(0)
		# recalculate hardware use in percentage
		for line in res:
			column = line.split("\t")
			if column[0] in ids:
				resource_data.append([(((float(column[2]) / float(column[1])) / timemax) * 100), (((float(column[3]) / float(column[1])) / memmax) * 100), (((float(column[4]) / float(column[1])) / diskmax) * 100)])
	# swap rows and cols for gnuplot
	# add degrees on first column
	output_data = ""
	first_row = ""
	degree = 0
	first_line = True
	for line in zip(*resource_data):
		begin_line = True
		for column in line:
			# add degree on beginning of line
			if begin_line:
				output_data += str(degree) + "\t"
				degree += 120
				begin_line = False
			output_data += str(column) + "\t"
		output_data += "\n"
		# append 360 degrees on last row
		if first_line:
			first_row += "36" + output_data
			first_line = False
	output_data += first_row
	# write output
	with open(stats_path + "resources.out", "w") as resgraph:
		resgraph.write(output_data)

def rename_files(test_id):
	tests = argparsed.m.split(",")
	letter = len(tests[0] + ".out") + 2
	for file in os.listdir(stats_path):
		if file.endswith(tests[0] + ".out"):
			if file[-letter:-letter+1].isalpha():
				os.rename(stats_path + file, stats_path + file[:(len(file) - (len(tests[1]) + 4))] + tests[0] + "_0.out")
	if int(test_id) == int(tests[1]):
		lines = []
		with open(stats_path + "test_id.out", "r") as id_file:
			lines = id_file.readlines()
		with open(stats_path + "test_id.out", "w") as id_file:
			lines = lines[:-1]
			file = "".join(lines)
			id_file.write(file)

	runs = 1
	while os.path.isfile(stats_path + "filtered_input_" + str(tests[0]) + "_" + str(runs) + ".out") == True:
		runs += 1
	letter = len(tests[1] + ".out") + 2
	for file in os.listdir(stats_path):
		if file.endswith(tests[1] + ".out") and file[-letter:-letter+1].isalpha():
			os.rename(stats_path + file, stats_path + file[:(len(file) - (len(tests[1]) + 4))] + tests[0] + "_" + str(runs) + ".out")

# calculates root mean square error for tests
def rmse(expected, results):
	# calculates number of runs of specified test
	# expect at least 1 run
	runs = 1
	while os.path.isfile(stats_path + "filtered_input_" + str(results) + "_" + str(runs) + ".out") == True:
		runs += 1
	if (not os.path.isfile(stats_path + "filtered_input_" + str(results) + ".out" == False)) and (os.path.isfile(stats_path + "filtered_input_" + str(results) + "_0.out" == False)):
		print("error: missing results for rmse")
		exit(2)

	# sets files to operate with
	files = []
	if argparsed.b == True:
		files += [["binary_distribution_",2],["prefix_length_",2]]
	if argparsed.t == True:
		files += [["tree_nesting_",1],["tree_branching_",1],["tree_depth_",1],["tree_depth_",2]]
	for file in files:
		# gathers expected data of original sample
		expected_data = []
		with open(stats_path + file[0] + str(expected) + ".out", "r") as input_file:
			for line in input_file:
				data = line.split("\t")[file[1]]
				data = re.sub("\n", "", data)
				expected_data.append(data)
		# calculates mean error for each run with second power
		mean_data = [0] * len(expected_data)
		for run in range (0, runs):
			file_id = str(results)
			if runs > 1:
				file_id += "_" + str(run)
			cursor = 0
			with open(stats_path + file[0] + file_id + ".out", "r") as input_file:
				for line in input_file:
					data = line.split("\t")[file[1]]
					data = re.sub("\n", "", data)
					if expected_data[cursor] == "?":
						exp_data = "0"
					else:
						exp_data = expected_data[cursor]
					if data == "?":
						data = "0"
					mean_data[cursor] += pow((float(exp_data) - float(data)),2)
					cursor += 1
		# splits tree_depth into two files
		if file[0] == "tree_depth_":
			if file[1] == 1:
				file[0] = "tree_skew_"
			else:
				file[0] = "tree_branching_probability_"
		with open(stats_path + "rmse_" + file[0] + str(results) + ".out", "w") as rmse_file:
			# divides each value by number of runs including square root
			output_data = []
			for data in mean_data:
				if isinstance(data, str) == False:
					data = float(data) / runs
					data = math.sqrt(data)
				output_data.append(float(data) / 100)
			cursor = 0
			# writes results into file
			for data in output_data:
				rmse_file.write(str(cursor) + "\t" + str(data) + "\n")
				cursor += 1

# calls basic tests
def run_basics(test_id):
	print("starting basic tests")
	print("1/3 duplicity check")
	basic.no_duplicates(argparsed.input, test_id, True)
	argparsed.input = stats_path + "filtered_input_" + str(test_id) + ".out"
	print("2/3 binary distribution")
	basic.bin_distribution(argparsed.input, test_id)
	print("3/3 prefix length")
	basic.prefix_length(argparsed.input, test_id)
	print("basic tests done")
 
# calls trie tests
def run_trie(test_id):
	print("starting trie tests")
	tree.commit(argparsed.input, test_id)
	print("trie tests done")

# main function for tests
def run_tests(test_id):
	# starts basic tests including removal of duplicates
	if argparsed.b == True:
		run_basics(test_id)
	# if basic tests are not required removes duplicates for furher tests
	else:
		print("removing duplicates")
		basic.no_duplicates(argparsed.input, test_id, False)
		argparsed.input = stats_path + "filtered_input_" + str(test_id) + ".out"
	# starts trie tests
	if argparsed.t == True:
		run_trie(test_id)

# generates graphs
def generate_graphs(test_id, name):
	print("printing graphs")
	# sets output graphs as png if requested otherwise uses eps
	format = "eps"
	if argparsed.png == True:
		format = "png"
	# sets ids of tests
	parameters = []
	if argparsed.g == "last" or argparsed.e == "last":
		parameters = [int(test_id)]
	elif argparsed.g != "":
		parameters = argparsed.g.split(",")
	elif argparsed.e != "":
		parameters = argparsed.e.split(",")
	# adds names of tests specified in test_id file
	test = []
	param_length = len(parameters)
	with open(stats_path + "test_id.out", "r") as id_file:
		for line in id_file:
			column = line.split("\t")
			if column[0] == str(parameters[0]):
				test.extend([int(column[0]), column[1]])
			elif param_length > 1:
				if column[0] == str(parameters[1]):
					test.extend([int(column[0]), column[1]])
	# creates data for basic graphs
	if argparsed.r == True and len(parameters) > 1:
		recalculate_resources(parameters)
		gnuplot.hardware(test, format)
	# creates data for basic graphs
	if argparsed.e != "":
		if argparsed.b == True:
			gnuplot.rmse_basic(test, format, name)
		if argparsed.t == True:
			gnuplot.rmse_tree(test, format, name)
	# creates data for basic graphs
	else: 
		if argparsed.b == True:
			gnuplot.basic(test, format, name)
		if argparsed.t == True:
			gnuplot.tree(test, format, name)
	# starts generation of graphs
	if argparsed.r == True or argparsed.b == True or argparsed.t == True:
		gnuplot.generate()

def main():
	# parse arguments and get run id
	arg_parse()
	if argparsed.clean:
		print("cleaning")
		shutil.rmtree(graph_path, ignore_errors=True)
		shutil.rmtree(stats_path, ignore_errors=True)
		return
	if not argparsed.t and not argparsed.r and not argparsed.b:
		print("error: missing arguments")
		return
	test_id = id_set()
	if test_id == 0:
		print("error: missing tests")
		return
	if argparsed.gen != "" or argparsed.input != "":
		print("Test id: " + str(test_id))
	# parse arguments for generator
	# try to get output file for tests
	arguments = []
	if argparsed.gen != "":
		arguments = argparsed.gen.split()
		found = False
		output = ""
		for x in arguments:
			if found:
				output = x
				break
			if x.find("output") != -1:
				found = True
		if output != "":
			argparsed.input = output
	if argparsed.m != "":
		print("merging tests")
		rename_files(test_id)
	# starts generator and tests
	elif argparsed.gen != "":
		print("starting generator")
		generator_resoures(test_id, [0.0, 0], arguments)
		print("generator finished")
		run_tests(test_id)
	# starts tests on input prefix file
	elif argparsed.input != "":
		run_tests(test_id)
	# starts rmse calculation
	if argparsed.rmse != "":
		print("calculating rmse")
		parameters = argparsed.rmse.split(",")
		test_id = parameters[1]
		rmse(parameters[0], parameters[1])
	if argparsed.g != "" or argparsed.e != "":
		name = ""
		if argparsed.name != "":
			name = argparsed.name
		generate_graphs(test_id, name)


argparsed = None
if __name__ == "__main__":
	main()
