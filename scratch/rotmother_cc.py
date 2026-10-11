import sys,trimesh,numpy as np
m=trimesh.load(sys.argv[1],force='mesh',process=False)
print('bounds',m.bounds.round(3).tolist(), 'v',len(m.vertices),'f',len(m.faces))
m2=trimesh.Trimesh(m.vertices,m.faces,process=True)
cc=trimesh.graph.connected_component_labels(m2.face_adjacency,node_count=len(m2.faces))
n=np.bincount(cc); o=np.sort(n)[::-1]
print('components',len(n),'largest',o[:8].tolist(),'faces outside largest',int(n.sum()-o[0]), f'({(n.sum()-o[0])/n.sum()*100:.3f}%)')
