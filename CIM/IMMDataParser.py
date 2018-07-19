import os
import shutil
from io import open

class IMMDataParser:

    def __init__(self, files_dir_name, node_properties, encoding=None):
        #Create object representing an IMBalanced input files directory
        if(encoding is None):
            encoding = "utf-8"
        self.encoding = encoding
        self.files_dir_name = files_dir_name
        self.nodes_file_name = files_dir_name + "/nodes.txt"
        self.graph_file_name = files_dir_name + "/graph.txt"
        self.attribute_file_name = files_dir_name + "/attribute.txt"
	self.protected_group_file_name = files_dir_name + "/protected_group.txt"
        self.node_properties = node_properties

    def build_row(self, data):
	#Concatenate strings in data seperated by white-space
        row = data[0]
        for attr in data[1:]:
            row = row + "\t" + attr
        row = row + "\n"
        return row

    def create_nodes(self, nodes_gen):
	#Build nodes file from iterable nodes_gen where each element in nodes_gen is an array of string representing the node
	#e.g. [57, "John Doe", "United States"]...
        with open(self.nodes_file_name, "w", encoding=self.encoding) as f:
            for node_data in nodes_gen:
                node = self.build_row(node_data)
                f.write(node)

    def create_attribute_file(self, n, m):
	#Given n = num of vertices, m = num of edges create file containing both.
	#This is required for IMM
        with open(self.attribute_file_name, "w", encoding=self.encoding) as file:
            file.write(u"n=" + str(n) + "\n")
            file.write(u"m=" + str(m) + "\n")

    def format_graph(self, graph_file_name, delimiter=None, header=False, encoding="utf-8", remove_weights=False):
	#Parse a file representing graph into the format required by IMM, can ignore weights, ignore first line.
	#delimiter specifies how the data is seperated in the input file, default is '\t'
        if (delimiter is None):
            delimiter = "\t"

        n = 0
        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                if(line != "" and line != "\n"):
                    n += 1

        m = 0
        with open(graph_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                if (line != "" and line != "\n"):
                    m += 1

        if(header):
            m -= 1

        self.create_attribute_file(n, m)

        with open(self.graph_file_name, "w", encoding=self.encoding) as f:
            with open(graph_file_name, "r", encoding=encoding) as file:
                if (header):
                    header = file.readline()
                    res = header.strip("\n").split(delimiter)
                    #self.create_attribute_file(int(res[0]), int(res[1]))
                #m = 0
                #d = {}
                for line in file:
                    res = line.strip("\n").split(delimiter)
                    if (len(res) > 1):
                        if(remove_weights):
                            f.write(res[0] + "\t" + res[1] + "\n")
                        else:
                            f.write(line.replace(delimiter, "\t"))
                        #if (not header):
                            #m += 1
                            #d[res[0]] = 0
                            #d[res[1]] = 0
                #if (not header):
                    #n = len(d.keys())
                    #self.create_attribute_file(int(n), int(m))

    def direct_edges(self):
	#Duplicate the edges of self.graph_file_name, the new edges will have the same weights as the original, if exists
	#Also updates attributes file
        new_graph_name = self.graph_file_name.split(".")[0] + "_dir.txt"
        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    f2.write(line)
                    res = line.strip("\n").split("\t")
                    if (len(res) > 1):
                        temp = res[0]
                        res[0] = res[1]
                        res[1] = temp
                        f2.write(self.build_row(res))

        with open(self.attribute_file_name, "r", encoding=self.encoding) as f3:
            n = f3.readline().split("=")[1].strip("\n")
            m = f3.readline().split("=")[1].strip("\n")

        with open(self.attribute_file_name, "w", encoding=self.encoding) as f4:
            f4.write("n=" + n + "\n")
            f4.write("m=" + str(2 * int(m)) + "\n")
            f4.close()

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_graph_name)

    def add_default_weights(self):
    #Add to each edge (u,v) the weight 1/d_in(v)
    #Will delete already existing weights
        d = {}
        with open(self.graph_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                res = line.strip("\n").split("\t")
                if (len(res) > 1):
                    key = res[1]
                    if (key not in d):
                        d[key] = 0
                    d[key] = d[key] + 1

        temp_graph = self.graph_file_name.split(".")[0] + "_temp.txt"
        with open(self.graph_file_name, "r", encoding=self.encoding) as f:
            with open(temp_graph, "w", encoding=self.encoding) as f2:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (len(res) > 1):
                        key = res[1]
                        f2.write(res[0] + res[1] + "\t" + str(1 / float(d[key])) + "\n")


        with open(temp_graph, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                        for line in f:
                            file.write(line)
        os.remove(temp_graph)

    def remove_nodes_by_property(self, property_name, value, default_weights=False):
	#Removes from graph and nodes files all nodes with property <property name> matching an element in <value>
	#<value> must be of type list/dict/set or a single element such as string/int...
	#if default_weights is set to True, at the end the weights will be normalized such that the total weight of ingoing edges to vertex v is 1

        # Remove from nodes file
	if(type(value) != list and type(value) != dict and type(value) != set):
		value = [value]
        removed_nodes = {}
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_rm.txt"
        f3 = open(self.nodes_file_name.split(".")[0] + "_del.txt", "w", encoding=self.encoding)

        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:

                ind = 0
                for i in range(len(self.node_properties)):
                    if (self.node_properties[i] == property_name):
                        ind = i
                        break

                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    if (res[ind] not in value):
                        f2.write(line)
                    else:
                        removed_nodes[res[0]] = 0
                        f3.write(line)

        f3.close()

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

        # Remove from graph file
        new_graph_name = self.graph_file_name.split(".")[0] + "_rm.txt"

        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                removed_edges = 0
                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    if (res[0] not in removed_nodes) and (res[1].strip("\n") not in removed_nodes):
                        f2.write(line)
                    else:
                        removed_edges += 1
                        if (res[0] in removed_nodes):  # res[0] was in both nodes and the graph
                            removed_nodes[res[0]] = 1
                        if (res[1].strip("\n") in removed_nodes):  # res[1] was in both nodes and the graph
                            removed_nodes[res[1]] = 1

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)

        os.remove(new_graph_name)

        f3 = open(self.attribute_file_name, "r")
        n = int(f3.readline().split("=")[1].strip("\n"))
        m = int(f3.readline().split("=")[1].strip("\n"))
        f3.close()

        n -= len({key: val for key, val in removed_nodes.items() if val == 1}.keys())
        m -= removed_edges
        self.create_attribute_file(n, m)

        if (default_weights):
	     self.normalize_existing_weights()

    def replace_nodes_Ids(self, d):
	#Replace the id of node x with d[int(x.id)], where d maps int to int
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_changed.txt"
        deleted_nodes = 0
        deleted_edges = 0
        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (int(res[0]) in d):
                        res[0] = str(d[int(res[0])])
                        f2.write(self.build_row(res))
                    else:
                        deleted_nodes += 1

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

        new_graph_name = self.graph_file_name.split(".")[0] + "_changed.txt"

        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (int(res[0]) not in d) or (int(res[1]) not in d) :
                        deleted_edges += 1
                    else:
                        res[0] = str(d[int(res[0])])
                        res[1] = str(d[int(res[1])])
                        f2.write(self.build_row(res))

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_graph_name)

        f3 = open(self.attribute_file_name, "r")
        n = int(f3.readline().split("=")[1].strip("\n"))
        m = int(f3.readline().split("=")[1].strip("\n"))
        f3.close()

        n -= deleted_nodes
        m -= deleted_edges
        self.create_attribute_file(n, m)

    def build_protected_group_dict(self, is_protected):
	#builds dict mapping old id to new id such that the protected group will appear first
        d = {}
        protected = 0
        non_protected = 0
        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                res = line.strip("\n").split("\t")
                if (is_protected(res)):
                    protected += 1
                    d[int(res[0])] = (-1) * protected
                else:
                    d[int(res[0])] = non_protected
                    non_protected += 1
        d = {k: (v + protected) for (k, v) in d.items()}
        return protected, d

    def change_protected_Ids(self, is_protected):
	#Change the ids such that the protected group will appear first
        protected_users_num, new_Ids = self.build_protected_group_dict(is_protected)
        self.replace_nodes_Ids(new_Ids)
        with open(self.files_dir_name + "/protected_group.txt", "w", encoding=self.encoding) as f:
            print 'R=', str(protected_users_num)
            f.write(u"R=" + str(protected_users_num))

    def saveSeedSet(self, seeds):
	#Saves array of strings representing seeds (e.g. names or ids) in a file called "seed_set.txt", seperated by white-space
        with open(self.files_dir_name + "/seed_set.txt", "w", encoding=self.encoding) as f:
		f.write(unicode(seeds[0]))
		for seed in seeds[1:]:
 			f.write(unicode(" " + seed))

    def create_lt(self):
	#Create graph_lt.inf as required by IMM (it's a copy of graph.txt with a different name)
        shutil.copy2(self.graph_file_name, self.graph_file_name.split(".")[0] + "_lt.inf")

    def create_ic(self):
	#Create graph_ic.inf as required by IMM (it's a copy of graph.txt with a different name)
        shutil.copy2(self.graph_file_name, self.graph_file_name.split(".")[0] + "_ic.inf")

    def create_input_files(self, nodes_gen, graph_file_name, delimiter=None, header=True, encoding="utf-8", directed=True, add_weights= False, lt=True, ic=True):
	#This function brings together previous function to allow the creation of all IMM input files in one go.
	#Arguments must adhere to the requirements of the previous functions
        os.mkdir(self.files_dir_name)
        shutil.copy2(graph_file_name, self.files_dir_name + "/original_graph.txt")
        self.create_nodes(nodes_gen)
        self.format_graph(graph_file_name, delimiter, header, encoding, add_weights)
        if(not directed):
            self.direct_edges()
        if(add_weights):
            self.add_default_weights()
        if(lt):
            self.create_lt()
        if (ic):
            self.create_ic()

    def add_property_by_property(self, new_property_name, d, property_name):
	#Add a new property to all nodes, <new_property_name> specifies the new property, <property_name> specifies an already existing property
	# d is a dict mapping: node.property_name |-----> node.new_property_name

        # Update nodes file
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_1.txt"
        self.node_properties.append(new_property_name)

        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:

                ind = 0
                for i in range(len(self.node_properties)):
                    if (self.node_properties[i] == property_name):
                        ind = i
                        break

                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    node = res[ind]
                    if(node in d):
                        f2.write(line.strip("\n") + "\t" + d[node] + "\n")
                    else:
                        f2.write(line.strip("\n") + "\t" + new_property_name + "\n")

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

    def remove_property(self, property_name):
	#Remove property from all nodes, <property_name> specifies the property to be removed
        # Update nodes file
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_1.txt"

        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:

                ind = 0
                for i in range(len(self.node_properties)):
                    if (self.node_properties[i] == property_name):
                        ind = i
                        break

                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    del res[ind]
                    node = self.build_row(res)
                    f2.write(node)

        self.node_properties.remove(property_name)

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

    def get_attribute_values(self, property_name):
	#Returns a set with all values attained by the property <property_name>
	#Meaning, x in get_attribute_values(self, property_name) iff exists node n with n.property_name = x
        values = set()
        ind = 0
        for i in range(len(self.node_properties)):
            if (self.node_properties[i] == property_name):
                ind = i
                break

        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                val = line.strip("\n").split("\t")[ind]
                values.add(val)

        return values

    def get_attribute_histogram(self, property_name):
	#Returns a dict mapping all values attained by the property <property_name> to how many times are they attained
	#Meaning, k = get_attribute_histogram(self, property_name)[x] iff exists nodes n_1,...,n_k with n_i.property_name = x
        hist = {}
        ind = 0
        for i in range(len(self.node_properties)):
            if (self.node_properties[i] == property_name):
                ind = i
                break

        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                val = line.strip("\n").split("\t")[ind]
                if val not in hist:
                    hist[val] = 0
                hist[val] = hist[val] + 1

        return hist

    def get_attribute_values_with_selector(self, property_name, selector_property_name, selector_nodes):
	#Returns a set with all values attained by the property <property_name> looking only at nodes x such that x.selector_property_name in selector_nodes
        values = {}
        ind = 0
        for i in range(len(self.node_properties)):
            if (self.node_properties[i] == property_name):
                ind = i
                break

        select_ind = 0
        for i in range(len(self.node_properties)):
            if (self.node_properties[i] == selector_property_name):
                select_ind = i
                break


        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
		if(line.strip("\n").split("\t")[select_ind] in selector_nodes):
                	val = line.strip("\n").split("\t")[ind]
                	values[line.strip("\n").split("\t")[select_ind]] = val

        return values

    def get_protected_group_size(self):
	#Returns protected group size, from the file, not by recalculating it
        with open(self.protected_group_file_name, "r", encoding=self.encoding) as f:
            line = f.readlines()
	    return float(line[0].strip("\n").split("=")[1])

    def normalize_existing_weights(self):
	#Normalize weights such that total weight from edges ingoing to vertex v is 1
    	d_in = {}

    	with open(self.graph_file_name, "r", encoding="utf-8") as f:
        	for line in f:
            		res = line.strip("\n").split("\t")
            		if res[1] not in d_in:
                		d_in[res[1]] = 0
            		d_in[res[1]] += float(res[2])

    	with open(self.graph_file_name, "r", encoding="utf-8") as f:
        	with open(self.graph_file_name.split(".")[0] + "_w.txt", "w", encoding="utf-8") as f2:
            		for line in f:
                		res = line.strip("\n").split("\t")
                		f2.write(res[0] + "\t" + res[1] + "\t" + str(float(res[2]) / d_in[res[1]]) + "\n")

    	with open(self.graph_file_name, "w", encoding="utf-8") as f:
        	with open(self.graph_file_name.split(".")[0] + "_w.txt", "r", encoding="utf-8") as f2:
            		for line in f2:
               			f.write(line)
   	os.remove(self.graph_file_name.split(".")[0] + "_w.txt")

    def create_attribute_file_from_scratch(self):
	#Create attributes.txt file as required by IMM, by counting lines in graph.txt and in nodes.txt
        n = 0
        m = 0
        with open(self.nodes_file_name, "r", encoding=self.encoding) as file:
            for line in file:
                n += 1
        with open(self.graph_file_name, "r", encoding=self.encoding) as file:
            for line in file:
                m += 1
        with open(self.attribute_file_name, "w", encoding=self.encoding) as file:
            file.write(unicode("n=" + str(n) + "\n"))
            file.write(unicode("m=" + str(m) + "\n"))

    def build_consecutive_id_dict(self):
	#Creates a dict mapping old id to new id such that ids wil be consecutive
    	d = {}
    	i = 0
    	with open(self.nodes_file_name, "r", encoding="utf-8") as f:
        	for line in f:
            		res = line.strip("\n").split("\t")
            		if(len(res) >= 1):
                		d[int(res[0])] = i
                		i += 1
    	return d

    def create_consecutive_ids(self):
	#Changes node ids such that new ids wil be consecutive
	d = self.build_consecutive_id_dict()
	self.replace_nodes_Ids(d)

