import pyreadstat
import pandas as pd

zone_map = {1:'NC',2:'NE',3:'NW',4:'SE',5:'SS',6:'SW'}
zone_labels = {'NC':'N.Central','NE':'N.East','NW':'N.West',
               'SE':'S.East','SS':'S.South','SW':'S.West'}

ir, _ = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGIR8BDT/NGIR8BFL.dta")
ir['zone'] = ir['v024'].astype(int).map(zone_map)
ir['any_anaemia'] = (ir['v457'].astype(float) < 4).astype(int)
ir_sub = ir[ir['v457'].notna()].copy()

kr, _ = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGKR8BDT/NGKR8BFL.dta")
kr['zone'] = kr['v024'].astype(int).map(zone_map)
kr['haz'] = kr['hw70'] / 100
kr['whz'] = kr['hw71'] / 100
kr.loc[kr['haz'].abs() > 6, 'haz'] = None
kr.loc[kr['whz'].abs() > 6, 'whz'] = None

hr, _ = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGHR8BDT/NGHR8BFL.dta")
hr['zone'] = hr['hv024'].astype(int).map(zone_map)
hr['unimproved_water'] = hr['hv201'].isin([32,42,43,96]).astype(int)
hr['poor_sanitation'] = hr['hv205'].isin([23,41,51,96]).astype(int)
hr['solid_fuel'] = hr['hv226'].isin([6,7,8,9,10]).astype(int)

print(f"{'Zone':<11} {'Stunting':>9} {'Wasting':>8} {'W.Anaemia':>10} {'Unimpr.Water':>13} {'PoorSanit':>10} {'SolidFuel':>10}")
print("-" * 76)

for z in ['NC','NE','NW','SE','SS','SW']:
    kr_z = kr[kr['zone']==z]
    stunt = (kr_z[kr_z['haz'].notna()]['haz'] < -2).mean()*100
    waste = (kr_z[kr_z['whz'].notna()]['whz'] < -2).mean()*100
    anaem = ir_sub[ir_sub['zone']==z]['any_anaemia'].mean()*100
    water = hr[hr['zone']==z]['unimproved_water'].mean()*100
    sanit = hr[hr['zone']==z]['poor_sanitation'].mean()*100
    fuel  = hr[hr['zone']==z]['solid_fuel'].mean()*100
    print(f"{zone_labels[z]:<11} {stunt:>8.1f}% {waste:>7.1f}% {anaem:>9.1f}% {water:>12.1f}% {sanit:>9.1f}% {fuel:>9.1f}%")
