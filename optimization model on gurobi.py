import gurobipy as gp

# create the model
model = gp.Model('opt_model')


n = 5  # number of jobs= already existing ones + new arrival

a = 1  # cost coefficient for makespan
b = [2, 3, 3, 4]  # cost coefficient for tardiness for each job
p = [3, 1, 2, 1,6]  # expected processing time for each job
d = [6, 5, 8, 7]  # due date for each job


# define the parameters
I = range(n)  # set of jobs
M = sum(p) + 1  # a large number to handle big-M constraints
L= [(i,j) for i in I for j in range(i+1,n)]

# define the decision variables
C = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='C')  # completion time of each job
T = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='T')  # tardiness for each job
Y = model.addVars(L,lb=0, vtype=gp.GRB.BINARY, name='Y')  # binary variables for job sequencing


# set the objective function
model.setObjective(a * C[n-1] + gp.quicksum(b[i] * T[i] for i in range(n-1)), sense=gp.GRB.MINIMIZE)


# add the constraints
for i in I:
    for j in range(i+1, n):
        print(i,j)
        model.addConstr(C[i] <= C[j] - p[j] + M * (1 - Y[i,j]))
        model.addConstr(C[j] <= C[i] - p[i] + M * (Y[i,j]))

for i in range(n-1):
    model.addConstr(T[i] >= C[i] - d[i])
    model.addConstr(T[i] >= 0)

    
for i in I:
    model.addConstr(C[i] >= p[i])

    
    
# optimize the model
model.optimize()



if model.status == gp.GRB.OPTIMAL:
    print("Optimal objective value:", model.objVal)
    print("Optimal job sequence:")
    for i in range(n):
        for j in range(i+1, n):
            if Y[i,j].x > 0.5:
                print("Job", i, "starts before job", j)
            else:
                print(Y[i,j].x)
            
    print("Optimal completion times:")
    for i in range(n):
        print("Job", i, ":", C[i].x)
    print("Optimal tardiness:")
    for i in range(n):
        print("Job", i, ":", T[i].x)
    print("Optimal due date for new job:", C[n-1].x)
else:
    print("No solution found.")
