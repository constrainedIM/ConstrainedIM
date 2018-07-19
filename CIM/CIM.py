

from IMMDataParser import IMMDataParser
import json, subprocess, os, shutil, time

def printArgs(args):
	print 'k = ', args['k']
	print 't = ', args['t']
	print 'constraint: ',args['constraint'] 
	print 'network: ', args['network'] #give full path for the network
#example of usage of different properties
#{u'name': u'age', u'value': [u'below', u'40']}
#{u'name': u'gender', u'value': [u'f']}
#{u'name': u'country', u'value': [u'India']}
#constraint = ['overall', 'protected']
#graph name - directory file name

def updateProtectedSet(protected_set_array, graph_name, properties):
	protected_set_dict = parseProtectedArray(protected_set_array)
	isProtected = create_is_protected(protected_set_dict, properties)
	parser = IMMDataParser("IMM_files/" + graph_name, properties )
	parser.change_protected_Ids(isProtected)
	parser.create_lt()
	parser.create_ic()
	print("------------------------ finished protected group ------------------------")

def parseProtectedArray(protected_set_array): # NOT DONE
	#We assume correctness in form input, meaning values make sense and don't contradict each other
	#Also we assume that not all possible values have been chosen, e.g. no one chooses both "Male" and "Female" for gender
	protected_set_dict = {}
	for d in protected_set_array:
		if(d['name'] == "gender"):
			protected_set_dict[d['name']] = [d["value"][0]]

		if(d['name'] == "country"):
			if(not (d['name'] in protected_set_dict )):
				protected_set_dict[d['name']] = []
			protected_set_dict[d['name']].append(d["value"][0])

		if(d['name'] == "age" or  d['name'] == "h-index"):
			if(not (d['name'] in protected_set_dict )):
				protected_set_dict[d['name']] = [0, float("Inf")]
			if(d['value'][0] == "below"):
				protected_set_dict[d['name']][1] = int(d['value'][1]) - 1;
			if(d['value'][0] == "above"):
				protected_set_dict[d['name']][0] = int(d['value'][1]) + 1;
			if(d['value'][0] == "exactly"):
				protected_set_dict[d['name']] = [int(d['value'][1]), int(d['value'][1])]

	return protected_set_dict

def isProtected_with_dict(node, protected_set_dict,attr):
	#We assume that every node is given as an array of attributes: ["Id", "name", "country", "h-index", "age", "gender"]


	node = {attr[i]: node[i] for i in range(len(attr))}
	for attr_name in protected_set_dict.keys():
			if(attr_name == u"gender" or attr_name == u"country"):
				if(str(node[attr_name]) not in str(protected_set_dict[attr_name])):
					return False
			else:
				if(float(node[attr_name]) > float(protected_set_dict[attr_name][1]) or float(node[attr_name]) < float(protected_set_dict[attr_name][0])):
					return False
	return True

def create_is_protected(protected_set_dict,attr):
	return lambda node : isProtected_with_dict(node, protected_set_dict,attr)

#run regular IMM algorithm
def runIMM(k, graph_name):

	with open("IMM_res.txt", "w") as f:
		proc = subprocess.Popen(["./IMM_files/imm_discrete", "-dataset", graph_name + "/","-k",  k, "-model", "LT", "-epsilon", "0.1"], stdout=f) # for now we run with epsilon=0.1, model=LT
		proc.wait()

	with open("IMM_res.txt", "r") as f:
		with open("IMM_seed.txt", "w") as f2:
			for line in f:
				if "g.seedSet" in line:
					f2.write(line.split("=")[1])
					S = line.strip("\n").split("=")[1].split(" ")[:-1]
				if "opt_lower_bound" in line and not "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					opt_lb = line.strip("\n").split("=")[1]
				if "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					protected_opt_lb = line.strip("\n").split("=")[1]

	return [S, float(opt_lb), float(protected_opt_lb)]



