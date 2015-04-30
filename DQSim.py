import numpy as np
import random



def import_dailies_list(target_file,delimiter="\t"):
	"""Imports a list of possible quests from file and returns a list of Quest objects"""
	with open(target_file) as fil:
		contents=fil.read().splitlines()
	contents=[i.split(delimiter) for i in contents]
	available_quests=[]
	for line in contents:
		available_quests.append(Quest(line[0],int(line[-1])))
	return(available_quests)

		
class Trial():
	"""Trial object that contains a QuestLog and tracks Earnings.
	
	Parameters:

		QuestList: List of all possible Quests.
	"""

	def __init__(self,QuestList):
		"""Creates a Trial instance. Contains list of possible Quests for assigning new QUests daily and for rerolling. Also tracks Earnings. Subclass this and overwrite RunAlgorithm with your own instructions and decision making logic."""
		self.QuestLog=QuestLog(QuestList)
		self.Earnings=0.0
	def GetEarnings(self):
		"""Returns the current Earnings value"""
		return(self.Earnings)
	def CompleteQuest(self,Quest):
		"""Complete a Quest. Adds value of Quest to Earnings and removes it from the QuestLog"""
		self.Earnings += Quest.value
		self.QuestLog.RemoveQuest(Quest)
	def GetQuestLog(self):
		"""Returns the QuestLog"""
		return(self.QuestLog)
	def GetNumberOfQuests(self):
		"""Return an integer specifying number of Quest objects currently in QuestLog"""
		return(len(self.GetQuestLog().GetQuests()))
	def GetQuests(self):
		"""Returns a list of Quest objects currently in the QuestLog"""
		return(self.GetQuestLog().GetQuests())
	def GetQuestLimit(self):
		"""Return an integer representing how many quests the quest log can hold"""
		return(self.GetQuestLog().GetQuestLimit())
	def RerollQuest(self,QueryQuest):
		"""Reroll the specified Quest object into a random other quest"""
		self.GetQuestLog().RerollQuest(QueryQuest)
	def Update(self):
		"""Performs the automatic daily things that happen. So far just adds a new Quest to the log."""
		self.QuestLog.AddQuest()
	def CompleteAll(self):
		"""Complete all remaining Quests in QuestLog. Usually done on the last day to clear the log."""
		for EachQuest in self.GetQuestLog().GetQuests():
			self.CompleteQuest(EachQuest)
	def RunAlgorithm(self):
		"""Runs whatever instructions you want to each day. Overwrite this in subclasses, and implement other instructions in this fuction for your own algorithm. By default will just complete all quests."""
		self.CompleteAll()


class Simulation():
	"""The simulation instantiates trials, runs them, and collects a list
	of earnings. Can then return the average and standard deviation.
	Automatically imports list of possible quests from QuestFile.
	
	Parameters:
		
		NumTrials: Number of Trials to run (integer).

		NumDays: Number of days to run each Trial for (integer).

		QuestFile: Tab delimited file containing data on all possible.

		Quests. Quest names should be in the first column, and quest values in the last column. 

		Algorithm: Which subclass of Trial should be used for this simulation. Uses basic Trial logic if not specified.

		verbose: If true, will print out contents of quest log each day.

	"""
	def __init__(self,NumTrials,NumDays,QuestFile,Algorithm=Trial,verbose=False):
		self.NumTrials=NumTrials
		self.NumDays=NumDays
		self.QuestList=import_dailies_list(QuestFile)
		self.Algorithm=Algorithm
		self.verbose=verbose

	
	def RunSim(self):
		"""Instantiates and runs the number of trials specified by NumTrials. Collects the earnings from each trial and then calculates average and standard deviation."""
		Earnings=[]
		for each in range(self.NumTrials):
			if (each+1)%10==0:
				print("Running Trial {} of {}".format(each+1,self.NumTrials))
			Earnings.append(self.RunTrial())
		return(np.mean(Earnings),np.std(Earnings))



	def RunTrial(self):
		"""Instantiates a trial subclass of type specified by Algorithm. Runs trial for number of days specified by NumDays, then returns average earnings per day."""
		CurrentTrial=self.Algorithm(self.QuestList)

		for Day in range(self.NumDays):
			CurrentTrial.Update()
			if self.verbose==True:
				print("Day {} start".format(Day+1))
				CurrentTrial.QuestLog.PrintQuestLog()
			CurrentTrial.RunAlgorithm()
			if Day != self.NumDays-1 and self.verbose ==True:
				print("Day {} after completing stuff".format(Day+1))
				CurrentTrial.QuestLog.PrintQuestLog()
		CurrentTrial.CompleteAll()
		if self.verbose ==True:
			print("Day {} after completing stuff".format(Day+1))
			CurrentTrial.QuestLog.PrintQuestLog()

		return(CurrentTrial.GetEarnings()/self.NumDays)

