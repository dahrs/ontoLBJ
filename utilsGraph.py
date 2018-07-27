#!/usr/bin/python
#-*- coding:utf-8 -*-

import json, codecs, random, community
from tqdm import tqdm
import pandas as pd
import numpy as np
import networkx as nx

import utilsOs, utilsString


##################################################################################
#GRAPH FILES MAKER (EDGE_LIST and NODE_LIST) in O(n^2) where n is the nb of skills
##################################################################################


def edgeListTemp(pathInput, pathTempFile, lowercaseItAll=False):
	'''
	takes the linkedin data and makes a temporary file that is an edge list of (columns):
		- jobNode(source)
		- skillNode(target)
	It's only a temporary file because we still need to erase doubles, 
	to make the weight (count coreference of skills) and count how 
	many times the job titles appeared
	'''
	#we open a temp file
	outputTempFile = utilsOs.createEmptyFile(pathTempFile) #don't specify that the headerLine is 'Source \t Target'

	with open(pathInput) as jsonFile:
		#we read the original json file line by line
		jsonData = jsonFile.readline()
		while jsonData:
			jsonDict = json.loads(jsonData)
			#if there are experiences
			if u'experiences' in jsonDict:
				#reliable job-skill correspondence if we only have one job title
				if len(jsonDict[u'experiences']) == 1:
					if u'function' in jsonDict[u'experiences'][0]:
						jobTitle = jsonDict[u'experiences'][0][u'function']
						if lowercaseItAll != False:
							jobtitle = jobTitle.lower()
						if u'skills' in jsonDict:
							for skillDict in jsonDict[u'skills']:
								skill = skillDict[u'name']
								if lowercaseItAll != False:
									skill = skill.lower()
								outputTempFile.write(u'{0}\t{1}\n'.format(jobTitle, skill))
								#outputTxt.write(u'{0}\t{1}\n'.format(jobTitle, skill))
			jsonData = jsonFile.readline()
	#closing the file	
	outputTempFile.close()


def edgeListDump(pathTempFile, pathOutput):
	'''
	opens the temp file containing the extracted linkedin data and makes an edge list of (columns):
		- jobNode(source)
		- skillNode(target)	
		- weight(coreference) 
		- nbOfTimesJobTitleAppeared
	
	[in a further function we might want to add keywords (non stop-words most common tokens for each jobtitle)]
	'''
	skillCorefDict = {}
	jobTitleCorefDict = {}
	lastJobTitle = None
	lineSet = set()

	#open the output file
	outputTxt = utilsOs.createEmptyFile(pathOutput, headerLine=u'Source\tTarget\tWeight\tWeight1')
	#we browse the data once to get the weight and nbOfTimesJobTitleAppeared data

	with codecs.open(pathTempFile, u'r', encoding=u'utf8') as tempData:
		dataLine = tempData.readline()
		while dataLine:
			dataList = dataLine.replace(u'\n', u'').split(u'\t')
			if len(dataList) > 1:
				#count the skills coref
				skillCorefDict[dataList[1]] = skillCorefDict.get(dataList[1], 0) + 1
				#count the repetitions of job titles
				if dataList[0] != lastJobTitle:
					jobTitleCorefDict[dataList[0]] = jobTitleCorefDict.get(dataList[0], 0) + 1
					lastJobTitle = dataList[0]
				#we add the line to the set
				lineSet.add(dataLine)
			###else:
			###	print(111111, dataList)
			#get to the next line
			dataLine = tempData.readline()
	#we browse the data a second time to dump it
	for dataLine in lineSet:
		dataList = dataLine.replace(u'\n', u'').split(u'\t')
		#we write 2 possible edge weights: skill coreference & skill coreference*jobtitle coreference
		outputTxt.write(u'{0}__s\t{1}__t\t{2}\t{3}\n'.format(dataList[0], dataList[1], skillCorefDict[dataList[1]], skillCorefDict[dataList[1]]*jobTitleCorefDict[dataList[0]]))

	#closing the file	
	outputTxt.close()


