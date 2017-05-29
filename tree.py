# xvasek06@vutbr.cz
# this file consains functions for trie tests

import argparse
import sys
import os
import math
import re
import time
import collections
import binascii
import IPv6PrefixComparison

ipv6prefix = 64

# class for nodes of trie
class Node:
	def __init__(self):
		self.value = 0
		self.weight = 0
		self.succesors = 0
		self.left = None
		self.right = None
		self.depth = 0
		self.nesting = 0
		self.skew = 0.0
		self.branching = 0

class Tree:
	cursor = None

	def __init__(self):
		self.root = Node()
		self.root.value = 1
		self.root.nesting = 1
		self.nesting = [0]*(ipv6prefix+1)
		self.branching = [0]*(ipv6prefix+1)

	# parse prefix into binary
	def add_prefix(self, prefix):
		prefix, length = prefix.split("/")
		length = int(length)
		current_length = 0
		prefix = prefix.split(":")
		binary = ""
		# one block equals 4 hexadecimal digits
		for block in prefix:
			if block == "":
				binary += "0000000000000000"
			else:
				binary += "{0:016b}".format(int(block, 16))
			current_length += 16
			# cuts binary string to the length of prefix
			if current_length >= length:
				binary = binary[0:length]
				break
		# sets trie cursor to root of trie
		self.cursor = self.root
		# adds each bit into trie
		for bit in binary:
			self.add(int(bit))
		# marks end of prefix
		self.cursor.value += 1

	# add bit into trie
	# set number of succesors of each node
	def add(self, value):
		if(value == 1):
			if(self.cursor.left == None):
				self.cursor.left = Node()
				if(self.cursor.right != None):
					self.cursor.succesors = 2
				else:
					self.cursor.succesors = 1
			self.cursor = self.cursor.left
		if(value == 0):
			if(self.cursor.right == None):
				self.cursor.right = Node()
				if(self.cursor.left != None):
					self.cursor.succesors = 2
				else:
					self.cursor.succesors = 1
			self.cursor = self.cursor.right

	# recursively calculate weight of each branch
	def weight(self, node):
		if node.left != None:
			node.weight += self.weight(node.left)
		if node.right != None:
			node.weight += self.weight(node.right)
		if node.value != 0:
			node.weight += node.value
		return node.weight
	
	# most of trie tests
	def tests(self, node, root):
		# set depth of trie
		node.depth = root.depth + 1
		# set prefix nesting
		node.nesting += root.nesting + node.value
		# get branching
		if root.succesors == 1:
			node.branching = root.branching + 1
		else:
			node.branching = 1
		# get skew
		if node.left != None and node.right != None:
			if node.left.weight > node.right.weight:
				node.skew = 1 - node.right.weight / node.left.weight
			elif node.right.weight > 0:
				node.skew = 1 - node.left.weight / node.right.weight
			else:
				node.skew = 1

		if node.left != None:
			self.tests(node.left, node)
		if node.right != None:
			self.tests(node.right, node)

	def trie_tests(self):
		# calculate weight
		if self.root.left != None:
			self.weight(self.root.left)
		if self.root.right != None:
			self.weight(self.root.right)
		# calculate data of nodes
		if self.root.left != None:
			self.tests(self.root.left, self.root)
		if self.root.right != None:
			self.tests(self.root.right, self.root)

	# get compcact data from trie about branching and nesting
	def get_stats(self, node):
		if (node.succesors == 2):
			self.branching[node.branching] += 1
		if node.value != 0:
			if node.left == None and node.right == None:
				self.nesting[node.nesting] += 1
		if node.left != None:
			self.get_stats(node.left)
		if node.right != None:
			self.get_stats(node.right)

	# print branching and nesting and call stats_by_depth
	def call(self, test_id):
		self.get_stats(self.root)
		with open(main.stats_path + "tree_nesting_" + str(test_id) + ".out", 'w') as outfile:
			total = sum(int(line) for line in self.nesting)
			if total > 0:
				for i, data in enumerate(self.nesting):
					outfile.write(str(i) + "\t" + str(data / total * 100) + "\n")
		with open(main.stats_path + "tree_branching_" + str(test_id) + ".out", 'w') as outfile:
			total = sum(int(line) for line in self.branching)
			if total > 0:
				for i, data in enumerate(self.branching):
					outfile.write(str(i) + "\t" + str(data / total * 100) + "\n")
		self.stats_by_depth(test_id)

	# goes through each level of trie and gathers informations
	def stats_by_depth(self, test_id):
		with open(main.stats_path + "tree_depth_" + str(test_id) + ".out", 'w') as outfile:
			print_level = [self.root]
			max_depth = 0
			# print level equals depth
			while print_level:
				next_level = list()
				depth = -1
				skew = 0
				skew_number = 0
				dist = 0
				dist_number = 0
				vals = 0
				# gather informations from nodes of equal depth
				for node in print_level:
					if node.value != 0:
						vals += node.value
					if node.succesors == 0:
						continue
					depth = node.depth
					if node.succesors == 2:
						skew += node.skew
						skew_number += 1
						dist += 1
					if node.succesors > 0:
						dist_number += 1
				if depth < 0:
					break;
				if skew_number > 0:
					skew = skew / skew_number
				else:
					skew = "?"
				if dist_number > 0:
					dist = dist / dist_number * 100
				else: 
					dist = "?"
				max_depth = depth
				outfile.write(str(depth) + "\t" + str(skew) + "\t" + str(dist) + "\n")
				# get next depth level
				for node in print_level:
					if node.left:
						next_level.append(node.left)
					if node.right:
						next_level.append(node.right)
					print_level = next_level
			# write results of each depth
			while max_depth < 64:
				max_depth += 1
				outfile.write(str(max_depth) + "\t?\t0.0\n")

# main function for trie
def commit(inputfile, test_id):
	tree = Tree()
	print("1/3 filling trie")
	with open(inputfile, 'r') as infile:
		for line in infile:
			tree.add_prefix(line)
	print("2/3 calculating trie tests")
	tree.trie_tests()
	print("3/3 gathering informations")
	tree.call(test_id)