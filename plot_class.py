import matplotlib.pyplot as plt
import networkx as nx


def plot_solution(model):

    plt.figure()
    for i in model.data.roots:
        plt.scatter(model.data.loc[i][0], model.data.loc[i][1], c='red')
        plt.annotate(i, (model.data.loc[i][0] + 2, model.data.loc[i][1]))

    for i in model.data.customers:
        plt.scatter(model.data.loc[i][0], model.data.loc[i][1], c='black')
        plt.annotate(i, (model.data.loc[i][0] + 2, model.data.loc[i][1]))

    for (i, j) in model.x_keys:
        if model.x[i, j].solution_value > 0.9:
            plt.plot([model.data.loc[i][0], model.data.loc[j][0]], [model.data.loc[i][1], model.data.loc[j][1]], c='blue', linewidth='1')
            plt.arrow(model.data.loc[i][0], model.data.loc[i][1], model.data.loc[j][0] - model.data.loc[i][0], model.data.loc[j][1] - model.data.loc[i][1],
                      color='b', shape='full', lw=0, length_includes_head=True, head_width=0.035*model.data.width)

    for (i, j) in model.y_keys:
        if model.y[i, j].solution_value > 0.9:
            plt.plot([model.data.loc[i][0], model.data.loc[j][0]], [model.data.loc[i][1], model.data.loc[j][1]], c='red', linewidth='1')
            plt.arrow(model.data.loc[i][0], model.data.loc[i][1], model.data.loc[j][0] - model.data.loc[i][0], model.data.loc[j][1] - model.data.loc[i][1],
                      color='r', shape='full', lw=0, length_includes_head=True, head_width=0.035 * model.data.width)

    plt.show()


def plot_graph(model, backbone_nodes, leaf_nodes, tree_edges, assignment_edges, show=True, save=False, title='Figure'):
    # Scale factor for node size and arrow size
    scaler = model.data.width

    # Create a directed graph
    G = nx.DiGraph()

    # Add root nodes to the graph with the color 'red'
    G.add_nodes_from(model.data.roots, color='red')

    # Add backbone nodes to the graph with the color 'orange'
    G.add_nodes_from(backbone_nodes, color='orange')

    # Add leaf nodes to the graph with the color 'yellow'
    G.add_nodes_from(leaf_nodes, color='yellow')

    # Add tree edges to the graph with the color 'black'
    G.add_edges_from(tree_edges, color="black")

    # Add assignment edges to the graph with the color 'red'
    G.add_edges_from(assignment_edges, color="red")

    # Get the color attributes for nodes and edges
    node_colors = nx.get_node_attributes(G, 'color').values()
    edge_colors = nx.get_edge_attributes(G, 'color').values()

    # Define the drawing options for the graph
    options = {
        'pos': model.data.loc,  # Node positions
        'edge_color': edge_colors,  # Edge colors
        'node_color': node_colors,  # Node colors
        'node_size': 2 * scaler,  # Node size
        'arrowstyle': '-|>',  # Arrow style for directed edges
        'arrowsize': 0.12 * scaler,  # Arrow size
        'with_labels': True,  # Display node labels
    }

    # Draw the graph with the specified options
    nx.draw_networkx(G, arrows=True, **options)

    # Adjust the layout and display the graph
    plt.tight_layout()  # Adjust subplots to fit into figure area
    plt.draw()  # Redraw the current figure

    # Save the graph to a file if 'save' is True
    if save:
        plt.savefig('Figures/' + title)
        plt.close()  # Close the figure to free up memory

    # Show the graph if 'show' is True
    if show:
        plt.show()  # Display the figure


def create_solution(model):

    # Add backbone nodes to the graph (nodes with solution value > 0.9) and color them orange
    backbone_nodes = [i for i in model.data.customers if model.y[i, i].solution_value > 0.9]

    # Add leaf nodes to the graph (nodes with solution value < 0.1) and color them yellow
    leaf_nodes = [i for i in model.data.customers if model.y[i, i].solution_value < 0.1]

    # Add tree edges to the graph (edges with solution value > 0.9) and color them black
    tree_edges = [(i, j) for (i, j) in model.x_keys if model.x[i, j].solution_value > 0.9]

    # Add assignment edges to the graph (edges with solution value > 0.9) and color them red
    assignment_edges = [(i, j) for (i, j) in model.y_keys if model.y[i, j].solution_value > 0.9 and i != j]

    return backbone_nodes, leaf_nodes, tree_edges, assignment_edges


def plot_solution_graph(model):
    # Create the network structure (backbone nodes, leaf nodes, tree edges, assignment edges)
    backbone_nodes, leaf_nodes, tree_edges, assignment_edges = create_solution(model)

    # Plot the graph using the generated network structure
    plot_graph(model, backbone_nodes, leaf_nodes, tree_edges, assignment_edges)

