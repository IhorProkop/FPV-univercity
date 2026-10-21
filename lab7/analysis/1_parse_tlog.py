from pathlib import Path
HERE = Path(__file__).resolve().parent          # lab7/analysis
FLIGHT = HERE.parent / "flight"                 # lab7/flight (журнали польоту)
import os; os.chdir(HERE)
from pymavlink import mavutil
import pandas as pd, math, json, datetime
m=mavutil.mavlink_connection(str(FLIGHT / 'mavproxy_mav.tlog'))
rows=[]; boot=None; att_roll=None; att_pitch=None; mode=None; armed=None; hud=None
while True:
    msg=m.recv_match()
    if msg is None: break
    if msg.get_srcSystem()!=1 or msg.get_srcComponent()!=1: continue
    t=msg.get_type()
    if t=='HEARTBEAT': mode=msg.custom_mode; armed=bool(msg.base_mode&128)
    elif t=='ATTITUDE': att_roll=math.degrees(msg.roll); att_pitch=math.degrees(msg.pitch); boot=msg.time_boot_ms
    elif t=='VFR_HUD': hud=(msg.airspeed,msg.groundspeed,msg.alt,msg.climb,msg.throttle)
    elif t=='GLOBAL_POSITION_INT' and hud:
        rows.append(dict(wall=msg._timestamp,boot=msg.time_boot_ms/1000,lat=msg.lat/1e7,lon=msg.lon/1e7,
            alt_rel=msg.relative_alt/1000,alt_amsl=msg.alt/1000,vx=msg.vx/100,vy=msg.vy/100,vz=msg.vz/100,
            gs_calc=math.hypot(msg.vx,msg.vy)/100,airspeed=hud[0],groundspeed=hud[1],climb=hud[3],throttle=hud[4],
            roll=att_roll,pitch=att_pitch,mode=mode,armed=armed))
df=pd.DataFrame(rows)
df.to_pickle('all.pkl')
a=df[df.armed]; i0=a.index[0]; i1=a.index[-1]
print('arm wall',datetime.datetime.fromtimestamp(df.wall[i0]+3*3600),'disarm',datetime.datetime.fromtimestamp(df.wall[i1]+3*3600))
print('arm boot',df.boot[i0],'disarm boot',df.boot[i1],'sim dur',df.boot[i1]-df.boot[i0],'wall dur',df.wall[i1]-df.wall[i0])
print('RTF',(df.boot[i1]-df.boot[i0])/(df.wall[i1]-df.wall[i0]))
for k,g in df.groupby((df['mode']!=df['mode'].shift()).cumsum()):
    print('mode',g['mode'].iloc[0],'armed',g.armed.iloc[0],'boot',g.boot.iloc[0],g.boot.iloc[-1])
print(df.loc[i0-2:i1+2,['alt_rel','airspeed','groundspeed','roll']].describe())
