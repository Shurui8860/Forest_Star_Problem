from data_class import *
from model_class import *
from solver import *
import random

num_of_roots, num_of_customers = 3, 24
const = 0.7
seed = 0
# seed = random.randint(0, 100)

p = Data(num_of_roots, num_of_customers, threshold=0.6, plot=True)
p.create_data(const=const, seed=seed, width=100)
m = FspModel("FSP", p)

warm_start = False
lazy_callback = True
user_callback = False
heuristic_callback = False
plot = True

solve(m, warm_start, lazy_callback, user_callback, heuristic_callback, plot)


