import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.policy = []
        # TODO: Initialize any additional variables here

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        pactions = [None, 'forward', 'left', 'right']

        # TODO: Update state
        state = inputs
        self.state = "{}".format(state)
        
        # TODO: Select action according to your policy
        scores = [self.Get_Rewards(self, a, state, self.next_waypoint) for a in pactions[0:]]
        action = pactions[scores.index(max(scores))]
        
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.policy = action        
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, state = {}".format(deadline, inputs, action, reward, state)  # [debug]
        
    def Get_Rewards(self, agent, action, currstate, waypoint):
        state = currstate
        light = currstate['light']
        reward = 0  
        move_okay = True
        if action == 'forward':
            if light != 'green':
                move_okay = False
        elif action == 'left':
            if light == 'green':
                pass
            else:
                move_okay = False
        elif action == 'right':
            pass
        if action is not None:
            if move_okay:

                reward = 2 if action == waypoint else 0.5
            else:
                reward = -1
        else:
            reward = 1            
        return reward
        
        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=1.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=10)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
