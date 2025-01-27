# Forest_Star_Problem

This project implements a graph-based optimization framework for solving facility assignment and connection problems. It combines mathematical modeling, implementation of branch and bound algorithm with lazy(integer sub-solutions), user(fractional sub-solutions) and heuristic(improvement of upper bounds) callbacks, and visualization techniques to optimize resource assignments and connections while minimizing associated costs.

## Project Structure

### Main Components

#### `main.py`

- Entry point of the program.
- Initializes data (`Data` class), defines the model (`FspModel` class), and solves the optimization problem using various configurations.
- Key parameters include the number of roots, customers, and constraints such as thresholds and constants for cost calculations.

#### `data_class.py`

- Contains the `Data` class responsible for generating random problem instances.
- **Key functionalities:**
  - Creates random locations for roots and customers.
  - Generates distance (`c`) and assignment cost (`a`) matrices.
  - Defines edges for graph-based modeling.

#### `model_class.py`

- Implements the `FspModel` class for the optimization model using IBM CPLEX.
- **Key functionalities:**
  - Defines decision variables for edges (`x`) and assignments (`y`).
  - Sets up constraints ensuring:
    - Roots are fixed.
    - Customers are either assigned to roots or connected through a tree.
  - Establishes the objective function to minimize total costs.
  - Includes warm-start initialization using heuristics for better performance.

#### `solver.py`

- Provides utility functions for solving and visualizing the optimization problem.
- **Key functionalities:**
  - Solves the model using defined callbacks and configurations.
  - Generates a visualization of the solution as a graph with backbone and leaf nodes, tree edges, and assignment edges.

#### `callback.py`

- Contains custom callbacks for solving the optimization problem.
- Implements lazy constraints, user cuts, and heuristic approaches for model refinement.
- **Key functionalities:**
  - Ensures feasible solutions during the optimization process.
  - Utilizes graph-based methods to dynamically add constraints and improve the solution.

#### `plot_class.py`

- Handles graph visualization.
- **Key functionalities:**
  - Visualizes the solution graph, differentiating between backbone and leaf nodes, tree edges, and assignment edges.
  - Supports saving the plots for analysis.

## Dependencies

The project requires the following Python libraries:

- `numpy`
- `matplotlib`
- `math`
- `networkx`
- IBM CPLEX (`docplex`)

## Execution

1. Ensure all dependencies are installed.
2. Run the `main.py` file:
   ```bash
   python main.py
   ```
3. The script generates and solves the optimization problem, and the solution is visualized as a graph.


## Customization

- Modify parameters in `main.py` (e.g., number of roots and customers, cost constants).
- Adjust thresholds and random seeds for different problem instances.

---

This project demonstrates the power of mathematical optimization and graph theory in solving complex resource allocation problems. Modify the code or parameters to suit specific applications or test scenarios.

