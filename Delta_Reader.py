import numpy as np
import csv
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import myconst as mc
import random

#for identifiying event number and the number of particles in the event
def h_read(header):
  e_num=int(header[0])
  numPart=int(header[1])
  return e_num, numPart


#distance formula: sqrt(x1^2+x2^2+...+xn^2)
def dist_form(vec):
  vsum2=0
  for i in range(0,len(vec)):
    vsum2+=vec[i]**2
  return np.sqrt(vsum2)  

#sum of two vectors
def v_sum(v1,v2):
  vtot=[]
  for i in range (0,len(v1)):
    vtot.append(v1[i]+v2[i]) 
  return vtot

#given total energy and rest mass, calculate the Lorentz factor and relative velocity
def gam_calc(En,m0):
  gam=En/m0
  return gam

#LT in 3D space in matrix form
def gam_mat(gam,v,vx,vy,vz,p4):
    A=np.array([[gam,-gam*vx,-gam*vy,-gam*vz],
                [-gam*vx,1+(gam-1)*vx**2/v**2,(gam-1)*vx*vy/v**2,(gam-1)*vx*vz/v**2],
                [-gam*vy,(gam-1)*vx*vy/v**2,1+(gam-1)*vy**2/v**2,(gam-1)*vy*vz/v**2],
                [-gam*vz,(gam-1)*vx*vz/v**2,(gam-1)*vy*vz/v**2,1+(gam-1)*vz**2/v**2]])
    return np.dot(A,p4)

#find the invariant mass given the total energy and the momentum
def inv_m(en,p):
  m2=en**2-p**2
  return np.sqrt(m2)

def IM_method(plist,pilist):
  m_list=[]
  mnt_list=[]
  for i in range(0,len(pilist)):
    for j in range(0,len(plist)):
      Ep=float(plist[j][0]) #total E of p
      Epi=float(pilist[i][0]) #total E of pi
      pp=[]
      ppi=[]
      for k in range(0,3):
        pp.append(float(plist[j][k+1])) #3D momentum of p
        ppi.append(float(pilist[i][k+1])) #3D momentum of pi
      ptot=v_sum(pp,ppi) #total momentum of the two particles
      pmag=dist_form(ptot) #magnitude of the total momentum
      Etot=Ep+Epi #total energy of the two particles
      
      #move to the "delta" frame assuming the pair can create one
      gam=gam_calc(Etot,mc.m_del0)
      if gam<1:
        continue
      v=np.sqrt(1-1/gam**2)

      vx=ptot[0]/(gam*mc.m_del0)
      vy=ptot[1]/(gam*mc.m_del0)
      vz=ptot[2]/(gam*mc.m_del0)

      p4p=[Ep]+pp #4 momentum of p in lab frame
      p4pi=[Epi]+ppi #4 momentum of pi in lab frame
      ptest=gam_mat(gam,v,vx,vy,vz,p4p) #4 momentum of p in delta frame
      pitest=gam_mat(gam,v,vx,vy,vz,p4pi) #4 momentum of pi in delta frame
      pt_tot=v_sum(ptest,pitest)
      pt_mag=dist_form(pt_tot[1:])
      

      #momentum cut
      if pt_mag < mc.p_cut:
        mdel_rec=inv_m(Etot,pmag)
        m_list.append(mdel_rec)
        #mass cut
        if abs(mdel_rec-mc.m_del0)<mc.m_cut and pmag<mc.pd_max:
          mnt_list.append(pmag)

  return m_list, mnt_list

#for fitting
def poly_func(x,c0,c1,c2,c3,c4):
  return c0+c1*x+c2*x**2+c3*x**3+c4*x**4

def r2_calc(f,x,y,p):
  res=[]
  ss_res=[]
  ss_tot=[]
  m=np.mean(y)
  for i in range(0,len(x)):
    r=y[i]-f(x[i],*p)
    res.append(r)
    ss_res.append(r**2)
    ss_tot.append((y[i]-m)**2)
  ssr=np.sum(ss_res)
  sst=np.sum(ss_tot)
  return 1-(ssr/sst)


#csv file to save invariant mass data of all events
with open('data_IM.csv','w') as fm:
  fm.close()


IM_list=[] #the invariant mass of the pairs from all events

momentum_list=[] #the momenta of recreated deltas

#open data file, do a momentum cut, and calculate the invariant mass of the particle pairs
with open("data.csv",'r') as file:
  f=csv.reader(file, delimiter=',')
  for row in f:
    #momenta of protons and pions
    p_list=[]
    pi_list=[]
    eventNum,partNum=h_read(row)

    for i in range(0,partNum):
      rowdata=next(f)
      PID=int(rowdata[0]) #identify the particle with PDG codes
      if PID==2212: #proton
        p_list.append(rowdata[1:5])
      elif PID==211: #pion+
        pi_list.append(rowdata[1:5])

    #invariant mass of the p and pi in the event with momentum cut applied
    #random.shuffle(p_list)
    #random.shuffle(pi_list)
    m_list,mnt_list=IM_method(p_list,pi_list)

    for kk in range(0,len(m_list)):
      IM_list.append(m_list[kk])
    for ll in range(0,len(mnt_list)):
      momentum_list.append(mnt_list[ll])
    
    with open('data_IM.csv','a',newline='') as fm:
      g=csv.writer(fm,delimiter=',')
      g.writerow(m_list)
      fm.close()



  file.close()
  
