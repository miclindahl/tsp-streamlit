import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import random
import itertools
from gurobipy import *
plt.rcParams['savefig.pad_inches'] = 0
st.title('Travelling salesman problem')

# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = tuplelist((i,j) for i,j in model._vars.keys() if vals[i,j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour,tours = subtour(selected)
 
        if len(tour) < n:
            model._subtours += 1
            # add subtour elimination constraint for every pair of cities in tour
            model.cbLazy(quicksum(model._vars[i,j]
                                  for i,j in itertools.combinations(tour, 2))
                         <= len(tour)-1)
               #st.write(tour)
        current_length = round(model.cbGet(GRB.Callback.MIPSOL_OBJ))
        best = round(model.cbGet(GRB.Callback.MIPSOL_OBJBST))
        bound = max(0,round(model.cbGet(GRB.Callback.MIPSOL_OBJBND)))
        model._summary.markdown("**Sub tour elimination constraints** {:d} **Lower bound** {:d}km  \n**Current Solution**  {:d}km  - {:d} subtour(s)".format(model._subtours,bound,current_length,len(tours)))
        #TODO update bound in other callback. Structure output
        plt.plot([x[0] for x in points], [x[1] for x in points], 'o')
        #print("total tours " + str(sum(len(t) for t in tours)))
        for tour in tours:
            tour.append(tour[0])
            points_tour = [points[i] for i in tour]
            plt.plot([x[0] for x in points_tour], [x[1] for x in points_tour], '-')
        plt.axis([0, 105, 0, 105])
        plt.xlabel("km")
        plt.ylabel("km")
        model._plot.pyplot()
        

# Given a tuplelist of edges, find the shortest subtour

def subtour(edges):
    unvisited = list(range(n))
    cycle = range(n+1) # initial length has 1 more city
    cycles = []
    while unvisited: # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i,j in edges.select(current,'*') if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
        cycles.append(thiscycle)
    return (cycle,cycles)


n = st.slider('How many destinations to generate?', 5, 200, 5)
# Create n random points
points = [(random.randint(0,100),random.randint(0,100)) for i in range(n)]

# Dictionary of Euclidean distance between each pair of points

dist = {(i,j) :
    math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
    for i in range(n) for j in range(i)}

m = Model()
m._subtours = 0
m._summary = st.empty()
m._plot = st.empty()
m._points = points
# Create variables

vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
for i,j in vars.keys():
    vars[j,i] = vars[i,j] # edge in opposite direction

# Add degree-2 constraint

m.addConstrs(vars.sum(i,'*') == 2 for i in range(n))

# Optimize model

m._vars = vars
m.Params.lazyConstraints = 1
m.optimize(subtourelim)

vals = m.getAttr('x', vars)
selected = tuplelist((i,j) for i,j in vals.keys() if vals[i,j] > 0.5)

tour,tours = subtour(selected)
assert len(tour) == n
tour.append(tour[0])
points_tour = [points[i] for i in tour]

current_length = round(m.objVal)
best = round(m.objVal)
bound = max(0,round(m.objVal))
m._summary.markdown("**Sub tour elimination constraints** {:d} **Lower bound** {:d}km  \n**Current Solution**  {:d}km  - {:d} subtour(s)".format(m._subtours,bound,current_length,len(tours)))

plt.plot([x[0] for x in points_tour], [x[1] for x in points_tour], '-o')
plt.axis([0, 105, 0, 105])
plt.xlabel("km")
plt.ylabel("km")
m._plot.pyplot()

st.write('')
#st.write('Optimal tour: %s' % str(tour))
st.write('Optimal cost: {:0.1f}km'.format(m.objVal))
st.write('Running time to optimize: {:0.1f}s'.format(m.Runtime))
st.write('Sub tour constraint added: {:d}'.format(m._subtours)) 
