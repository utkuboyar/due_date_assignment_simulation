#!/usr/bin/env python
# coding: utf-8

# In[46]:


import gurobipy as gp


# In[47]:


# create the model
model = gp.Model('opt_model')


# In[48]:


n = 5  # number of jobs

a = 1  # cost coefficient for makespan
b = [2, 3, 1, 4, 2]  # cost coefficient for tardiness for each job
p = [3, 1, 2, 4, 2]  # processing time for each job
d = [6, 5, 8, 7, 9]  # due date for each job


# In[49]:


# define the parameters
I = range(n)  # set of jobs
M = sum(p) + 1  # a large number to handle big-M constraints


# In[50]:


# define the decision variables
C = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='C')  # makespan
T = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='T')  # tardiness for each job
Y = model.addVars(I, I, vtype=gp.GRB.BINARY, name='Y')  # binary variables for job sequencing

#D = model.addVar(lb= 0, vtype=gp.GRB.INTEGER, name='D') # due date for the new order


# In[51]:


# set the objective function
model.setObjective(a * C[range(I)] + gp.quicksum(b[i] * T[i] for i in I-1), sense=gp.GRB.MINIMIZE)


# In[56]:


# add the constraints
for i in I:
    for j in range(i+1, n):
        model.addConstr(C[i] <= C[j] - p[j] + M * (1 - Y[i,j]))
        model.addConstr(C[j] <= C[i] - p[i] + M * (1 - Y[i,j]))
for i in I:
    model.addConstr(T[i] >= C[i] - d[i])
    model.addConstr(T[i] >= 0)
    
model.addConstr(D in d)


# In[53]:


# optimize the model
model.optimize()


# In[55]:


if model.status == gp.GRB.OPTIMAL:
    print("Optimal objective value:", model.objVal)
    print("Optimal job sequence:")
    for i in range(n):
        for j in range(n):
            if y[i,j].x > 0.5:
                print("Job", i, "starts before job", j)
    print("Optimal completion times:")
    for i in range(n):
        print("Job", i, ":", C[i].x)
    print("Optimal tardiness:")
    for i in range(n):
        print("Job", i, ":", T[i].x)
    print("Optimal due date for new job:", D.x)
else:
    print("No solution found.")


# In[ ]:




