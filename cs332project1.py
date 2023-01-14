# -*- coding: utf-8 -*-
"""CS332Project1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gZ7n8XTmGPtTiWRSyAU7zCDc4uPEeOJP

# **Project 1**

# Loading data, importing libraries
"""

import pandas as pd
import numpy as np
import scipy as sp
from scipy import optimize
from numpy import random
import random
import math
n = 1000
url = 'https://raw.githubusercontent.com/anonymous-student123/bid_data/main/bid_data.csv'
df = pd.read_csv(url)

"""Calculating probabilities with uniform distrubtion

"""

values = np.array([10*v for v in range(1,11)])
c_bids = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
a_bids = np.array([0.01, 10.01, 20.01, 30.01, 40.01, 50.01, 60.01, 70.01, 70.02, 80.02])
test_bids = [0 for i in range(10)]

# removing our bids
df_c = df.drop(index=1)
df_a = df.drop(index=37)

def calculate_prob_and_utility(p,x=None,i=None, sample = None, mc_bids = None):
  probability_arr_c = []
  probability_arr_a = []
  probability_arr_test = []
  probability_arr_MC = []

  if p == 'c':
    df_s = df_c
    own_bids = c_bids
    probability_arr = probability_arr_c
  if p == 'a':
    df_s = df_a
    own_bids = a_bids
    probability_arr = probability_arr_a
  if p == 'test':
    df_s = df
    own_bids = test_bids
    own_bids[i] = x
    probability_arr = probability_arr_test
  if p == 'algorithm':
    df_s = sample
    own_bids = test_bids
    own_bids[i] = x
    probability_arr = probability_arr_test
  if p == 'algorithm-monte-carlo':
    df_s = df
    own_bids = mc_bids
    probability_arr = probability_arr_MC

  # variable for potentially won bets
  total_won = 0

  for i in range(10):
    # our bid
    bid = own_bids[i]

    # DF of bools, true being bids we win against
    win = (df_s < bid)

    # DF of bools, true being bids we tie against
    tie = (df_s == bid)

    # now we simply divide favorable outcomes by total outcomes because the
    # distribution is uniform: any other student's value and bid is equally likely
    # note that we halve the number of "favorable" events in the case of ties
    # to account for the coin flip deciding the outcome.
    favorable = win.to_numpy().sum() + 0.5 * tie.to_numpy().sum()
    probability = favorable / win.size

    total_won += favorable

    # array for probabilities
    probability_arr.append(probability)

  # now we just take the dot product of each probability of win
  prob_win = total_won / (df_s.size * 10)
  utility = np.dot(np.array(probability_arr), values - own_bids) / 10
  return prob_win, utility, probability_arr, np.multiply(np.array(probability_arr), values - own_bids)

prob_win_c, utility_c, prob_arr_c, utility_per_value_c = calculate_prob_and_utility('c')
prob_win_a, utility_a, prob_arr_a, utility_per_value_a = calculate_prob_and_utility('a')

print("Probability C overall wins a bet: ", prob_win_c)
print("C's expected utility: ", utility_c)
print("C's bid winning probability per value: ", prob_arr_c)
print("C's expected utility per value: ", utility_per_value_c)
print("------------")
print("Probability A overall wins a bet: ", prob_win_a)
print("A's expected utility", utility_a)
print("A's bid winning probability per value: ", prob_arr_a)
print("A's expected utility per value: ", utility_per_value_a)

"""Calculating probabilities with Monte-Carlo"""