def getIMMAns():
	with open("IMM_res.txt", "r") as f:
		with open("IMM_seed.txt", "w") as f2:
			for line in f:
				if "g.seedSet" in line:
					f2.write(line.split("=")[1])
					S = line.strip("\n").split("=")[1].split(" ")[:-1]
				if "opt_lower_bound" in line and not "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					opt_lb = line.strip("\n").split("=")[1]
				if "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					protected_opt_lb = line.strip("\n").split("=")[1]

	return [S, float(opt_lb), float(protected_opt_lb)]



def runProtectedIMM(k, graph_name):
	with open("ProtectedIMM_res.txt", "w") as f:
		proc = subprocess.Popen(["./IMM_files/protected_imm_discrete", "-dataset", graph_name + "/", "-k",  k, "-model", "LT", "-epsilon", "0.1"], stdout=f)# for now we run with epsilon=0.1, model=LT
		proc.wait()

	with open("ProtectedIMM_res.txt", "r") as f:
		with open("ProtectedIMM_seed.txt", "w") as f2:
			for line in f:
				if "g.seedSet" in line:
					f2.write(line.split("=")[1])
					S = line.strip("\n").split("=")[1].split(" ")[:-1]
				if "opt_lower_bound" in line and not "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					opt_lb = line.strip("\n").split("=")[1]
				if "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					protected_opt_lb = line.strip("\n").split("=")[1]


	return [S, float(opt_lb), float(protected_opt_lb)]
	

def getProtectedIMMans():
	with open("ProtectedIMM_res.txt", "r") as f:
		with open("ProtectedIMM_seed.txt", "w") as f2:
			for line in f:
				if "g.seedSet" in line:
					f2.write(line.split("=")[1])
					S = line.strip("\n").split("=")[1].split(" ")[:-1]
				if "opt_lower_bound" in line and not "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					opt_lb = line.strip("\n").split("=")[1]
				if "protected_opt_lower_bound" in line:
					f2.write(line.split("=")[1])
					protected_opt_lb = line.strip("\n").split("=")[1]


	return [S, float(opt_lb), float(protected_opt_lb)]


def getInf(k, graph_name):
	with open("Inf_res.txt", "w") as f:
		proc = subprocess.Popen(["./IMM_files/inf_imm_discrete", "-dataset", graph_name + "/", "-k",  k, "-model", "LT", "-epsilon", "0.1"], stdout=f)# for now we run with epsilon=0.1, model=LT
		proc.wait()

	with open("Inf_res.txt", "r") as f:
		for line in f:
			if "opt_lower_bound" in line and not "protected_opt_lower_bound" in line:
				opt_lb = line.strip("\n").split("=")[1]
			if "protected_opt_lower_bound" in line:
				protected_opt_lb = line.strip("\n").split("=")[1]
	
	return [float(opt_lb), float(protected_opt_lb)]




def runIMBalanced(t, k, constraint, graph_name, protected_set_array):
	start_time = time.time()
	kp = round(float(t) * float(k), 0)
	kk = int(k) -  int(kp)
	if constraint == "overall":
		f1 = open("IMM_res.txt", "w") 
		f2 = open("ProtectedIMM_res.txt", "w")

		IMMproc = subprocess.Popen(["./IMM_files/imm_discrete", "-dataset", graph_name + "/","-k",  str(kp), "-model", "LT", "-epsilon", "0.1"], stdout=f1) # for now we run with epsilon=0.1, model=LT
		protectedIMMproc = subprocess.Popen(["./IMM_files/protected_imm_discrete", "-dataset",graph_name + "/", "-k",  str(k), "-model", "LT", "-epsilon", "0.1"], stdout=f2)# for now we run with epsilon=0.1, model=LT

		IMMproc.wait()
		protectedIMMproc.wait()

		f1.close()
		f2.close()
		
		IMMans = getIMMAns()
		protectedIMMans = getProtectedIMMans()
		
		
		S = IMMans[0] + protectedIMMans[0][:kk]

	else:

		f1 = open("IMM_res.txt", "w") 
		f2 = open("ProtectedIMM_res.txt", "w")

		IMMproc = subprocess.Popen(["./IMM_files/imm_discrete", "-dataset", graph_name + "/","-k",  str(k), "-model", "LT", "-epsilon", "0.1"], stdout=f1) # for now we run with epsilon=0.1, model=LT
		protectedIMMproc = subprocess.Popen(["./IMM_files/protected_imm_discrete", "-dataset", graph_name + "/", "-k",  str(kp), "-model", "LT", "-epsilon", "0.1"], stdout=f2)# for now we run with epsilon=0.1, model=LT

		IMMproc.wait()
		protectedIMMproc.wait()

		f1.close()
		f2.close()
		
		IMMans = getIMMAns()
		protectedIMMans = getProtectedIMMans()
		
		S = IMMans[0][:kk] + protectedIMMans[0]
	S = list(set(S))

	# handle |S| < k
	if len(S) < float(k):
	
		if constraint == "overall":
			i = 0
			while len(S) < float(k):
				if not protectedIMMans[0][i] in S:
					S.append(protectedIMMans[0][i])
				i = i + 1
			
		else:
			i = 0
			while len(S) < float(k):
				if not IMMans[0][i] in S:
					S.append(IMMans[0][i])
				i = i + 1	

	saveSeeds(S, graph_name)
	Inf = getInf(k, graph_name)
	return [S, Inf[0], Inf[1]]