def nodeListIdType(pathEdgeListFile, pathNodeFileOutput):
	'''
	opens the temp file containing the extracted linkedin data and makes a node list of (columns):
		- id(same as label)
		- label(jobTitle / skill node)	
		- type(source or target; 2 for source 1 for target) #the job title is always the source, the skill is always the target
	'''
	jobTitleSet = set()
	skillSet = set()

	#open the output file
	outputTxt = utilsOs.createEmptyFile(pathNodeFileOutput, headerLine=u'Id\tLabel\tNodeType')

	with codecs.open(pathEdgeListFile, u'r', encoding=u'utf8') as edgeData:
		dataLine = edgeData.readline()
		while dataLine:
			dataList = dataLine.replace(u'\n', u'').split(u'\t')
			if len(dataList) > 1:
				#add to the jobTitle (source) set
				jobTitleSet.add(dataList[0])
				#add to the skill (target) set
				skillSet.add(dataList[1])
			###else:
			###	print(111111, dataList)
			#get to the next line
			dataLine = edgeData.readline()
	#browse the data sets to dump them
	for jobTitle in jobTitleSet:
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(jobTitle, jobTitle.replace(u'__s', u''), 2)) #id's '_s' means 'source', 2 means 'source'
	for skill in skillSet:
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(skill, skill.replace(u'__t', u''), 1)) #id's '_t' means 'target', 1 means 'target'


##################################################################################
#GET ADJACENCY
##################################################################################

def getNodeAdjacency(nodeName, edgeList, bothWays=True): ###########################################################
	'''
	given a node, searchs for the adjacent nodes to it
	'''
	adjacencyList = []
	#add all nodes adjacent to the source nodes
	for edge in edgeList:
		if edge[0] == nodeName:
			adjacencyList.append(edge[1])
	#if the nodeName is not a source node, browse all the target nodes and append the source nodes to the adjacency list
	#or if bothways is true, it means the graph is not directed so there is no difference between source and target nodes
	if len(adjacencyList) == 0 or bothways == True:
		for edge in edgeList:
			if edge[1] == nodeName:
				adjacencyList.append(edge[0])
	return adjacencyList


##################################################################################
#RANDOM WALK
##################################################################################

def randomWalk(edgeDf, nodeDf):
	'''
	takes 2 pandas dataframes as main arguments:
	an edgeList and nodeList with the following columns:
	- edge list:
		- Source, Target, Weight, etc.
	- node list:
		- Id, Label, etc.
	'''
	#get a random node where to begin the random walk
	#get the adjacency list of the randomly chosen node
	#randomly choose if we want to move or not
		#randomly choose where we want to move, if we want to move
	return


##################################################################################
#MODULARITY
##################################################################################

def nodeDfCleaner(nodeDf):
	''' cleans all the node dataframe from NaN values in the modularity class '''
	#return nodeDf.loc[nodeDf[u'modularity_class'] != float(u'nan')]
	return nodeDf.dropna()


def modularizeLouvain(edgeFilePath, nodeFilePath, outputFilePath=None):
	'''
	uses the original code of the louvain algorithm to give modularity to a graph
	downloaded from https://github.com/taynaud/python-louvain
	documentation at: http://python-louvain.readthedocs.io/en/latest/api.html
	official website: https://perso.uclouvain.be/vincent.blondel/research/louvain.html
	'''
	#open the edge list as a networkx graph
	graph = nx.read_weighted_edgelist(edgeFilePath, delimiter='\t')
	#compute the best partition
	dendrogram = community.generate_dendrogram(graph, weight='weight')
	dendroBestPartitionDict = community.partition_at_level(dendrogram, len(dendrogram)-1) #dendroBestPartitionDict = community.best_partition(graph)
	#open the node list as a data frame	
	nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')
	#add a column to the node data frame so we can add the community values
	nodeDf[u'Community'] = np.nan	
	#add the community values to the node data frame
	nodeDf[u'Community'] = nodeDf[u'Id'].map(dendroBestPartitionDict)
	#making sure all 'modularity_class' NaN were deleted 
	nodeDf = nodeDfCleaner(nodeDf)
	#dumps the dataframe with the modularization data
	if outputFilePath != None:
		nodeDf.to_csv(outputFilePath, sep='\t')
	return nodeDf, dendrogram


