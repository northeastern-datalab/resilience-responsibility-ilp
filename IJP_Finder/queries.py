"""
Queries for which ASP can be generated.
A CQ here is represented by a list of atoms - where each atom (R, [v]) has a relation and list of variables.
"""

queries = {
    "3Star": [ ("R",['x']), ("S",['y']), ("T",['z']), ("W",['x', 'y', 'z']) ], # hard
    "SJ-chain": [ ("R",['x','y']), ("R",['y','z']) ], # hard
    "SJ-conf": [ ("R",['x','y']), ("R",['x','z']), ("A", ['y']), ("B", ['z'])],
    "SJ-3-chain": [("R",['x','y']), ("R",['y','z']), ("R",['z','w'])], # hard
    "SJ-3-conf-ac": [("A",['x']),("R",['x','y']), ("R",['z','y']), ("R",['z','w']),("C",['w'])], # hard
    "SJ-3-conf-as": [("A",['x']),("R",['x','y']), ("R",['z','y']), ("R",['z','w']),("S",['z','w'])], # unknown
    "SJ-3-chain-conf-s": [("R",['x','y']), ("R",['y','z']), ("R",['w','z']),("S",['w','z'])], # unknown - shown hard now
    "SJ-3-perm-R-ASxy": [("A",['x']),("S",['x','y']),("R",['x','y']), ("R",['y','z']), ("R",['z','y'])], # unknown - shown hard now    
    "SJ-3-perm-R-SxyB": [("S",['x','y']),("R",['x','y']),("B",['y']), ("R",['y','z']), ("R",['z','y'])], # unknown - shown hard now    
    "SJ-3-perm-R-SxyC": [("S",['x','y']),("R",['x','y']),("R",['y','z']), ("R",['z','y']),("C",['z']),], # unknown - shown hard now    
    "SJ-z5": [("A",['x']),("R",['x','y']),("R",['y','z']), ("R",['z','z'])], # known hard
    "SJ-z6": [("A",['x']),("R",['x','y']),("R",['y','y']), ("R",['y','z']),("C",['z'])], # unknown - shown hard now 
    "SJ-z7": [("A",['x']),("R",['x','y']),("R",['y','x']), ("R",['y','y'])], # unknown    
}