from cplex.callbacks import *
from docplex.mp.callbacks.cb_mixin import *
import numpy as np
import plot_class
from plot_class import *


class Callback_lazy(ConstraintCallbackMixin, LazyConstraintCallback):
    def __init__(self, env):
        """
        Initializes the Callback_lazy class.

        Args:
            env: CPLEX environment.

        Returns:
            None
        """
        LazyConstraintCallback.__init__(self, env)
        ConstraintCallbackMixin.__init__(self)

    def __call__(self):
        """
        Callback function to be called for lazy constraint callback.
        This function is called during the optimization process to add
        lazy constraints when the solution violates certain conditions.

        Returns:
            None
        """
        print('running lazy callback..........')
        self.num_calls += 1

        # Retrieve solution values for x and y variables
        sol_x = self.make_solution_from_vars(self.model_instance.x.values())
        sol_y = self.make_solution_from_vars(self.model_instance.y.values())

        # Create a graph G and add nodes
        G = nx.Graph()
        # for node in self.model_instance.data.V:
        #     if
        G.add_nodes_from(self.model_instance.data.V)

        # Add edges to the graph G based on the solution values of x and y variables
        edges = []
        for (i, j) in self.model_instance.x_keys:
            if sol_x.get_value(self.model_instance.x[i, j]) > 1 - 1e-2:
                edges.append((i, j))
        for (i, j) in self.model_instance.y_keys:
            if sol_y.get_value(self.model_instance.y[i, j]) > 1 - 1e-2:
                edges.append((i, j))
        G.add_edges_from(edges)

        # Find connected components in the graph
        components = list(nx.connected_components(G))

        # Check if the number of components exceeds the allowed number of components
        if len(components) > self.model_instance.data.n:
            for component in components:
                if len(component) > 1:

                    # Identify the cut set and component edges
                    cut_set = [(o, i) for (o, i) in self.model_instance.x_keys if
                               o not in component and i in component]
                    c_edges = [(o, i) for (o, i) in self.model_instance.x_keys if
                               o in component and i in component]

                    # Add lazy constraints for vertex in the component
                    for j in component:
                        if not self.model_instance.is_root(j):
                            ct = self.model_instance.model_instance.sum(self.model_instance.x[o, i] for (o, i) in cut_set
                                                                        ) >= self.model_instance.model_instance.sum(
                                self.model_instance.y[p, q] for (p, q) in c_edges if q == j) + self.model_instance.y[j, j]
                            # print(ct)
                            ct_cpx = self.linear_ct_to_cplex(ct)
                            self.add(ct_cpx[0], ct_cpx[1], ct_cpx[2])
                            print('added lazy cut')


class Callback_user(ConstraintCallbackMixin, UserCutCallback):
    def __init__(self, env):
        """
        Initializes the Callback_user class.

        Args:
            env: CPLEX environment.

        Returns:
            None
        """
        UserCutCallback.__init__(self, env)
        ConstraintCallbackMixin.__init__(self)

    def __call__(self):
        """
        Callback function to be called for user cut callback.

        Returns:
            None
        """
        print('running user callback......')
        # Retrieve solution values for x and y variables
        sol_x = self.make_solution_from_vars(self.model_instance.x.values())
        sol_y = self.make_solution_from_vars(self.model_instance.y.values())

        # Create a graph G and add nodes
        G = nx.Graph()
        G.add_nodes_from(self.model_instance.data.V)

        # add the source and the sink
        source = -1
        sink = len(self.model_instance.data.V)
        G.add_nodes_from([source, sink])

        # Add edges to the graph G based on the solution values of x and y variables
        edges = []

        for (i, j) in self.model_instance.x_keys:
            if sol_x.get_value(self.model_instance.x[i, j]) > 1e-5:
                edges.append((i, j, {'capacity': sol_x.get_value(self.model_instance.x[i, j])}))

        for r in self.model_instance.data.roots:
            # get the neighbourhood of root r
            array = [j for (i, j) in self.model_instance.data.edges if i == r]

            # get the maximal x_rj
            sr_capacity = max(array, key=lambda j: sol_x.get_value(self.model_instance.x[r, j]))

            edges.append((source, r, {'capacity': sr_capacity}))

        for costumer in self.model_instance.data.customers:
            edges.append((costumer, sink, {'capacity': 0}))

        G.add_edges_from(edges)

        min_cut = np.inf
        min_cut_vertex = None
        cut_partition = None

        for i in self.model_instance.data.customers:

            # assign capacities of edges from customers to the sink
            for j in self.model_instance.data.customers:
                if i != j:
                    G[j][sink]['capacity'] = sol_y.get_value(self.model_instance.y[j, i])
            G[i][sink]['capacity'] = sol_y.get_value(self.model_instance.y[i, i])

            cut_value, partition = nx.minimum_cut(G, source, sink)

            if cut_value < min_cut and len(partition[1]) > 1:
                min_cut = cut_value
                min_cut_vertex = i
                cut_partition = partition

        if min_cut < 1 and min_cut_vertex in cut_partition[1]:
            print('min_cut', min_cut)
            cut_set = [(o, i) for (o, i) in self.model_instance.x_keys if
                           o not in cut_partition[1] and i in cut_partition[1]]
            c_edges = [(o, i) for (o, i) in self.model_instance.y_keys if
                       o in cut_partition[1] and i in cut_partition[1]]
            print(c_edges)

            # left = sum(sol_x.get_value(self.model_instance.x[i, j]) for (i, j) in cut_set)
            # right = sum(sol_y.get_value(self.model_instance.y[i, j]) for (i, j) in c_edges if j == min_cut_vertex) + \
            #         sol_y.get_value(self.model_instance.y[min_cut_vertex, min_cut_vertex])
            #
            # # print('left:', left)
            # # print('right:', right)

            ct = self.model_instance.model_instance.sum(self.model_instance.x[o, i] for (o, i) in cut_set) >= \
                 self.model_instance.model_instance.sum(self.model_instance.y[p, min_cut_vertex] for p in cut_partition[1])
            # print(ct)
            ct_cpx = self.linear_ct_to_cplex(ct)
            self.add(ct_cpx[0], ct_cpx[1], ct_cpx[2])
            print('added user cut')


