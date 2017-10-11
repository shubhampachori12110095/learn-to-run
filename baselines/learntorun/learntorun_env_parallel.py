#!/usr/bin/env python
import os, sys, shutil, argparse
from os import getpid
print (os.getcwd())
sys.path.append(os.getcwd())

import gym
import numpy as np
import time

from baselines.common.vec_env.safe_subproc_vec_env import SafeSubprocVecEnv
from baselines.common.vec_env.subproc_vec_env import SubprocVecEnv
from learntorun_env import LearnToRunEnv

import psutil

num_cpu = 16
seed = 0

def memory_used():
    process = psutil.Process(getpid())
    return process.memory_info().rss  # https://pythonhosted.org/psutil/#psutil.Process.memory_info


def make_env(rank):
    def _thunk():
        env = LearnToRunEnv(difficulty=(seed+rank)%3)
        env.seed(seed + rank)
        return env
    return _thunk

env = SafeSubprocVecEnv([make_env(i) for i in range(num_cpu)])
action_space = env.action_space
obs = env.reset()

num_timesteps = 1000
t = 0
t1 = time.time()
for i in range(1000):
    action = np.random.randn(*(num_cpu, action_space.shape[0]))
    action[action<0] = 0
    action[action>1] = 1
    observation, reward, done, info = env.step(action)

    t += observation.shape[0]
    if t >= num_timesteps:
        break
    """
    if i % 100 == 0:
        print ("step {}, memory {}".format(i, memory_used()))
    if i % 200 == 0:
        print ("resetting")
        env.close()
        del env
        env = SafeSubprocVecEnv([make_env(j) for j in range(num_cpu)])
        env.reset()
        print ("step {}, memory {}".format(i, memory_used()))
    """

t2 = time.time()

print ("{} timesteps took {} time".format(num_timesteps, t2 - t1))

print ("closing env")
env.close()
print ("closed")
sys.exit()
