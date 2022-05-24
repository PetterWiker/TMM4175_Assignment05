import laminatelib
import numpy as np
from numpy import ndarray
import copy

from Ply import Ply


class Laminate:

    def __init__(self, layup: list[Ply], name: str) -> None:
        """
        Class for modeling the in-plane properties of a laminate comprised of a stack of plies (using the "Ply"-class).
        :param layup: A list of "Ply"-objects.
        :param name: A chosen name for the laminate.
        """
        self.layup = copy.deepcopy(layup)
        self.name = name
        self.thickness = self.compute_thickness()
        self.A = self.compute_A()
        pass

    def compute_thickness(self) -> float:
        return sum([ply.thickness for ply in self.layup])

    def compute_A(self) -> ndarray:
        A = np.zeros((3, 3), float)
        h_bot = -self.thickness/2
        for ply in self.layup:
            Q = laminatelib.Q2D(ply.material)
            Qt = laminatelib.Q2Dtransform(Q, ply.orientation)
            h_top = h_bot + ply.thickness
            A += Qt*(h_top-h_bot)
            h_bot = h_top
        return A

    def compute_ABD(self):
        ABD = np.zeros((6, 6), float)
        h_bot = -self.thickness/2
        for ply in self.layup:
            Q = laminatelib.Q2D(ply.material)
            Qt = laminatelib.Q2Dtransform(Q, ply.orientation)
            h_top = h_bot + ply.thickness
            ABD[0:3,0:3] += Qt*(h_top-h_bot)
            ABD[0:3,3:6] += (1/2)*Qt*(h_top**2-h_bot**2)
            ABD[3:6,0:3] += (1/2)*Qt*(h_top**2-h_bot**2)
            ABD[3:6,3:6] += (1/3)*Qt*(h_top**3-h_bot**3)
            h_bot = h_top
        return ABD

    def calculate_laminate_properties(self) -> tuple:
        Ex = (1/self.thickness)*(self.A[0, 0]-self.A[0, 1]**2/self.A[1, 1])
        Ey = (1/self.thickness)*(self.A[1, 1]-self.A[0, 1]**2/self.A[0, 0])
        Gxy = (1/self.thickness)*self.A[2, 2]
        vxy = self.A[0, 1]/self.A[1, 1]
        return Ex, Ey, Gxy, vxy
