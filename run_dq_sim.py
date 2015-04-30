import datetime
import DQSim

def main():
	### File that contains the information on names and values of daily quests. 
	### Should be tab delimited, with name in first column, and value in last column
	#file_of_quests="./hearthstone_dailies.txt"
	QuestFile="./heroes_dailies.txt"

	NumTrials=100 #This is how many trials you want to do
	NumDays=100 #Number of days to run each simulation
	Algorithm=DQSim.CompleteHighest # The subclass of Trial containing the algorithm you want to run.
	
	StartTime=datetime.datetime.now() # Just to mark time so we can see how long everything took. Optional
	Average,StdDev=DQSim.Simulation(NumTrials,NumDays,QuestFile,Algorithm).RunSim() # Creates the simluation, runs all the trials, and then collects the average daily earnings and standard deviation.
	EndTime=datetime.datetime.now() # Marks end time.
	print("completed {} trials of {} steps in {}".format(NumTrials,NumDays,EndTime-StartTime)) # Displays completion message with time taken
	print("Average Earnings: {}. Standard Deviation: {}.".format(Average,StdDev)) # Displays average and standard deviation of earnings


# define your custom trial algorithms here. Ensure they inherit from DQSim.Trial. Must include method for RunAlgorithm(self). Can define whatever other methods to use.

class AwesomeHeroesAlgorithm(DQSim.Trial):
	def RunAlgorithm(self):
		pass
		#whatever other instructions you need.


if __name__=="__main__":
	main()
