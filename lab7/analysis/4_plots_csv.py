from pathlib import Path
HERE = Path(__file__).resolve().parent          # lab7/analysis
FLIGHT = HERE.parent / "flight"                 # lab7/flight (журнали польоту)
import os; os.chdir(HERE)
import pandas as pd, matplotlib, json
matplotlib.use('Agg'); import matplotlib.pyplot as plt
df=pd.read_csv(FLIGHT / '2026-10-20 21-23-33 vehicle1.csv')
df['ts']=pd.to_datetime(df.Timestamp); df['t']=(df.ts-df.ts[0]).dt.total_seconds()
df['alt']=df.altitudeRelative*0.3048; df['as_']=df.airSpeed*0.44704; df['gs']=df.groundSpeed*0.44704
ft=df.flightTime.astype(str)
dis=df.index[ft==ft.iloc[-1]][0]   # first row where flightTime froze = disarm
f=df.loc[:dis+10].copy()
mi=f.missionItemIndex
def first(cond): return float(f.t[cond].iloc[0])
lift=first(f.alt>0.3); tko=first((mi==1)&(f.alt>3.2)); wp=first(mi==2); ld=first(mi==3); td=first((mi==3)&(f.alt<=0.05)); tdis=float(f.t[dis])
ev=dict(lift=lift,auto_takeoff=tko,wp=wp,land=ld,touchdown=td,disarm=tdis)
print(ev)
res=dict(ev=ev,max_alt=f.alt.max(),max_as=f.as_.max(),max_gs=f.gs.max(),max_roll=f.roll.abs().max(),roll_signed=float(f.roll[f.roll.abs().idxmax()]),
 start=(f['gps.lat'].iloc[0],f['gps.lon'].iloc[0]),end=(f['gps.lat'].iloc[dis],f['gps.lon'].iloc[dis]),flight_time=ft.iloc[-1],
 t0=str(df.Timestamp[0]),t_lift=str(f.Timestamp[f.alt>0.3].iloc[0]),t_dis=str(f.Timestamp[dis]),dist_home=f.distanceToHome.iloc[dis]*0.3048,
 cruise_alt=f.alt[mi==2].mean(), cruise_gs=f.gs[(mi==2)&(f.gs>3.8)].mean(), dis_row=int(dis))
print(json.dumps(res,indent=1,default=float)); json.dump(res,open('csvstats.json','w'),default=float,indent=1)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#555'})
ph=[(0,tko,'GUIDED:\nзліт до 3 м'),(tko,wp,'AUTO:\nнабір 45 м'),(wp,ld,'AUTO:\nпереліт'),(ld,tdis,'AUTO:\nпосадка')]
def plot(col,yl,title,fn,ref,rl):
    fig,ax=plt.subplots(figsize=(8.6,3.9),dpi=200); ymax=f[col].max()*1.32
    for (a,b,l),c in zip(ph,['#f2f2f2','#e6e6e6','#f2f2f2','#e6e6e6']):
        ax.axvspan(a,b,color=c,lw=0,zorder=0); ax.text((a+b)/2,ymax*0.97,l,ha='center',va='top',fontsize=8,color='#555')
    ax.axhline(ref,color='#999',lw=1,ls='--',zorder=1); ax.text(f.t.max(),ref,f' {rl}',va='bottom',ha='right',fontsize=8,color='#666')
    ax.plot(f.t,f[col],color='#1f5fa8',lw=2,zorder=2)
    ax.set_xlim(0,f.t.max()); ax.set_ylim(0,ymax); ax.set_xlabel('Час від армування за CSV (реальний час), с'); ax.set_ylabel(yl)
    ax.set_title(title,loc='left',fontsize=11,fontweight='bold'); ax.grid(axis='y',color='#ddd',lw=0.6); fig.tight_layout(); fig.savefig('figures/'+fn); plt.close(fig)
plot('alt','Висота над точкою старту, м','Висота польоту (CSV: altitudeRelative)','c_alt.png',45,'план 45 м')
plot('as_','Повітряна швидкість, м/с','Повітряна швидкість (CSV: airSpeed)','c_as.png',4,'WP_SPD = 4 м/с')
plot('gs','Наземна швидкість, м/с','Наземна швидкість (CSV: groundSpeed)','c_gs.png',4,'WP_SPD = 4 м/с')
f.to_pickle('csvflight.pkl')
