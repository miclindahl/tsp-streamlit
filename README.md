# tsp-streamlit
Animation of solving the traveling salesman problem to optimality using mixed-integer programming and iteratively eliminating sub tours. The optimization is done using gurobi and the visualization is made using streamlit

Install streamlit and run with this command: `streamlit run tsp-app.py`

The traveling salesman problem is a NP-hard problem where the goal is to find the shortest tour that visits all points in the graph. Here we solve it using a mixed-integer programming model that only states that every point has to be visited once, which can result in multiple sub-tours instead of a single one.  There are exponentially many of these sub-tours, so it would be very computational expensive to add them all from the beginning. But instead, we iteratively remove the sub-tours that occur by adding additional constraints to the model that removes them.

**Disclaimer: All optimization code is made by https://www.gurobi.com/ . I only made some minor tweaks and added the visualization layer**



![Solving TSP using subtour elimination constraints](tsp_subtours.gif)
