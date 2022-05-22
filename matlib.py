# Available by courtesy of Assoc. Prof. Nils Petter Vedvik, NTNU

materials = []

# The materials used in TMM4175 assignment 05, problem 2

materials.append( {"name": "E-glass/Epoxy", "units": "MPa-mm-Mg", "type": "UD", "fiber": "E-glass",
                   "Vf": 0.55, "rho": 2000E-12,
                   "description": "Typical UD E-glass/Epoxy from TMM4175",
                   "E1": 40000, "E2": 10000, "E3": 10000,
                   "v12": 0.3, "v13": 0.3, "v23": 0.4,
                   "G12": 3800, "G13": 3800, "G23": 3400,
                   "a1": 7e-06, "a2": 2.2e-05, "a3": 2.2e-05,
                   "XT": 1000, "YT": 40, "ZT": 40,
                   "XC": 700, "YC": 120, "ZC": 120,
                   "S12": 70, "S13": 70, "S23": 40,
                   "f12": -0.5, "f13": -0.5, "f23": -0.5} )

materials.append( {"name": "Carbon/Epoxy(a)", "units": "MPa-mm-Mg", "type": "UD", "fiber": "Carbon",
                   "Vf": 0.55, "rho": 1600E-12,
                   "description": "Typical low modulus carbon/Epoxy from TMM4175",
                   "E1": 130000, "E2": 10000, "E3": 10000,
                   "v12": 0.28, "v13": 0.28, "v23": 0.5,
                   "G12": 4500, "G13": 4500, "G23": 3500,
                   "a1": -0.5e-06, "a2": 3.0e-05, "a3": 3.0e-05,
                   "XT": 1800, "YT": 40, "ZT": 40,
                   "XC": 1200, "YC": 180, "ZC": 180,
                   "S12": 70, "S13": 70, "S23": 40,
                   "f12": -0.5, "f13": -0.5, "f23": -0.5} )


def get(matname):
    for m in materials:
        if m['name'] == matname:
            return m
    return False


def printlist():
    for m in materials:
        print(m['name'])


def newMaterial(**kwargs):
    m = {}
    for key in kwargs:
        m.update({key: kwargs[key]})
    return m