c_bids = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
a_bids = np.array([0.01, 10.01, 20.01, 30.01, 40.01, 50.01, 60.01, 70.01, 70.02, 80.02])
test_bids = [0 for i in range(10)]
# run_auction takes in a number of auctions to run and a player
# then outputs the calculated percentage of auctions won and
# the average utility over these auctions
def run_auction(n, p, x=None, i=None):
  if p == 'c':
    df_s = df_c
    own_bids = c_bids
  if p == 'a':
    df_s = df_a
    own_bids = a_bids
  if p == 'test':
    # this other "player" is used while optimizing later: it simulates an auction
    # with the only bid being x given value i. this way we can calculate
    # maximum expectation componentwise
    df_s = df
    own_bids = test_bids
    own_bids[i] = x

  wins = 0
  utility = 0
  auctions = 0
  utility_index_i = np.array([0 for i in range(10)])
  auctions_index_i = np.array([0 for i in range(10)])
  wins_index_i = np.array([0 for i in range(10)])

  # looping over each possible value [1,..,10] (in other words [10, ..., 100])
  for i in range(n):
    # generating a random value for self
    self_rn = random.randrange(0,10)
    self_value = (self_rn+1)*10
    self_bid = own_bids[self_rn]


    # generating a random value for other student
    # then selecting this student with sample()
    other_rn = random.randrange(0,10)
    other_value = (other_rn+1) * 10
    random_bid_given_value = df_c.sample()
    other_bid = random_bid_given_value.iat[0,other_rn]


    # generating random value for coin
    coin = random.randrange(0,101) % 2
    
    # the below increments stats given the results of the simulated
    # auction. if a bid is tied it uses a coin RV to update the 
    # counts
    auctions += 1
    auctions_index_i[self_rn] += 1

    if self_bid > other_bid:
      wins += 1
      wins_index_i[self_rn] += 1

      utility += (self_value - self_bid)
      utility_index_i[self_rn] += (self_value - self_bid)
    
    if self_bid == other_bid:
      if coin == 1:
        wins += 1
        wins_index_i[self_rn] += 1

        utility += (self_value - self_bid)
        utility_index_i[self_rn] += (self_value - self_bid)

  return wins / auctions, utility / auctions, np.divide(wins_index_i, auctions_index_i), np.divide(utility_index_i, auctions_index_i)

c_win_percent, c_avg_utility, c_win_percent_indices, c_avg_utility_indices = run_auction(n, 'c')
a_win_percent, a_avg_utility, a_win_percent_indices, a_avg_utility_indices = run_auction(n, 'a')
print("C's simulated win % with ", n, " auctions: ", c_win_percent)
print("C's simulated average utility with ", n, " auctions: ", c_avg_utility)
print("C's bid winning probability per value: ", c_win_percent_indices)
print("C's expected utility per value: ", c_avg_utility_indices)
print("------")
print("A's simulated win % with ", n, " auctions: ", a_win_percent)
print("A's simulated average utility with ", n, " auctions: ", a_avg_utility)
print("A's bid winning probability per value with", n, "auctions: ", a_win_percent_indices)
print("A's expected utility per value with ", n, "auctions: ", a_avg_utility_indices)

"""Error bounds"""

print("DIFFERENCES BETWEEN SIMULATED AND CALCULATED STATISTICS: ")
print("C's agregate probability difference: ", np.abs(c_win_percent - prob_win_c))
print("C's agregate expected utility difference: ", np.abs(c_avg_utility - utility_c))
print("C's componentwise probability difference: ", np.abs(prob_arr_c - c_win_percent_indices))
print("C's componentwise expected utility difference: ", np.abs(utility_per_value_c - c_avg_utility_indices))
print("-------")
print("A's agregate probability difference: ", np.abs(a_win_percent - prob_win_a))
print("A's agregate expected utility difference: ", np.abs(a_avg_utility - utility_a))
print("A's componentwise probability difference: ", np.abs(prob_arr_a - a_win_percent_indices))
print("A's componentwise expected utility difference: ", np.abs(utility_per_value_a - a_avg_utility_indices))

"""Finding optimal bid to maximize utility"""

epsilon = 0.00001

def utility_coord_i(x, i, sample=None):
  if sample is not None:
    return calculate_prob_and_utility('test', x, i, sample)[1]
  return calculate_prob_and_utility('test', x, i)[1]