def fillBagOfWords(bowSet, jobTitleList, occupationsUkDf, occupationsUsDf):
	'''
	Takes an empty of full set and fills it with the job title and description bag of words
	'''
	#adding the job titles to the bag of words
	for jobTitle in jobTitleList:
		bowSet = bowSet.union(set(utilsString.tokenizeAndExtractSpecificPos(jobTitle, [u'n', u'np', u'j'], caseSensitive=False, eliminateEnStopwords=True)))
	#adding the description(s) to the bag of words
	selectiveEscoDf = occupationsUkDf.loc[occupationsUkDf['preferredLabel'].isin(jobTitleList)]
	if selectiveEscoDf.empty:
		selectiveEscoDf = occupationsUsDf.loc[occupationsUkDf['preferredLabel'].isin(jobTitleList)]
		if selectiveEscoDf.empty:
			return bowSet
	for rowIndex, row in selectiveEscoDf.iterrows():
		#adding the description(s) to the bag of words
		bowSet = bowSet.union(set(utilsString.tokenizeAndExtractSpecificPos(row['description'], [u'n', u'np', u'j'], caseSensitive=False, eliminateEnStopwords=True)))
	return bowSet


def getEscoBowByLevel(escoTree):
	'''
	starting at level 0 : the most abstract job title domain,
	we make a bag of words of the job titles and added descriptions 
	contained in the domain
	e.g., 	0: 		a0 : bow of a1+a2
					b0: bow of b1+b2
				1: 		a1: bow of a1 ...
						a2: bow of a2 ...
						b1: bow of b1 ...
						b2: bow of b2 ...
	'''
	from nltk.corpus import stopwords
	bowsDict = {0:{}, 1:{}, 2:{}, 3:{}}
	#open a dataframe of all occupation data, ready to extract the description
	occupationsUkDf = pd.read_csv(u'./001ontologies/ESCO/v1.0.2/occupations_en.csv')
	occupationsUsDf = pd.read_csv(u'./001ontologies/ESCO/v1.0.2/occupations_en-us.csv')
	#browsing the esco tree by hand to add the bow in the 4 levels	
	with codecs.open(u'./001ontologies/ESCO/v1.0.2/occupations_en.csv', u'r', encoding=u'utf8') as escoFileForDescription:
		#level 0
		for domain1digit, value1digit in escoTree.items():
			bow0 = set()
			#level 1
			for domain2digit, value2digit in value1digit.items():
				bow1 = set()
				#level 2
				for domain3digit, value3digit in value2digit.items():
					bow2 = set()
					#when the job titles are at level 3
					if type(value3digit) is list:
						bow2 = fillBagOfWords(bow2, value3digit, occupationsUkDf, occupationsUsDf)
					else:
						#level 3
						for domain4digit, value4digit in value3digit.items():
							bow3 = set()
							#when the job titles are at level 4
							bow3 = fillBagOfWords(bow3, value4digit, occupationsUkDf, occupationsUsDf)						
							#saving in the bow dict
							bowsDict[3][domain4digit] = bow3
							bow2 = bow2.union(bow3)
					#saving in the bow dict
					bowsDict[2][domain3digit] = bow2
					bow1 = bow1.union(bow2)
				#saving in the bow dict
				bowsDict[1][domain2digit] = bow1
				bow0 = bow0.union(bow1)
			#saving in the bow dict
			bowsDict[0][domain1digit] = bow0
	return bowsDict


def getOntologyBowByCommunity(nodeDf):
	'''
	makes a bag of words composed of the job title names
	for each community in the ontology
	'''
	communityBagOfWords = {}
	communitiesSet = set(nodeDf['Community'].tolist())
	for community in communitiesSet:
		bowSet = set()
		#get a reduced df where the community column corresponds to the community value
		communityDf = nodeDf.loc[nodeDf[u'Community'] == community]
		#make the bag of words set
		jobTitleList = communityDf['Label'].tolist()
		for jobTitle in jobTitleList:
			bowSet = bowSet.union(set(utilsString.naiveRegexTokenizer(jobTitle, caseSensitive=False, eliminateEnStopwords=True)))
		#SHOULD WE ADD THE LINKEDIN PROFILES PITCH ??????
		#save the bag of words to the dict
		communityBagOfWords[community] = set(bowSet)
	return communityBagOfWords


