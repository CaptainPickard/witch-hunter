"""Offline: L_Hand <-> R_Hand local-frame mirror map at bind pose (Order B, throwaway)."""
import struct, json
import numpy as np
exec(open("scratch/measure_hand_basis.py").read().split("# ---- pick a bin chunk")[0])
def rot(i):
    U, S, Vt = np.linalg.svd(world_matrix(i)[:3, :3]); return U @ Vt
WL, WR = rot(name_to_idx("L_Hand")), rot(name_to_idx("R_Hand"))
Sx = np.diag([-1., 1., 1.])
print("L origin", world_matrix(name_to_idx("L_Hand"))[:3, 3].round(3), "R origin", world_matrix(name_to_idx("R_Hand"))[:3, 3].round(3))
M_LtoR = WR.T @ Sx @ WL
print("L-local -> R-local mirror map:\n", M_LtoR.round(3))
print("R-local -> L-local mirror map:\n", (WL.T @ Sx @ WR).round(3))
print("det", np.linalg.det(M_LtoR).round(3))
