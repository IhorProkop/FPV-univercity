from pathlib import Path
HERE = Path(__file__).resolve().parent          # lab7/analysis
FLIGHT = HERE.parent / "flight"                 # lab7/flight (журнали польоту)
import os; os.chdir(HERE)
import pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
f=pd.read_pickle('flight.pkl'); s=json.load(open('stats.json')); e=s['evt']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#555','axes.labelcolor':'#222','xtick.color':'#444','ytick.color':'#444'})
ph=[(0,e['Takeoff'],'GUIDED:\nзліт до 3 м'),(e['Takeoff'],e['WP'],'AUTO:\nнабір 45 м'),(e['WP'],e['Reached2'],'AUTO:\nпереліт до цілі'),(e['Reached2'],e['Disarm'],'AUTO:\nпосадка (LAND)')]
shade=['#f2f2f2','#e6e6e6','#f2f2f2','#e6e6e6']
def plot(col,ylabel,title,fn,ref=None,reflabel=None):
    fig,ax=plt.subplots(figsize=(8.6,3.9),dpi=200)
    ymax=f[col].max()*1.32 if f[col].max()>0 else 1
    for (a,b,l),c in zip(ph,shade):
        ax.axvspan(a,b,color=c,lw=0,zorder=0)
        ax.text((a+b)/2,ymax*0.97,l,ha='center',va='top',fontsize=8,color='#555')
    if ref is not None:
        ax.axhline(ref,color='#999',lw=1,ls='--',zorder=1); ax.text(f.t.max(),ref,f' {reflabel}',va='bottom',ha='right',fontsize=8,color='#666')
    ax.plot(f.t,f[col],color='#1f5fa8',lw=2,zorder=2)
    ax.set_xlim(-3,f.t.max()); ax.set_ylim(0,ymax)
    ax.set_xlabel('Час симуляції від армування, с'); ax.set_ylabel(ylabel); ax.set_title(title,loc='left',fontsize=11,fontweight='bold')
    ax.grid(axis='y',color='#ddd',lw=0.6); fig.tight_layout(); fig.savefig('figures/'+fn); plt.close(fig)
plot('alt_rel','Висота над точкою старту, м','Висота польоту (relative_alt)','g_alt.png',45,'план 45 м')
plot('airspeed','Повітряна швидкість, м/с','Повітряна швидкість (VFR_HUD.airspeed)','g_as.png',4,'WP_SPD = 4 м/с')
plot('groundspeed','Шляхова швидкість, м/с','Шляхова швидкість (VFR_HUD.groundspeed)','g_gs.png',4,'WP_SPD = 4 м/с')
# trajectory top view
import math
lat0,lon0=s['start'][0],s['start'][1]
x=(f.lon-lon0)*111320*math.cos(math.radians(lat0)); y=(f.lat-lat0)*110574
fig,ax=plt.subplots(figsize=(8.6,3.0),dpi=200)
ax.plot(x,y,color='#1f5fa8',lw=2,label='фактична траєкторія')
tx=(149.1637991-lon0)*111320*math.cos(math.radians(lat0)); ty=(-35.3630965-lat0)*110574
ax.plot([0,tx],[0,ty],'--',color='#999',lw=1,label='план')
ax.scatter([0],[0],s=60,color='#222',zorder=3); ax.annotate('H / старт',(0,0),xytext=(-10,8),textcoords='offset points',ha='right',fontsize=9)
ax.scatter([tx],[ty],s=80,marker='x',color='#c0392b',zorder=3); ax.annotate('ціль варіанту 17',(tx,ty),xytext=(8,8),textcoords='offset points',fontsize=9)
ax.set_aspect('equal'); ax.set_xlabel('Схід, м'); ax.set_ylabel('Північ, м'); ax.set_title('Траєкторія у плані (вид згори)',loc='left',fontsize=11,fontweight='bold')
ax.grid(color='#eee',lw=0.6); ax.legend(frameon=False,fontsize=8,loc='upper right'); ax.set_ylim(-10,40)
fig.tight_layout(); fig.savefig('figures/g_traj.png'); plt.close(fig)