def getCommunityNameInferences(nodeDf, outputFilePath):
	''' 
	using a bag of words on jobtitles of the same community and on
	job titles and descriptions from existing ontologies (ESCO)
	we estimate what is the name of the community domain
	'''
	inferencesDict = {}
	#bag of words of the esco ontology
	escoTree = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/escoTree.json')
	escoTreeBagOfWords = getEscoBowByLevel(escoTree)
	#bag of words of the communities in our ontology
	communityBagOfWords = getOntologyBowByCommunity(nodeDf)
	#add an empty column
	nodeDf[u'Infered_Community_Name'] = np.nan
	#comparing intersection between esco bow and the communities bow
	for community, communityBow in communityBagOfWords.items():
		#reset values of best intersection
		bestIntersection = {u'result': 0.0, u'set': None, u'name': u'00000000___'}
		for nb in reversed(range(1, 4)):
			for escoDomain, escoBow in escoTreeBagOfWords[nb].items():
				#we intersect the 2 bag of words
				bowIntersection = communityBow.intersection(escoBow)
				#we evaluate if we are at the same level in the esco taxonomy the score we need to replace the best intersection 
				#is > than the precedent, if we are one level upper, then the needed score is twice the best intersection score
				if len(bestIntersection[u'name'].split(u'___')[0]) == len(escoDomain.split(u'___')[0]):
					multiplier = 1.0
				else:
					multiplier = (4.1 - (nb * 1.2))
				#if the score is greater, we replace the previous best intersection with the new intersection
				if len(bowIntersection) > bestIntersection['result']*multiplier or bestIntersection['result'] == 0.0:
					bestIntersection[u'result'] = len(bowIntersection)
					bestIntersection[u'set'] = bowIntersection
					bestIntersection[u'name'] = escoDomain
		#saving the information
		inferencesDict[community] = bestIntersection
		nodeDf[u'Infered_Community_Name'].loc[nodeDf[u'Community'] == community] = str(bestIntersection['name'])
	#dump to file
	nodeDf.to_csv(outputFilePath, sep='\t')
	return inferencesDict


def getModularityPercentage(nodeFilePathWithModularity, communityColumnHeader=u'Community'):
	'''
	opens the node list tsv file and calculates the percentage of communities
	'''
	communityDict = {}
	resultDict = {}
	nodeDf = pd.read_csv(nodeFilePathWithModularity, sep=u'\t')

	#remaking a community dict
	for nodeIndex, nodeRow in nodeDf.iterrows():
		modCommunity = nodeRow[communityColumnHeader]
		if modCommunity in communityDict:
			communityDict[modCommunity].append(nodeRow[u'Label'])
		else:
			communityDict[modCommunity] = [nodeRow[u'Label']]
	#calculation
	for idKey, communityValue in communityDict.items():
		resultDict[idKey] = (float(len(communityValue)) / float(len(nodeDf)))
	#printing in order
	for v,k in (sorted( ((v,k) for k,v in resultDict.items()), reverse=True)):
		print(44444444444444444444444, 'community {0} normalized score: {1}'.format(k, v))
		#if v > 0.01:
		#	print(55555555555, communityDict[k])
	return resultDict


##################################################################################
#ONTOLOGY CLEANING AND TRIMMING
##################################################################################

def ontologyContentCleaning():
	''''''


