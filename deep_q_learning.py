# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 16:43:15 2020

@author: cleme
Source: https://keon.github.io/deep-q-learning/
"""

import numpy as np
import matplotlib.pyplot as plt
from backend_single_agent_v3 import Environment
from visualization import ImageResult, show_video
from tensorflow import keras
from collections import deque
from replay_buffer import ReplayBuffer
from keras.models import load_model, Sequential
from keras.layers.convolutional import Convolution2D
from keras.optimizers import Adam
from keras.layers.core import Activation, Dropout, Flatten, Dense

class DeepQ:
    
    def _init_(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
    
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model
    
    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = np.random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
              target = reward + self.gamma * \
                       np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def surrounding_state(env, hunter):
    #positions of the hunters and prey and walls if they are visible
    #hunter : index of hunter in list of hunters
    vision = env.vision
    shape = env.shape
    state = []
    pos_hunter = env.hunters[hunter].position
    pos_prey = env.prey.position
    
    #position of the prey
    if np.abs(pos_prey[0]-pos_hunter[0])<=vision and np.abs(pos_prey[1]-pos_hunter[1])<=vision :
        state.append(pos_prey - pos_hunter)
    else : 
        state.append(np.array([-100,-100]))
        
    #position of the hunters
    nbh_vision = 0
    relative_positions=[]
    for i in range (env.nb_hunters):
        if i == hunter:
            continue
        pos_other_hunter = env.hunters[i].position
        if np.abs(pos_other_hunter[0]-pos_hunter[0])<=vision and np.abs(pos_other_hunter[1]-pos_hunter[1])<=vision  :
            relative_positions.append(pos_other_hunter - pos_hunter)
            nbh_vision +=1
            
    np.sort(relative_positions, axis=0) #so that the state is not dependent on the order of the hunters
    for i in range(nbh_vision):
        state.append(relative_positions[i])
    
    for i in range(env.nb_hunters-nbh_vision-1):
        state.append(np.array([-100, -100]))
            
    #position of the walls       
    if pos_hunter[0]<vision :
        pos_wall_x = -1-pos_hunter[0]
    elif pos_hunter[0]>=shape - vision :
        pos_wall_x = shape-pos_hunter[0]
    else :
        pos_wall_x = -100
    if pos_hunter[1]<vision :
        pos_wall_y = -1-pos_hunter[1]
    elif pos_hunter[1]>=shape - vision :
        pos_wall_y = shape-pos_hunter[1]
    else :
        pos_wall_y = -100    
    
    state.append(np.array([pos_wall_x,pos_wall_y]))
    r = []
    for i in state:
        r += list(i)
    return r

def visions(env):
    #array of the surrounding states of all hunters
    visions = []
    for i in range(env.nb_hunters):
        visions.append(surrounding_state(env,i))
    return visions
        
if __name__ == "__main__":

    # initialize gym environment and the agent
    env = Environment()
    agent = DeepQ(env)
    
    n_episode = 500
    print("n_episode ", n_episode)
    max_horizon = 300
    
    rewards_list = []
    successes = []
    nb_steps = []

    # Iterate the game
    for i_episode in range(n_episode):

        # reset state in the beginning of each game
        env.reset()
        states = visions(env)
        
        images =[env.show()]
        rewards_episode = []

        for i_step in range(max_horizon):
            actions = []
            # Decide action
            for i in range(env.nb_hunters):
                actions.append(agent.act(states[i]))

            # Advance the game to the next frame based on the action.
            # Reward is 1 for every frame the pole survived
            obs_prime, rewards, done, info = env.step(actions)
            images.append(env.show())
            rewards_episode.append(sum(rewards))
            states_prime = visions(env) 
            
            # memorize the previous state, action, reward, and done
            for i in range(env.nb_hunters):
                agent.memorize(states[i], actions[i], rewards[i], states_prime[i], done)

            # make next_state the new current state for the next frame.
            states = states_prime.copy()

            # done becomes True when the game ends
            if done:
                # print the score and break out of the loop
                successes.append(1)
                nb_steps.append(i_step)
                break
            
            if i_step == max_horizon-1 :
                successes.append(0)
                nb_steps.append(i_step)
                rewards_list.append(np.sum(rewards))
        
        if (i_episode+1)%100==0:
            show_video(images, i_episode)

        # train the agent with the experience of the episode
        agent.replay(32)
    
    plt.figure(0)
    plt.plot([np.mean(rewards_list[i*100:(i+1)*100]) for i in range(n_episode//100)])
    plt.title("Policy with {0} and {1}".format(rl_algorithm, explore_method))
    plt.xlabel("Number of episodes (x100)")
    plt.ylabel("Average rewards")
    plt.show()
    
    plt.figure(1)
    plt.plot([np.mean(successes[i*100:(i+1)*100]) for i in range(n_episode//100)])
    plt.title("Policy with {0} and {1}".format(rl_algorithm, explore_method))
    plt.xlabel("Number of episodes (x100)")
    plt.ylabel("Average success rate")
    plt.show()
    
    plt.figure(2)
    plt.plot([np.mean(nb_steps[i*100:(i+1)*100]) for i in range(n_episode//100)])
    plt.title("Policy with {0} and {1}".format(rl_algorithm, explore_method))
    plt.xlabel("Number of episodes (x100)")
    plt.ylabel("Average time steps")
    plt.show()