class HeuristicsCallback(ConstraintCallbackMixin, HeuristicCallback):

    def __init__(self, env):
        HeuristicCallback.__init__(self, env)
        ConstraintCallbackMixin.__init__(self)
        self.count = 0

    def __call__(self):
        print('run heuristic')

        # Retrieve solution values for w variables
        sol_w = self.make_solution_from_vars(self.model_instance.w.values())

        # Initialize a source node and get the threshold value from the data
        source = -1
        threshold = self.model_instance.data.threshold

        # Identify root nodes and classify customers into tree_nodes and leaf_nodes based on the threshold
        roots = self.model_instance.data.roots
        tree_nodes = [i for i in self.model_instance.data.customers
                      if sol_w.get_value(self.model_instance.w[i]) > threshold]
        backbone_nodes = [*roots, *tree_nodes]

        leaf_nodes = [i for i in self.model_instance.data.customers
                      if sol_w.get_value(self.model_instance.w[i]) <= threshold]

        # Create a graph G and add nodes
        G = nx.DiGraph()
        G.add_node(source)
        G.add_nodes_from(backbone_nodes)

        # Add edges from the source to each root with zero weight
        dummy_to_roots = [(source, i, {'weight': 0}) for i in self.model_instance.data.roots]

        # Add edges from roots to tree nodes with weights from the data
        root_to_nodes = [(r, i, {'weight': self.model_instance.data.c[r, i]}) for r in roots for i in tree_nodes]

        # Add edges between tree nodes with weights from the data
        edges = [(i, j, {'weight': self.model_instance.data.c[i, j]})
                 for i in tree_nodes for j in tree_nodes if i != j]

        # Add all edges to the graph G
        G.add_edges_from(dummy_to_roots)
        G.add_edges_from(root_to_nodes)
        G.add_edges_from(edges)

        # Compute the minimum spanning arborescence T and remove the source node
        T = nx.minimum_spanning_arborescence(G)
        T.remove_node(source)

        # Get the edges of the spanning tree
        tree_edges = T.edges()

        # Determine the closest tree node for each leaf node and create edges
        leaf_edges = []
        for leaf in leaf_nodes:
            closest = min(tree_nodes, key=lambda k: self.model_instance.data.a[k, leaf])
            leaf_edges.append((closest, leaf))

        # Calculate the total cost of the solution
        cost = sum(self.model_instance.data.c[i, j] for (i, j) in tree_edges) +\
               sum(self.model_instance.data.a[i, j] for (i, j) in leaf_edges)

        # Check if the computed cost is better than the incumbent solution
        if cost < self.get_incumbent_objective_value():
            weights = []
            c = []

            # Set solution values for x variables based on tree edges
            for (i, j) in self.model_instance.x:
                c.append(self.model_instance.x[i, j].name)
                if (i, j) in tree_edges:
                    weights.append(1)
                else:
                    weights.append(0)

            # Set solution values for y variables based on leaf edges
            for (i, j) in self.model_instance.y:
                c.append(self.model_instance.y[i, j].name)
                if (i, j) in leaf_edges:
                    weights.append(1)
                else:
                    weights.append(0)
            # Set solution values for w variables based on tree nodes
            for i in self.model_instance.w:
                c.append(self.model_instance.w[i].name)
                if i in backbone_nodes:
                    weights.append(1)
                else:
                    weights.append(0)

            # Update the incumbent solution with the new values and cost
            self.set_solution([c, weights], cost)
            print("Incumbent updated with cost = " + str(cost))

            if self.model_instance.data.plot:
                self.count += 1
                title = 'Figure' + str(self.count) + '.png'
                plot_class.plot_graph(self.model_instance, tree_nodes, leaf_nodes, tree_edges, leaf_edges,
                                      show=False, save=True, title=title)
        else:
            print("failed")