def saveSeeds(seeds, graph_name):
	parser = IMMDataParser(graph_name, ["Id", "name", "country", "h-index", "age", "gender"])
	parser.saveSeedSet(seeds)



args = {'k': '20', 'constraint': u'protected',
		'protected_set_array': [{u'name': u'gender', u'value': [u'f']},{u'name': u'country', u'value': 'India'}],
		'network': u'dblp',
		't': '0.5','properties':["Id", "name", "country", "h-index", "age", "gender"]}
# ["Id", "gender", "country"], {u'name': u'country', u'value': [u'010']} facebook
# ["Id","age", "gender", "country"] , {u'name': u'gender', u'value': [u'f']},{u'name': u'age', u'value': ['above' ,u'50']}]  pokec
# ["Id", "name", "country", "h-index", "age", "gender"],{u'name': u'gender', u'value': [u'f']},{u'name': u'country', u'value': [u'India']}  dblp
print("------------------------ Args ------------------------")
printArgs(args)
updateProtectedSet(args['protected_set_array'], args['network'], args['properties'])
print("------------------------ IMM ------------------------")
IMMans = runIMM(args['k'], args['network'])
StandardIMSeeds = IMMans[0]
StandardIMUsers = float(IMMans[1])
protectedStandardIMUsers  = float(IMMans[2])
unprotectedStandardIMUsers = StandardIMUsers - protectedStandardIMUsers
print 'overall: ', StandardIMUsers, 'protected: ', protectedStandardIMUsers, 'non protected: ', unprotectedStandardIMUsers
print("------------------------ finished running IMM ------------------------")


print("------------------------ targeted IMM ------------------------")
protectedIMMans = runProtectedIMM(args['k'], args['network'])
TargetedIMSeeds = protectedIMMans[0]
TargetedIMUsers = float(protectedIMMans[1])
protectedTargetedIMUsers  = float(protectedIMMans[2])
unprotectedTargetedIMUsers = TargetedIMUsers - protectedTargetedIMUsers
print 'overall: ', TargetedIMUsers, 'protected: ', protectedTargetedIMUsers, 'non protected: ', unprotectedTargetedIMUsers
print("------------------------ finished running targeted IMM ------------------------")
	

print("------------------------ CIM------------------------")
IMBalancedans = runIMBalanced(args['t'], args['k'], args['constraint'], args['network'], args['protected_set_array'])
IMBalancedSeeds = IMBalancedans[0]
IMBalancedUsers = float(IMBalancedans[1])
protectedIMBalancedUsers  = float(IMBalancedans[2])
unprotectedIMBalancedUsers = IMBalancedUsers - protectedIMBalancedUsers
print 'overall: ', IMBalancedUsers, 'protected: ', protectedIMBalancedUsers, 'non protected:', unprotectedIMBalancedUsers
print("------------------------ finished running CIM ------------------------")
	