class KeepOneForty(Trial):
	"""Subclass of Trial. Algorithm: attempt to reroll a 40 gold Quest each day if it can. Will keep at most one 40 gold Quest at end of day, and complete all others. Intended for use with Hearthstone daily quests."""
	def Count40s(self):
		"""Returns the number of Quests with value 40."""
		count=0
		for EachQuest in self.QuestLog.GetQuests():
			if EachQuest.GetValue() ==40:
				count +=1
		return(count)
	def CompleteUnlessSole40(self):
		"""Completes all Quests except one 40 gold one to attempt a reroll tomorrow."""
		for EachQuest in self.GetQuestLog().GetQuests():
			if EachQuest.GetValue() !=40:
				self.CompleteQuest(EachQuest)
		while self.Count40s() >1 and len(self.GetQuestLog().GetQuests())!=0:
			self.CompleteQuest(self.GetQuestLog().GetQuests()[0])
	def RunAlgorithm(self):
		self.QuestLog.RerollA40()
		self.CompleteUnlessSole40()
	
class RerollAndClear(Trial):
	"""Subclass of Trial. Algorithm: attempts to reroll one 40 gold Quest, then clears all Quests"""
	def RunAlgorithm(self):
		self.QuestLog.RerollA40()
		self.CompleteAll()

class CompleteHighest(Trial):
	"""Subclass of Trial. Algorithm: waits till it has maximum number of Quests, then completes highest one each day"""
	def GetHighestValue(self):
		"""Returns the value of the most valuable Quest."""
		highest=0
		for EachQuest in self.GetQuestLog().GetQuests():
			if EachQuest.GetValue() > highest:
				highest=EachQuest.GetValue()
		return(highest)
	def CompleteHighestIfFull(self):
		"""If at maximum number of Quests, complete the highest value one."""
		if len(self.GetQuestLog().GetQuests()) == self.GetQuestLog().GetQuestLimit():
			HighestValue=self.GetHighestValue()
			for EachQuest in self.GetQuestLog().GetQuests():
				if EachQuest.GetValue() == HighestValue:
					self.CompleteQuest(EachQuest)
					break
	def RunAlgorithm(self):
		self.CompleteHighestIfFull()

class QuestLog(object):
	"""Containts a list of current Quests (Quests), and a list of possible Quests (QuestList).
	
	Parameters: 

		QuestList: List of all possible quests.
	"""
	def __init__(self,QuestList):
		self.Quests=[]
		self.QuestList=QuestList
		self.QuestLimit=3
	def PrintQuestList(self):
		"""Prints out all possible Quests."""
		for Quest in self.QuestList:
			print(Quest)
	def PrintQuestLog(self):
		"""Prints out the Quests currently in the QuestLog."""
		for Quest in self.Quests:
			print(Quest)
		if len(self.Quests) ==0:
			print("Quest Log is empty")
	def GetQuests(self):
		"""Returns the list of current Quests"""
		return(self.Quests)
	def GetQuestLimit(self):
		"""Returns the maximum number of Quests that the QuestLog can hold"""
		return(self.QuestLimit)
	def IsDuplicate(self,QueryQuest):
		"""Checks if current Quests already contain QueryQuest. Returns True or False."""
		for EachQuest in self.Quests:
			if str(EachQuest) == str(QueryQuest):
				return(True)
		return(False)
	def RemoveQuest(self,QueryQuest):
		"""Removes QueryQuest from list of current Quests."""
		NewState=[]
		for EachQuest in self.Quests:
			if str(EachQuest) != str(QueryQuest):
				NewState.append(EachQuest)
		self.Quests=NewState
	def AddQuest(self):
		"""Adds a random, non-duplicate Quest to the list of current Quests"""
		if len(self.Quests) <self.QuestLimit:
			added=False
			while added==False:
				RandomQuest=self.QuestList[random.randint(0,len(self.QuestList)-1)]
				if self.IsDuplicate(RandomQuest) ==False:
					self.Quests.append(RandomQuest)
					added=True
				
	def RerollQuest(self,QueryQuest):
		if self.IsDuplicate(QueryQuest)==False:
			print("Cannot reroll {}. Quest not in Quest Log".format(str(QueryQuest)))
			exit()
		else:
			self.QuestLimit +=1
			self.AddQuest()
			self.RemoveQuest(QueryQuest)
			self.QuestLimit -=1
	def RerollA40(self,TargetValue=40):
		"""Rerolls a Quest if it is same value as TargetValue"""
		for EachQuest in self.Quests:
			if EachQuest.value ==TargetValue:
				self.RerollQuest(EachQuest)
				break

class Quest(object):
	"""Contains name and value of quest.

	Parameters:
		name: string representing name of quest.

		value: integer representing value of quest.
	"""
	def __init__(self,name,value):
		self.name=name
		self.value=value
	def __str__(self):
		return("{}: {}".format(self.name,self.value))
	def GetName(self):
		"""Returns the name of the Quest."""
		return(self.name)
	def GetValue(self):
		"""Returns the value of the Quest."""
		return(self.value)


