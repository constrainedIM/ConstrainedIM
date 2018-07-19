To run the CIM algorithm one should change the parameters in the CIM.py file

Note: if you are running this on a 64-bit machine you will need to recomplie the imm files.
Source code is found at IMM, IMM_2 and IMM_Balanced. In each directory run make and copy the compiled file (imm_discrete/ protected_imm_discrete/ inf_imm_discrete) to example/IMM_files.



Network files format:
For each network you must have the following files:
1. nodes.txt - a file containing information on all the nodes in the graph. Each line represents a node, it must start with an Id (the smallest one being 0)
	and then have the rest of the nodes attributes seperated by "\t".
	for example:
		"54\tJohn Doe\tUnited States\t31"
2. graph.txt - a file containg the edges of the graph. Each line represents a directed, weighted edge, by two node Ids and the weight all seperated by "\t"
	for example:
		"0\t54\t0.2333"
3. attributes.txt - a file containing two lines specifying the number of nodes and the number of edges, in the following format:
		"n=<num_of_nodes>"
		"m=<num_of_edges>"
4. graph_lt.inf - this is a copy of graph.txt with a different name.

optional:
protected_group.txt - this file contains one line specifying the size of the protected_group. You do not have to create it, if you specify the protected group using the UI the demo creates the file on it's own.

Note: You may also see the file "seed_set.txt" - this file contains the last seed set returned by IMM_Balanced on this network. It is used mostly for internal/ debugging purposes.

For the creation of files in the correct format you may use the helper functions provided in IMMDataParser.py, the file contains various functions for creating and manipulating these files.

