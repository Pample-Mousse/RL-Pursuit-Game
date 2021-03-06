# -*- coding: utf-8 -*-

import numpy as np


class Environement:
    
    
    shape = None
    hunters = 0
    preys = 0
    agents = []
    role = 1
    positions = []
    actions = []
    step = 0
    
    action_to_delta = {
    0:np.array([0,1]),
    1:np.array([0,-1]),
    2:np.array([1,0]),
    3:np.array([-1,0]),
    4:np.array([0,0])
    }
    
    
    def __init__(self,shape,hunters = 4, preys = 1,positions = None, actions = list(range(4))):
        self.shape = shape
        self.hunters = hunters
        self.preys = preys
        self.actions = actions
        if positions == None:
            self.positions = None
        
        else:
            self.positons = positions
            for i in range(preys):
                self.agents.append(Agent(0,positions[i+1]))
            for i in range(hunters):
                self.agents.append(Agent(1,positions[i+1+preys]))
    
    def voisins(self, position): #C'est encore à faire cette fonction
        return None

    def select_possible_actons(self, position): #Pareil ici
        return self.actions
            
    def step(self,action):
        self.positions[0] += self.action_to_delta[action]
        for i,a in enumerate(self.agents):
            voisins = self.voisins(a.position)
            possible_actions = self.select_possible_actons(a.position)
            action = a.decision(voisins,possible_actions)
            new_position = self.move(a,action)
            self.positions[i] = new_position
        
        self.step += 1
        return self.positions, self.done(), self.reward()
        
    def move(self, agent, action):
        new_position = agent.position + self.action_to_delta[action]
        agent.position = new_position
        return new_position    
        
    def show(self):
        return self.positions
    

        

class Agent:
    
    role = None
    position = None
    decision_function = None
    
    def __init__(self,role,position,decision_function = lambda _,l : np.random.choice(l)):
        self.role = role
        self.position = position
        self.decision_function = decision_function
        
    def decision(self,voisions,possible_actions):
        return self.decision_function(voisions,possible_actions) # Par défaut c'est np.random.choice