def utility_monte_carlo_coord_i(x, i, n):
  return run_auction(n, 'test', x, i)[1]

def optimal_bid_one_index(index, df_g=None):
  utilities = []
  if df_g is not None:
    df_s = df_g
    values_arrays = df_s.to_numpy()
    all_values = np.sort(np.unique(np.concatenate(values_arrays)))
  else:
    values_arrays = df.to_numpy()
    all_values = np.sort(np.unique(np.concatenate(values_arrays)))
  for val in all_values:
    if (index+1) * 10 < val:
      if not utilities:
        utilities.append([0,0])
      break
    if df_g is not None:
      utilities.append([val, utility_coord_i(val,index, df_g)*10])
      utilities.append([val + epsilon, utility_coord_i(val + epsilon,index, df_g)*10])
    else:
      utilities.append([val, utility_coord_i(val,index)*10])
      utilities.append([val + epsilon, utility_coord_i(val + epsilon,index)*10])
  return max(utilities, key= lambda x: x[1])

def monte_carlo_bid_one_index(index):
  utilities = []
  values_arrays = df.to_numpy()
  all_values = np.sort(np.unique(np.concatenate(values_arrays)))
  for val in all_values:
    if (index+1) * 10 < val:
      break
    utilities.append([val, utility_monte_carlo_coord_i(val,index, n)])
    utilities.append([val + epsilon, utility_monte_carlo_coord_i(val + epsilon,index, n)])
  return max(utilities, key= lambda x: x[1])

best_utilities_arr = np.array([optimal_bid_one_index(i) for i in range(10)])
optimal = sum(j for i,j in best_utilities_arr)
print("The best bids and expected utilities for each are given in the following ",
      "array of the form [bid, expected utility].")
print(best_utilities_arr)
print("By linearity of expectation we can sum over these and find that our",
      "optimal aggregate expected utility is: ", optimal/10)

best_monte_carlo_utilities_arr = np.array([monte_carlo_bid_one_index(i) for i in range(10)])
mc_optimal = sum(j for i,j in best_monte_carlo_utilities_arr)
print("The best bids and expected utilities via Monte Carlo for each are given in the following ",
      "array of the form [bid, expected utility].")
print(best_monte_carlo_utilities_arr)
print("By linearity of expectation we can sum over these and find that our",
      "optimal aggregate expected utility is: ", mc_optimal)

"""Error with simulated"""

best_monte_carlo_utilities_arr - best_utilities_arr

"""Algorithm"""

def find_optimal_bid(n):
  if n > len(df):
    n = len(df)
  df_sample = df.sample(n)
  # this simply calculates the optimal bid, as done above, but given
  # only a select n number of bids from the original dataset
  # (can be adapted to input custom bids, but functions equivalently by
  # picking this random sample. this is also easier to test using monte-carlo)
  return np.array([optimal_bid_one_index(i, df_sample)[0] for i in range(10)])

find_optimal_bid(1)

"""Monte Carlo on Algorithm"""

def monte_carlo_algorithm(N, s):
  # N: number of times to run monte-carlo
  # s: sample size
  agg_utility = 0
  for i in range(s):
    bids = find_optimal_bid(s)
    compared_to_real = calculate_prob_and_utility('algorithm-monte-carlo', mc_bids = bids)
    agg_utility += compared_to_real[1]
  return agg_utility/s

one_sample_average_utility = monte_carlo_algorithm(n, 1)
ten_sample_average_utility = monte_carlo_algorithm(n, 10)
full_sample_average_utility = monte_carlo_algorithm(n, 100)

print("given ", n, "samples:")
print("when N=1 is given, our algorithm has average utility ", one_sample_average_utility)
print("when N=10 is given, our algorithm has average utility ", ten_sample_average_utility)
print("when N=FULL SET is given, our algorithm has average utility ", full_sample_average_utility)

