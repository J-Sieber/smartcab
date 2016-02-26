import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import numpy as np

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.policy = np.zeros(shape=(384,4))       #create empty matrix for Q.  All the states and actions possible
        self.alpha = 0.9    #Learning rate - alpha
        self.gamma = 0.00     #Discount rate - gamma - set to zero because no matter what action is taken the future action's value is unknown
        self.exploreRate = 0.0  #How much the cab explores or trys new (random) things
        self.numTrials = 100.0     #Set to same as n_trials at the bottom.
        self.curTrial = 0.0
        

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.curTrial = self.curTrial + 1.0
        
        #Update the exploreRate.  The car should explore alot early in the game and drop off quickly
        self.exploreRate = 1.2 * pow(((self.numTrials - self.curTrial) / self.numTrials),5)
        #Update the learning rate.  
        self.alpha = 0.9 * ((self.numTrials - self.curTrial) / self.numTrials) 

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        pactions = [None, 'left', 'right', 'forward']
        
        # Update state
        state = [inputs['light'], inputs['left'], inputs['right'], inputs['oncoming'], self.get_next_waypoint()]
        self.state = "{}".format(state)
        
        # Select action according to your policy
        state = self.GetQRow(inputs['light'], inputs['left'], inputs['right'], inputs['oncoming'], self.get_next_waypoint())
        
        if (random.random() * self.exploreRate) > 0.1:
            action = pactions[random.randint(0,3)]
        else:
            if np.max(self.policy[state]) == 0:
                #pick random direction
                action = pactions[random.randint(0,3)]
            else:
                #Go in the direction with the max Q
                action = pactions[np.argmax(self.policy[state])]
        
        # Execute action and get reward
        reward = self.env.act(self, action)
        
        #Convert action to column number
        action = self.ConvertTraffic(action)

        #Learn policy based on state, action, reward
        #Q(S,A) = (1-alpha)*Q(S,A) + alpha*(R(S,A)+gamma*max_(A')(Q(S',A')))
        self.policy[state][action] = (1-self.alpha)*self.policy[state][action]+self.alpha*(reward + self.gamma * np.max(self.policy))
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, state = {}".format(deadline, inputs, action, reward, state)  # [debug]
    
    def GetQRow(self, Light, Left, Right, Oncoming, NavDir):
        #Get Current Q value        
        if Light == 'green':       
            Light=0
        else:
            Light=1
        
        Left = self.ConvertTraffic(Left)
        Right = self.ConvertTraffic(Right)
        Oncoming = self.ConvertTraffic(Oncoming)
            
        if NavDir=='left':
            NavDir = 0
        elif NavDir=='right':
            NavDir = 1
        else:
            NavDir = 2
            
        Qrow = 192*Light+48*Left+12*Right+3*Oncoming+NavDir
        return Qrow        
    
    def ConvertTraffic(self, val):
        if val==None:
            val = 0
        elif val=='left':
            val = 1
        elif val=='right':
            val = 2
        else:
            val = 3
        return val
        
        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.1)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
