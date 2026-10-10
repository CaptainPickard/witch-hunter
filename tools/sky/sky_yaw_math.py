#!/usr/bin/env python3
"""Compute the dome yawDeg for the moon-contract night panos.

Measured contract (vision QA): moon u = 0.21..0.25 from LEFT; use 0.22 mean.
Three.js sphere inside-look: texture u=0 sits at -x when yaw=0 and view
bearing sweeps -x, -z at u=0.25, +x at u=0.5, +z at u=0.75 (u increases
counterclockwise seen from above). We want the moon (u 0.22) to sit to the
player's LEFT of the graveyard path bearing.

Region B (darkwood_edge, where the bonfire+graveyard path tutorial runs):
the path to the graveyard gate runs roughly NORTH (-z). Player walking the
path looks toward -z (u=0.25 at yaw=0 is exactly -z). 'A little to the
player's left' means slightly WEST of -z => bearing ~ -z rotated ~15-20 deg
toward -x.

u(bearing) = 0.25 - bearingFromNegZ_ccw/360 ... solving for yaw:
u = (0.25 - (bearingFromNegZ_ccw)/360 - yaw/360) mod 1
want u_moon = 0.22 at bearing = -18 deg (18 deg left of -z):
0.22 = 0.25 + 18/360 - yaw/360  =>  yaw = 360*(0.25 + 0.05 - 0.22) = 28.8
Sanity: old set had moon at u~0.70 with yaw 162 -> bearing = 360*(0.25+0.05-... )
check: bearing = 360*(0.25 + yaw/360 - 0.70)= 360*0.25 + 162 - 252 = 0 => yaw 162 put moon
at -z too... but the old QA said moon sat at azimuth 0 (-z) - consistent.
"""
def yaw_for(u_moon, bear_left_of_negz_deg):
    return 360 * (0.25 + bear_left_of_negz_deg / 360.0 - u_moon)

# moon slightly LEFT of the path (-z), 18 deg toward -x
print('yawDeg for u=0.22, 18deg left of -z:', round(yaw_for(0.22, 18), 1))
print('yawDeg for u=0.25 (dead-on -z):', round(yaw_for(0.25, 18), 1))
print('yawDeg for u=0.21 (more left):', round(yaw_for(0.21, 18), 1))