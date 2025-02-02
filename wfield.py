import numpy as np
from numpy import linalg as LA
import math, cmath
from scipy.optimize import fmin, minimize, rosen, rosen_der
from itertools import product, combinations
from copy import copy
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.interpolate import make_lsq_spline, BSpline
from scipy.interpolate import make_interp_spline
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from scipy.interpolate import interp1d
import scipy.optimize as optimize
 
#FUNCTIONS

def expf(x,L):
   return complex(np.cos(2*np.pi*x/L),np.sin(2*np.pi*x/L))

def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True 
    else:
        return False

def Ham(H1,H2,U):
   return H1+np.multiply(H2,U)

def UnD(th,a1,a2,a3,a4,Od):
   OpAux = np.matmul(np.matmul(np.matmul(np.transpose(Od[a1]),np.transpose(Od[a2])),Od[a3]),Od[a4])-np.matmul(np.matmul(np.matmul(np.transpose(Od[a4]),np.transpose(Od[a3])),Od[a2]),Od[a1])
   return np.identity(2**L)+np.multiply(OpAux,np.sin(th))-np.multiply((np.cos(th)-1),np.matmul(OpAux,OpAux))

#NUMBER OF SITES:
L = 5
print(L)

#NUMBER OF PARTICLES
N = 25

#TROTTER STEPS
trotter = 3

#WEIGHTS:
##Remember that there should be as many w as sites L
w = [0.5,0.4,0.3,0.2,0.1]

#GENERATION OF THE HILBERT (FOCK) SPACE
## This generates the Hilbert space {|000>,|001>,...} but in a non-organized way
res = [ele for ele in product([0,1], repeat = L)]
res1 = [ele for ele in product([0,0], repeat = L)]
res = np.array(res)
res1 = np.array(res1)

#ORGANIZING THIS IN N-PARTICLE SECTORS
##res1 contains ALL the states in the Hilbert space
sumsec= np.sum(res, axis=1)
vec = []
for j in range(L+1):
   vec.append([i for i,x in enumerate(sumsec) if x == j])

order= sum(vec,[])
for j in range(2**L):
   res1[j] = res[order[j]]

#GENERATION OF THE ANHILITATION OPERATORS
##Op[0],Op[1]... are the anhilitation operators for sites 0,1,...
Op = np.zeros((L,2**L,2**L))

for j in range(L):
   res2 = [ele for ele in product([0,0], repeat = L)]
   res2 = copy(res1)
   res2[:,j] = np.zeros(2**L)
   aux2 = copy(res1[:,j])
   if j == 0:
      sta= copy(res1[:,0])
   else:
      sta = [math.pow(-1,value) for value in sum(res1[:,x] for x in range(j))] 
   for j1 in range(2**L):
      for j2 in range(2**L):
         if np.array_equal(res1[j1],res2[j2]):
            Op[j,j1,j2] = sta[j2]*aux2[j2]

##This is optional to verify the fermionic commutation rules:
#print(np.sum(Op[0],axis=1))
#print(np.diag(np.matmul(np.transpose(Op[0]), Op[0])+np.matmul(Op[0],np.transpose(Op[0]))))


#CONSTRUCTION OF THE HAMILTONIANS

Ham1 =-sum(np.multiply(expf((k1-k2)*jj,L)*expf(-k2,L)/L,np.matmul(np.transpose(Op[k1]), Op[k2]))+np.multiply(expf((k1-k2)*jj,L)*expf(k1,L)/L,np.matmul(np.transpose(Op[k1]), Op[k2])) for k1 in range(L) for k2 in range(L) for jj in range(L))

Ham2 =sum(np.multiply(expf((k1-k2+k3-k4)*jj,L)*expf(k3-k4,L)/L**2,np.matmul(np.matmul(np.matmul(np.transpose(Op[k1]), Op[k2]),np.transpose(Op[k3])),Op[k4])) for k1 in range(L) for k2 in range(L) for k3 in range(L) for k4 in range(L) for jj in range(L))

#EIGENVALUES

eigen = []

for u in range(11):
   w, v = LA.eig(Ham(Ham1,Ham2,u)[6:16,6:16])
   eigen.append(w)

eigen = np.array(eigen)

print(np.sum(UnD(np.pi/2,1,1,2,2,Op),axis=1))
#[L+1:int(L+L*(L-1)/2),L+1:L+int(L*(L-1)/2)])

FI1 =[0,1,2,3,4,5, 6, 7, 8, 9,10]
FI1 = np.array(FI1)

plt.rc('axes', labelsize=15)
plt.rc('font', size=15)  
plt.plot(FI1, eigen[:,0],'b*')
plt.plot(FI1, eigen[:,1],'b*')
plt.plot(FI1, eigen[:,2],'b*')
plt.plot(FI1, eigen[:,3],'b*')
plt.plot(FI1, eigen[:,4],'b*')
plt.plot(FI1, eigen[:,5],'b*')
plt.plot(FI1, eigen[:,6],'b*')
plt.plot(FI1, eigen[:,7],'b*')
plt.plot(FI1, eigen[:,8],'b*')
plt.plot(FI1, eigen[:,9],'b*')
plt.xlabel("$U/t$")
#plt.show()


#QUANTUM ALGORITHM: here starts the quantum calculation

#Generation of all Doubles Excitations
test_list = np.arange(0, L, 1).tolist()
res = list(combinations(test_list,2))
Doubles = []
for j1 in range(len(res)):
   for k1 in range(j1+1,len(res)):
      if(common_member(res[j1],res[k1])==False):
         #print(res[j1],res[k1],common_member(res[j1],res[k1]),j1,k1)
         Doubles.append((res[j1],res[k1]))

def Unit(params,Doubles,Hamil,Od):
   x = params
   Full = np.identity(2**L)
   Full1 = np.identity(2**L)
   for j1 in range(len(Doubles)):
      Full = np.matmul(UnD(x[j1],Doubles[j1][0][0],Doubles[j1][0][1],Doubles[j1][1][0],Doubles[j1][1][1],Od),Full)
      Full1 = np.matmul(Full, UnD(-x[j1],Doubles[j1][0][0],Doubles[j1][0][1],Doubles[j1][1][0],Doubles[j1][1][1],Od))
   return np.matmul(np.matmul(Full1,Hamil),Full)

seed=list(np.full(len(Doubles),10))

print(Unit(seed,Doubles,Ham(Ham1,Ham2,0),Op))



