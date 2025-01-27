from docplex.mp.model import Model
import networkx as nx


class FspModel:
    def __init__(self, name, data):
        self.data = data  # Instance of Data class containing problem data
        self.model_instance = Model(name)  # Create a new optimization model with the given name

        # Define keys for binary decision variables
        self_loop = [(i, i) for i in data.V]
        self.x_keys = [(i, j) for (i, j) in data.edges]
        self.y_keys = [*self_loop, *data.edges]

        # Define keys for binary decision variables
        self.x = self.model_instance.binary_var_dict(self.x_keys, name='x')
        self.y = self.model_instance.binary_var_dict(self.y_keys, name='y')

        # Define objective function: minimize total costs including assignment costs and connectedness cost
        self.model_instance.minimize(
            self.model_instance.sum(self.x[i, j] * data.c[i, j] for (i, j) in data.edges)
            + self.model_instance.sum(self.y[i, j] * data.a[i, j] for (i, j) in data.edges))

        # fix the roots
        self.model_instance.add_constraints(self.y[i, i] == 1 for i in data.roots)

        # i is on a tree if i is connected to one predecessor
        self.model_instance.add_constraints(self.model_instance.sum(self.x[o, i] for o in data.V if o != i) == self.y[i, i]
                                            for i in data.customers)

        # i can be assigned to other vertex iff i is not on a tree.
        self.model_instance.add_constraints(self.model_instance.sum(self.y[o, i] for o in data.V) == 1
                                            for i in data.customers)

        # j can be connected or assigned to i in a tree only if i is on a tree plus no bi-directed loops
        self.model_instance.add_constraints(self.x[i, j] + self.y[i, j] + self.x[j, i] <= self.y[i, i]
                                            for i in data.customers for j in data.customers if i != j)

        self.model_instance.add_constraints(self.y[i, j] == 0 for i in data.roots for j in data.customers)

        self.model_instance.add_constraints(self.x[i, j] >= 0 for (i, j) in self.x_keys)
        self.model_instance.add_constraints(self.y[i, j] >= 0 for (i, j) in self.y_keys)

        self.model_instance.add_constraints(self.x[i, j] <= 1 for (i, j) in self.x_keys)
        self.model_instance.add_constraints(self.y[i, j] <= 1 for (i, j) in self.y_keys)

    def solve(self, log=False):
        self.solution = self.model_instance.solve(log_output=log)

    def is_root(self, i):
        return i < self.data.n

    def build_warmstart(self):
        # heu = heuristics(self)
        # heu.greedy_blank_sart()
        # heu.two_opt()

        source = -1
        # Create a graph G and add nodes
        G = nx.DiGraph()
        G.add_node(source)
        G.add_nodes_from(self.data.V)

        # Add edges to the graph G based on the solution values of x and y variables
        edges = [(i, j, {'weight': self.data.c[i, j]}) for (i, j) in self.data.edges]

        edges_to_roots = [(source, i, {'weight': 0}) for i in self.data.roots]

        G.add_edges_from(edges)
        G.add_edges_from(edges_to_roots)

        T = nx.minimum_spanning_arborescence(G)

        T.remove_node(source)

        backbone_nodes = [0 for _ in self.data.V]
        backbone_edges = []
        leaf_edges = []

        for (i, j) in self.data.edges:
            backbone_nodes[i] = 1

        for (i, j) in self.data.edges:
            if backbone_nodes[i] == 1 and backbone_nodes[j] == 1:
                backbone_edges.append((i, j))
            if backbone_nodes[i] == 1 and backbone_nodes[j] == 0:
                leaf_edges.append((i, j))

        warmstart = self.model_instance.new_solution()

        for edge in self.data.edges:
            if edge in backbone_edges:
                warmstart.add_var_value(self.x[edge], 1)
                warmstart.add_var_value(self.y[edge], 0)
            elif edge in leaf_edges:
                warmstart.add_var_value(self.x[edge], 0)
                warmstart.add_var_value(self.y[edge], 1)
            else:
                warmstart.add_var_value(self.x[edge], 0)
                warmstart.add_var_value(self.y[edge], 0)

        for i in self.data.V:
            if backbone_nodes[i] == 1:
                warmstart.add_var_value(self.w[i], 1)
            else:
                warmstart.add_var_value(self.w[i], 0)

        self.model_instance.add_mip_start(warmstart)
        print('warmstart created.')
