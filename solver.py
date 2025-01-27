from callback import *


def solve(m, warm_start=False, lazy_callback=False, user_callback=False, heuristic_callback=False, plot=False):

    if warm_start:
        m.build_warmstart()

    if lazy_callback:
        cb_lazy = m.model_instance.register_callback(Callback_lazy)
        cb_lazy.model_instance = m
        cb_lazy.problem_data = m.data
        cb_lazy.num_calls = 0

    if user_callback:
        cb_user = m.model_instance.register_callback(Callback_user)
        cb_user.model_instance = m
        cb_user.problem_data = m.data
        cb_user.num_calls = 0

    if heuristic_callback:
        cb_heur = m.model_instance.register_callback(HeuristicsCallback)
        cb_heur.model_instance = m
        cb_heur.problem_data = m.data

    m.solve(True)
    print('The objective function is:', round(m.solution.get_objective_value(), 2))

    if plot:
        plot_solution_graph(m)