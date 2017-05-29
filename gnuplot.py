# xvasek06@vutbr.cz
# this file contains functions for gnuplot

import sys
import math
import IPv6PrefixComparison
import os

graphs = ""

# sets arguments common for each graph
def	set_common(format):
	common = """
	reset 
	set boxwidth 0.8 relative
	set key on
	set grid
	set style fill solid border 0.75
	"""
	# also appends type of output
	if format == "png":
		common += "set terminal png size 1366, 768 font 'Helvetica,18'"
	else:
		common += "set terminal postscript eps color"
	return common

# defines type of plotting (called for each graph)
def plot(input, parameters, column):
	if input in ["binary_distribution_","rmse_binary_distribution_"]:
		to_plot = """plot \"""" + IPv6PrefixComparison.stats_path + input + str(parameters[0]) + """.out" using """ + str(column) + """ lc rgb "black" lw 1 ps 3 title \"""" + parameters[1] + """\", """
		if len(parameters) > 3:
			to_plot += """\"""" + IPv6PrefixComparison.stats_path + input + str(parameters[2]) + """.out" using """ + str(column) + """ lt 0 lc rgb "#77808080" pt 1 lw 1 ps 3 title \"""" + parameters[3] + """\""""
	else:
		to_plot = """plot \"""" + IPv6PrefixComparison.stats_path + input + str(parameters[0]) + """.out" using """ + str(column) + """ lt rgb "grey" w boxes title \"""" + parameters[1] + """\","""
		if len(parameters) > 3:
			to_plot +=	"""\"""" + IPv6PrefixComparison.stats_path + input + str(parameters[2]) + """.out" using """ + str(column) + """ w linespoints ls 1 ps 2 lw 1 lt rgb "black" title \"""" + parameters[3] + """\""""
	return to_plot

# saves the output of each function and start gnuplot
def generate():
	with open("graphs.in", 'w') as to_create:
		to_create.write("#!/usr/bin/gnuplot" + graphs)

	os.system("gnuplot graphs.in")
	os.remove("graphs.in")

# generates graph for consumption of generator
def hardware(format):
	global graphs
	
	if format == "png":
		terminal = "set terminal png size 1366, 768"
	else:
		terminal = "set terminal postscript eps color"
	
	graphs += """
	reset 
	""" + terminal + """

	set angles degrees
	set polar

	set style line 10 lt 1 lc 0 lw 0.3

	set grid polar 120.
	set grid ls 0
	set style data lines

	unset border
	unset param
	unset raxis

	set output \"""" + IPv6PrefixComparison.graph_path + """resources.""" + format + """\"

	set size square

	set xtics scale 0
	set xtics axis
	set ytics axis
	set yrange [-100:100]
	unset ytics
	set xtics 0,20,100
	set rtics 0,20,100
	set xrange [-100:100]

	M = 105
	set arrow from 0,0 to first M*cos(0), M*sin(0)
	set arrow from 0,0 to first M*cos(120), M*sin(120)
	set arrow from 0,0 to first M*cos(240), M*sin(240)

	set label "Time" at M*cos(0),M*sin(0) center offset char 1,1
	set label "Memory" at M*cos(120),M*sin(120) center offset char 1,1
	set label "Disk" at M*cos(240),M*sin(240) center offset char -1,-1
	set style line 11 lt 1 lw 2 pt 2 ps 2

	plot '""" + main.stats_path + """resources.out' using 1:2 notitle w lp, '' using 1:3 notitle w lp"""

# generates graphs for trie tests
def tree(parameters, format):
	global graphs
	common = set_common(format)

	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """tree_skew.""" + format + """\"
	set xrange [0:64]
	set yrange [0:1]
	set xtics 0,2,64
	set ytics 0.0, 0.1, 1.0
	set ylabel "Average skew"
	set xlabel "Trie depth"
	""" + plot("tree_depth_", parameters, 2)
 
	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """tree_distribution.""" + format + """\"
	set xrange [0:64]
	set yrange [0:100]
	set xtics 0,2,64
	set ytics 0,10,100
	set ylabel "Branching probability"
	set xlabel "Trie depth"
	""" + plot("tree_depth_", parameters, 3)
 
	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """tree_nesting.""" + format + """\"
	set xrange [0:32]
	set yrange [0.1:100]
	set xtics 0,2,32
	set logscale y
	set ylabel "Frequency"
	set xlabel "Prefix nesting"
	""" + plot("tree_nesting_", parameters, 2)
	 
	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """tree_branching.""" + format + """\"
	set xrange [0:32]
	set yrange [0.1:100]
	set xtics 0,2,32
	set logscale y
	set ylabel "Frequency"
	set xlabel "Step of branching"
	""" + plot("tree_branching_", parameters, 2)

# generates graphs for basic tests
def basic(parameters, format):
	global graphs
	common = set_common(format)

	graphs += common + """
	set xtics 0,2,64
	set output \"""" + IPv6PrefixComparison.graph_path + """length_distribution.""" + format + """\"
	set xrange [0:64]
	set yrange [0:60]
	set ytics 0,10,60
	set ylabel "Distribution"
	set xlabel "Trie depth"
	""" + plot("prefix_length_", parameters, 3)

	graphs += common + """
	set key bottom right
	set style data linespoints
	set xtics 0,2,64
	set output \"""" + IPv6PrefixComparison.graph_path + """binary_distribution.""" + format + """\"
	set xrange [0:64]
	set yrange [0:100]
	set ylabel "Probability of 0"
	set xlabel "Trie depth"
	""" + plot("binary_distribution_", parameters, 3)

# generates root mean square error graphs for trie tests
def rmse_tree(parameters, format):
	global graphs
	common = set_common(format)

	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_tree_skew.""" + format + """\"
	set xrange [0:64]
	set xtics 0,2,64
	set ylabel "RMSE"
	set xlabel "Trie depth"
	""" + plot("rmse_tree_skew_", parameters, 2)

	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_tree_distribution.""" + format + """\"
	set xrange [0:64]
	set xtics 0,2,64
	set ylabel "RMSE"
	set xlabel "Trie depth"
	""" + plot("rmse_tree_branching_probability_", parameters, 2)

	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_tree_nesting.""" + format + """\"
	set xrange [0:32]
	set xtics 0,2,32
	set ylabel "RMSE"
	set xlabel "Prefix nesting"
	""" + plot("rmse_tree_nesting_", parameters, 2)
	
	graphs += common + """
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_tree_branching.""" + format + """\"
	set xrange [0:32]
	set xtics 0,2,32
	set ylabel "RMSE"
	set xlabel "Step of branching"
	""" + plot("rmse_tree_branching_", parameters, 2)

# generates root mean square error graphs for basic tests
def rmse_basic(parameters, format):
	global graphs
	common = set_common(format)

	graphs += common + """
	set xtics 0,2,64
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_length_distribution.""" + format + """\"
	set xrange [0:64]
	set ylabel "RMSE"
	set xlabel "Trie depth"
	""" + plot("rmse_prefix_length_", parameters, 2)

	graphs += common + """
	set style data linespoints
	set xtics 0,2,64
	set output \"""" + IPv6PrefixComparison.graph_path + """rmse_binary_distribution.""" + format + """\"
	set xrange [0:64]
	set ylabel "RMSE"
	set xlabel "Trie depth"
	""" + plot("rmse_binary_distribution_", parameters, 2)