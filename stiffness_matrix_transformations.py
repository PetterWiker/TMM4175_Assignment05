import numpy as np
from Assignment02 import laminatelib

# Engineering constants for the orthotropic material in the 1'-2'-3' coordinate system
E_1 = 50
E_2 = 20
E_3 = 10
v_12 = 0.25
v_13 = 0.30
v_23 = 0.35
G_23 = 3
G_13 = 4
G_12 = 5


# The compliance matrix S' in the 1'-2'-3' coordinate system
S_bar = np.array([[   1/E_1, -v_12/E_1, -v_13/E_1,      0,      0,      0],
                 [-v_12/E_1,     1/E_2, -v_23/E_2,      0,      0,      0],
                 [-v_13/E_1, -v_23/E_2,     1/E_3,      0,      0,      0],
                 [0,                 0,         0, 1/G_23,      0,      0],
                 [0,                 0,         0,      0, 1/G_13,      0],
                 [0,                 0,         0,      0,      0, 1/G_12]])

# The stiffness matrix C' in the 1'-2'-3' coordinate system corresponds to the inverted compliance matrix
C_bar = np.linalg.inv(S_bar)

# The following rotations are outlined in the report. The stiffness matrices in the coordinate system 1-2-3 is obtained.
C_A = np.dot(np.linalg.inv(laminatelib.T3Dsx(90)),
             np.dot(C_bar,
                    laminatelib.T3Dex(90)))

C_B = np.dot(np.linalg.inv(laminatelib.T3Dsz(90)),
             np.dot(C_bar,
                    laminatelib.T3Dez(90)))

C_C = np.dot(np.linalg.inv(laminatelib.T3Dsx(90)),
             np.dot(np.dot(np.linalg.inv(laminatelib.T3Dsz(-90)),
                           np.dot(C_bar,
                                  laminatelib.T3Dez(-90))),
                    laminatelib.T3Dex(90)))

# Print the matrices to find that they are indeed what was calculated through substitution of axis.
np.set_printoptions(precision=2, suppress=True)
print("The stiffness matrix in the 1-2-3 coordinate system for case A:\n", C_A, "\n")
print("The stiffness matrix in the 1-2-3 coordinate system for case B:\n", C_B, "\n")
print("The stiffness matrix in the 1-2-3 coordinate system for case C:\n", C_C, "\n")