def remove1DegreeNodes(dictA, dictB):
	'''
	recursive function to remove all the less core-connected 
	nodes from the dicts representing the graph
	'''
	aOriginalSize = len(dictA)
	bOriginalSize = len(dictB)
	#remove job titles of degree 1 (with only one skill)
	for aKey, aList in dict(dictA).items():
		#if there is one (or less) skill for that job title
		if len(aList) <= 1:
			#to maintain consistency, delete the job title from the skill to jobs dict
			for bElem in list(aList):
				#delete the job title from the skill to jobs dict
				dictB[bElem].remove(aKey)
				#remove the keys in the dict with an empty list as value
				if len(dictB[bElem]) == 0:
					del dictB[bElem]
			#delete the dict entry from the job to skills dict
			del dictA[aKey]
	if len(dictA) != aOriginalSize and len(dictB) != bOriginalSize:
		dictB, dictA = remove1DegreeNodes(dictB, dictA)
	return dictA, dictB



def ontologyStructureCleaning(edgeFilePathInput, nodeFilePathInput, edgeFilePathOutput=None, nodeFilePathOutput=None):
	'''
	given an ontology (edge list and node list), removes:
		- all communities corresponding to less than 1% of the node
		- all independent and isolated skills and job titles:
			- all skills connected to only 1 job title
			- all job titles with only one skill
			- all job titles (and skills) whose skills are not connected to any other job titles
	'''
	edgeDf = pd.read_csv(edgeFilePathInput, sep=u'\t')
	nodeDf = pd.read_csv(nodeFilePathInput, sep=u'\t')

	#remove communities corresponding to less than 1% of the node
	communitiesSet = set(nodeDf['Community'].tolist())
	copyCommunitiesSet = list(communitiesSet)
	for communityId in copyCommunitiesSet:
		bowSet = set()
		#get a reduced df where the community column corresponds to the community id value
		communityDf = nodeDf.loc[nodeDf[u'Community'] == communityId]
		if len(communityDf)/len(nodeDf) < 0.01:
			communitiesSet.remove(communityId)
	#save the trimmed df as the new node df
	nodeDf = nodeDf.loc[nodeDf[u'Community'].isin(list(communitiesSet))]
	#make a dict of jobtitle to skills and a dict of skill to jobtitles
	jToSkillsDict = {}
	sToJobsDict = {}
	emptyList = []
	for edgeIndex, edgeRow in edgeDf.iterrows():
		jToSkillsDict[edgeRow[u'Source']] = list(set(jToSkillsDict.get(edgeRow[u'Source'], list(emptyList)) + [edgeRow[u'Target']]))
		sToJobsDict[edgeRow[u'Target']] = list(set(sToJobsDict.get(edgeRow[u'Target'], list(emptyList)) + [edgeRow[u'Source']]))
	#remove independent and isolated skills and job titles
	jToSkillsDict, sToJobsDict = remove1DegreeNodes(jToSkillsDict, sToJobsDict)
	#save the trimmed data frames as the new data frames
	nodeDf = nodeDf.loc[nodeDf[u'Id'].isin( list(jToSkillsDict.keys())+list(sToJobsDict.keys()) )]
	edgeDf = edgeDf.loc[edgeDf[u'Source'].isin(list(jToSkillsDict.keys())) & edgeDf[u'Target'].isin(list(sToJobsDict.keys()))]
	#dumping the data frames
	if edgeFilePathOutput != None:
		edgeDf.to_csv(edgeFilePathOutput, sep='\t')
	if nodeFilePathOutput != None:
		nodeDf.to_csv(nodeFilePathOutput, sep='\t')
	return edgeDf, nodeDf




	


##################################################################################
#ONTOLOGY EVALUATION METRICS
##################################################################################

def ontoQA():
	'''
	given an ontology (edge list and node list) it calculates the ontoQA score
	'''
	#RR - relationship richness
	#inheritance relationship = class-subclass relationship

	#IR - inheritance richness
	#

	#attribute richness
	#class richness
	#class connectivity 
	#class importance
	#cohesion
	#relationship richness




edgeFilePathInput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListWeight.tsv'
nodeFilePathInput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListModularityInfered.tsv'
edgeFilePathOutput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListWeightCleanedLvl1.tsv'
nodeFilePathOutput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListModularityInferedCleanedLvl1.tsv'
ontologyStructureCleaning(edgeFilePathInput, nodeFilePathInput, edgeFilePathOutput, nodeFilePathOutput)