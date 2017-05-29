# IPv6PrefixComparison

This is a project for bachelor thesis dealing with generators of IPv6 prefix tables. The main use is to compare large generated prefix tables used for utilization of routing algorithms with smaller already existing tables stored for example in routing tables.

## Prerequisites

- Python 3 is required to run the script. 
- Gnuplot is also required if graph generation from results is required.

## Running

There are several possibilities for running the script. 

### Tests
For tests over existing prefix files or using a generator to create such file we can use these commands:

&nbsp;&nbsp;&nbsp;**--input="input_file"** where input_file contains already generated or existing prefix table<br />
&nbsp;&nbsp;&nbsp;**--gen="command for generator"** starts specified generator and gathers informations about hardware constumptions<br /> 
&nbsp;&nbsp;&nbsp;of said generator

For these commands it is also required to specify types of tests:

&nbsp;&nbsp;&nbsp; **-t** for tests using trie (skew, nesting, branching)<br />
&nbsp;&nbsp;&nbsp; **-b** for basic tests (duplicity, prefix lenght, binary distribution)

Optional arguments:

&nbsp;&nbsp;&nbsp;**--name="name"** where name stands for name to be used in gnuplot

For gen switch it is also possible to specify number of runs:

&nbsp;&nbsp;&nbsp;**-m** runs generator for 10 times<br />
&nbsp;&nbsp;&nbsp;**-m="n"** runs generator for n times

Example: **_python3 main.py --input="generated" -b -t_**

### RMSE
There is also posibility to calculate RMSE (root mean square error) between source and generated samples:

&nbsp;&nbsp;&nbsp; **--rmse="source_id, generated_id"** where source_id contains id of tests over original sample and generated_id is id of tests<br /> 
&nbsp;&nbsp;&nbsp;over generated sample

For this command it is also required to specify types of tests to compare:

&nbsp;&nbsp;&nbsp; **-t** for tests using trie (skew, nesting, branching)<br />
&nbsp;&nbsp;&nbsp; **-b** for basic tests (duplicity, prefix lenght, binary distribution)

### Graphs
For graph generating there are 4 posibilities to start:

&nbsp;&nbsp;&nbsp; **-g** generates graphs over last sample<br />
&nbsp;&nbsp;&nbsp; **-g="id,id"** generates graphs over specified samples (1 or 2)<br />
&nbsp;&nbsp;&nbsp; **-e** generates graphs over RMSE sample in current run of script<br />
&nbsp;&nbsp;&nbsp; **-e="id,id"** generates graphs over existing RMSE samples (same as in switch g)

For these commands it is also required to specify types of graphs to generate:

&nbsp;&nbsp;&nbsp; **-t** for graphs using trie results (skew, nesting, branching)<br />
&nbsp;&nbsp;&nbsp; **-b** for graphs basic test results (duplicity, prefix lenght, binary distribution)<br />
&nbsp;&nbsp;&nbsp; **-r** for informations about generator resource constumption (needs 2 samples to compare)

Optional arguments:

&nbsp;&nbsp;&nbsp; **-png** generates graph as PNG instead of default EPS

It is also possible to manualy change name of sample in data/test_id.out

Example: **_python3 main.py -g="14" -b -t -r_**

### Erasing
For erasing of generated samples it is possible to use switch **-clean** which erases data/ and graphs/ folders

## Examples

For following examples, there is a folder named "data" which includes experimental data.

Runs all tests over already existing prefix file

- _python3 ./IPv6PrefixComparison.py --input="data/sada" -b -t_

Runs generator ipv6TableGen for 3 times over all tests 

- _python3 IPv6PrefixComparison.py --gen="python3 ipv6TableGen.py --input data/sada --output data/outsada -n 100000" -t -b -m="3"_

Calculates RMSE for generated sample and generates graphs for RMSE

- _python3 IPv6PrefixComparison.py --rmse="1,2" -b -t -e_

Runs generator for all tests then generates graphs

- _python3 IPv6PrefixComparison.py --gen="python3 ipv6TableGen.py --input data/sada --output data/outsada -n 10000" -t -b -g_

Generates comparison graphs for test samples 1 and 3

- _python3 IPv6PrefixComparison.py -g="1,3" -b -t_

Removes all data generated by script

- _python3 ./IPv6PrefixComparison.py -clean_

## Authors

- **Dominik Vašek**

## Licence

TBD
