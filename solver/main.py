from pyomo.environ import *
from pathlib import Path
# Output figures
import numpy as np
# import matplotlib.pyplot as plt
from pyomo.environ import Reals, PositiveReals, NonPositiveReals, NegativeReals, NonNegativeReals, PercentFraction, \
    UnitInterval, Integers, PositiveIntegers, NonPositiveIntegers, NegativeIntegers, NonNegativeIntegers, Binary
# import time
# Data management and treatment
import pandas as pd

hwdata = pd.read_csv('hw.csv')
task_data = pd.read_csv('task_data.csv')
# #print(hwdata)
hwparams = hwdata.drop(['type'],axis=1)
# h_index = hwdata.drop(['type','C','S'],axis=1)
# h_index.to_csv('hpd.csv',index = False)
hwparams.to_csv('H_params.csv', index=False)

model = AbstractModel()

#generadores 1,2,3
model.t = Set()
model.h = Set()

#Parameter Definition

#Implementability of task t in hardware h
model.I = Param(model.t, model.h, within = Binary)

#Load of task t in hardware h
model.L = Param(model.t, model.h, within = NonNegativeReals)

#Cost of hardware h
model.C = Param(model.h)

#Size of hardware h
model.S = Param(model.h)

#Variables definition

model.n = Var(model.h, within=NonNegativeIntegers)

model.x = Var(model.t, model.h, within=Binary)

# #Objective Function
#
def obj_rule(model):
    return sum(model.C[h]*model.n[h] for h in model.h)
model.obj =Objective(rule=obj_rule)
#
#
# #Constraints
#
def Incompatibility_rule(model,t):
    return (sum(model.I[t,h]*model.x[t,h] for h in model.h) == 1)
model.IncompatibilityConstraint = Constraint(model.t,rule=Incompatibility_rule)

def  AllTasksAssigned_rule(model,t):
    return (sum(model.x[t,h] for h in model.h) == 1)
model.AllTasksAssignedConstraint = Constraint(model.t,rule=AllTasksAssigned_rule)
# #
def Overload_rule(model,h):
    return (sum( model.x[t,h] * model.L[t,h] for t in model.t) <= model.S[h]*model.n[h] )
model.OverloadConstraint = Constraint(model.h, rule=Overload_rule)

def Utilization_rule(model,h):
    return ( sum (model.x[t,h] for t in model.t) <=model.n[h]*999)
model.UtilizationConstraint = Constraint(model.h, rule=Utilization_rule)

data = DataPortal()


# Load of sets
data.load(filename='t.csv', format='set', set=model.t)
data.load(filename='h.csv', format='set', set=model.h)


# Load of parameters
data.load(filename='H_Params.csv', index=model.h, param = [model.S,model.C])
data.load(filename='Loads.csv', param=model.L,format='array')
data.load(filename='Implementability.csv', param=model.I,format='array')

instance = model.create_instance(data)

binder = 1
optimizador = 'glpk'
solverpath_exe='C:\\glpk-4.65\\w64\\glpsol'
solver = SolverFactory(optimizador,executable=solverpath_exe)

solver_results = solver.solve(instance, tee=False)  # tee=True muestra la salida del solver
solver_results.write()  # Resumen de los resultados del solver
instance.solutions.load_from(solver_results)



instance.display()

df = pd.DataFrame.from_dict(instance.x.extract_values(), orient='index', columns=[str(instance.x)])
df.to_csv('x.csv', encoding='utf-8', index=True, header=True)
df = pd.read_csv('x.csv', header =0)

print(df)
used =[]

for i in range(len(df)):
    if df.iloc[i,1]==1:
        used.append(df.iloc[i,0])
# print(used[0])
used2=[]
delete=[")","(",",","","'"]
for string in used:
    for sub in delete:
        string = string.replace(sub,"")
    used2.append(string)
# print(used2)

new_string1=""
new_string2=""
t_l=[]
h_l=[]
num =1
for string in used2:
    new_string1 = ""
    new_string2 = ""
    num = 1
    for character in string:

        if (character != " "):
            if num == 1 :
                new_string1 += character
            if num == 2:
                new_string2 += character
        else:
            num =2
    t_l.append(new_string1)
    h_l.append(new_string2)

print(t_l)
print(h_l)

for i in range(len(h_l)):
    for j in range(len(h_l)):
        if (h_l[i] == h_l[j] and i != j and j>=i):
            temp_h = h_l [j]
            h_l[j] = h_l[i+1]
            h_l[i+1]=temp_h
            temp_t = t_l[j]
            t_l[j] = t_l[i + 1]
            t_l[i + 1] = temp_t



hw_repeats = []
for i in range(len(h_l)):
    num_rep=1
    for j in range(len(h_l)):
        if (h_l[i] == h_l[j] and i != j):
            num_rep+=1
    hw_repeats.append(num_rep)
print(hw_repeats)

con = pd.read_csv('connection.csv', header=None)
chl1 =[]
chl2=[]
print(con)
for i in range(len(con)):
    for j in range(len(t_l)):
        if con.iloc[i,0] == t_l[j]:
            chl1.append(h_l[j])
            for k in range(len(t_l)):
                # print(con.iloc[i, 1])
                # print(t_l[k])
                if (con.iloc[i, 1] == t_l[k]):
                    # print('a')
                    chl2.append(h_l[k])
# print(chl1)
# print(chl2)
rl=[]
i=0
while chl1[i:i+1] != []:
    if chl1[i] == chl2[i]:
        chl1.remove(chl2[i])
        chl2.remove(chl2[i])
        # print(chl1)
        # print(chl2)
    i += 1

for i in range(len(chl1)):
    for j in range(len(chl1)):
        if (chl1[i] == chl2[j] and chl1[j] == chl2[i] and i<j):
            rl.append(j)
num_removed=0
for i in rl:
    chl1.pop(i-num_removed)
    chl2.pop(i - num_removed)
    num_removed+=1
print(chl1)
print(chl2)




# print('a')



with open('deployment.flexmi', 'w') as f:
    f.write('<deployment title="TopComponent">\n')
    f.write('\t<device name="'+h_l[0]+'">\n')
    last_index=0
    for i in range(hw_repeats[last_index]):
        f.write('\t\t<component name = "'+t_l[i]+'"/>\n')

        last_index +=1
        # print(last_index)
    f.write('\t</device>\n')
    while(last_index<len(h_l)):

        f.write('\t<device name="' + h_l[last_index] + '">\n')
        for i in range(hw_repeats[last_index]):
            # print(last_index,t_l[last_index])
            f.write('\t\t<component name = "' + t_l[last_index] + '"/>\n')

            last_index+=1
        f.write('\t</device>\n')
    for i in range(len(chl1)):
        f.write('\t<connection from="'+chl1[i]+'" to="'+chl2[i]+'"/>\n')
    f.write('</deployment>')