#graphing and fitting
#mass cut done with the fitting
binsize=1 #in MeV/c^2
plt.figure()
hist,bins,packages=plt.hist(IM_list,bins=np.arange(int(mc.md_min)-1,int(mc.md_max)+1,binsize))
stp=int(mc.m_cut/binsize) #determines the width of the cut
x_omit=int(np.where(bins==mc.m_del0)[0][0]) #omit the inv mass of delta
#data to be consider for the fitting of the "noise"
x_start=np.where(hist>0.05*max(hist))[0][0]
x_end=np.where(hist[x_start:]<0.05*max(hist))[0][0]
x_new=bins[x_start:x_omit-stp].tolist()+bins[x_omit+stp+1:x_start+x_end].tolist()
y_new=hist[x_start:x_omit-stp].tolist()+hist[x_omit+stp+1:x_start+x_end].tolist()
#data to be considered for counting the number of deltas
x_skipped=bins[x_omit-stp:x_omit+stp]
y_skipped=hist[x_omit-stp:x_omit+stp]
print(x_skipped)
#fitting
xplt=np.arange(bins[x_start],bins[x_start+x_end],0.5)
ini_g=[0,0,0,0,0]
popt,pcov=curve_fit(poly_func, x_new,y_new,ini_g)
yplt=poly_func(xplt,*popt)
r2_poly=r2_calc(poly_func,x_new,y_new,popt)
r=str(round(r2_poly,5))
plt.plot(xplt,yplt,label='poly fit \n R^2=%s'%(r))
plt.plot(x_skipped,y_skipped,'.')
#plt.plot(x_skipped,poly_func(x_skipped,*popt),'.')
#guessing count
y_est=[]
for i in range(0,len(x_skipped)):
  xi=np.where(xplt==x_skipped[i])[0][0]
  y_est.append(y_skipped[i]-yplt[xi])

print("estimated number of deltas:",sum(y_est))

plt.title("Invariant Mass of Proton and Pion Pairs in Lab Frame")
plt.ylabel("Count")
plt.xlabel("Mass (MeV/c^2)")
plt.legend(loc='upper right')
plt.ylim(0,max(hist)*1.1)
plt.figtext(0.75,0.65,"m_err=%d \n p_min=%d"%(mc.m_cut,mc.p_cut),horizontalalignment='center',verticalalignment='center',bbox=dict(facecolor='none',edgecolor='black'))
plt.savefig("IM_pairs.png")
plt.show()
plt.close()

print("total number of counted particles after momentum cut:", np.sum(hist))



#efficiency over momentum

act_list=[]

with open("actual_del.csv",'r') as fa:
  fd=csv.reader(fa, delimiter=',')
  for row in fd:
    act_list.append(float(row[1]))
  fa.close()

binsize_new=5
plt.figure()
hist_rec,bins_rec,pack_rec=plt.hist(momentum_list,bins=np.arange(0,int(max(momentum_list))+1,binsize_new))
plt.title("Momenta of Recreated Deltas")
plt.xlabel("Momentum (MeV/c)")
plt.ylabel("Count")
plt.savefig("del_mnt_rec.png")
plt.show()
plt.close()

plt.figure()
hist_act,bins_act,packages_act=plt.hist(act_list,bins=bins_rec)
plt.title("Momenta of Actual Deltas")
plt.xlabel("Momentum (MeV/c)")
plt.ylabel("Count")
plt.savefig("del_mnt_act.png")
plt.show()
plt.close()

eff_list=[]
eff_err=[]

for i in range(0,len(bins_act)-1):
  if hist_rec[i] == 0:
    eff_list.append(0)
  else:
    eff_list.append(hist_act[i]/hist_rec[i])
  rec_err=np.sqrt(hist_rec[i]*(1-hist_rec[i]/len(hist_rec)))
  act_err=np.sqrt(hist_act[i]*(1-hist_act[i]/len(hist_act)))
  if hist_act[i]==0 or hist_rec[i]==0:
    eff_err.append(0)
  else:
    eff_err.append((hist_act[i]/hist_rec[i])*np.sqrt((act_err/hist_act[i])**2+(rec_err/hist_rec[i])**2))

plt.figure()
plt.plot(bins_rec[:-1],eff_list,'.')
plt.errorbar(bins_rec[:-1],eff_list,xerr=binsize_new/2,yerr=eff_err,linestyle='none')
plt.title("Efficiency vs Momentum")
plt.xlabel("Momentum (MeV/c)")
plt.ylabel("Efficiency (Actual/Recreated)")
plt.savefig("mnt_eff.png")
plt.show()
plt.close()