from pathlib import Path
HERE = Path(__file__).resolve().parent          # lab7/analysis
FLIGHT = HERE.parent / "flight"                 # lab7/flight (журнали польоту)
import os; os.chdir(HERE)
import pandas as pd, numpy as np, math, json, datetime
df=pd.read_pickle('all.pkl')
arm=df[df.armed]; i0,i1=arm.index[0],arm.index[-1]
T0=df.boot[i0]
f=df.loc[i0-8:i1+8].copy(); f['t']=f.boot-T0
ev={'Takeoff':1792520783.6640239,'WP':1792520892.649216,'Reached2':1792521069.5425558,'Disarm':1792521291.029336,'Arm':1792520613.216596}
evt={k:float(df.loc[(df.wall-v).abs().idxmin(),'boot']-T0) for k,v in ev.items()}
print(evt)
def dist(a,b,c,d):
    R=6371000; p1,p2=math.radians(a),math.radians(c); dl=math.radians(d-b); dp=p2-p1
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2; return 2*R*math.asin(math.sqrt(h))
s=df.loc[i0]; e=df.loc[i1]
tgt=(-35.3630965,149.1637991)
cr=f[(f.t>evt['WP'])&(f.t<evt['Reached2'])]
res=dict(arm_wall=str(datetime.datetime.fromtimestamp(df.wall[i0]+3*3600)),disarm_wall=str(datetime.datetime.fromtimestamp(df.wall[i1]+3*3600)),
 sim_dur=df.boot[i1]-T0, wall_dur=df.wall[i1]-df.wall[i0], max_alt=f.alt_rel.max(), t_max_alt=float(f.loc[f.alt_rel.idxmax(),'t']),
 max_gs=f.groundspeed.max(), max_as=f.airspeed.max(), max_roll=f.roll.abs().max(), roll_signed=float(f.loc[f.roll.abs().idxmax(),'roll']), t_roll=float(f.loc[f.roll.abs().idxmax(),'t']),
 max_pitch=f.pitch.abs().max(), max_climb=f.climb.max(), min_climb=f.climb.min(),
 start=(s.lat,s.lon,s.alt_amsl), end=(e.lat,e.lon,e.alt_amsl),
 land_err=dist(e.lat,e.lon,*tgt), path=dist(s.lat,s.lon,e.lat,e.lon), plan_dist=dist(s.lat,s.lon,*tgt),
 cruise_alt_mean=cr.alt_rel.mean(), cruise_alt_min=cr.alt_rel.min(), cruise_alt_max=cr.alt_rel.max(),
 cruise_gs_mean=cr[cr.groundspeed>3.5].groundspeed.mean(), evt=evt)
# time at which reached 45
c=f[(f.t>evt['Takeoff'])]; res['t_reach45']=float(c[c.alt_rel>=44.5].t.iloc[0])
# avg climb in auto takeoff between 5 and 40 m
seg=f[(f.t>evt['Takeoff'])&(f.alt_rel>5)&(f.alt_rel<40)]; res['climb_avg']=seg.climb.mean()
seg=f[(f.t>evt['Reached2'])&(f.alt_rel>12)&(f.alt_rel<40)]; res['desc_hi']=seg.climb.mean()
seg=f[(f.t>evt['Reached2'])&(f.alt_rel>1)&(f.alt_rel<8)]; res['desc_lo']=seg.climb.mean()
res['guided_alt']=f[(f.t>5)&(f.t<evt['Takeoff'])].alt_rel.mean()
print(json.dumps(res,indent=1,default=float))
json.dump(res,open('stats.json','w'),default=float,indent=1)
f.to_pickle('flight.pkl')
