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

    def calculate_laminate_properties(self) -> tuple:
        Ex = (1/self.thickness)*(self.A[0, 0]-self.A[0, 1]**2/self.A[1, 1])
        Ey = (1/self.thickness)*(self.A[1, 1]-self.A[0, 1]**2/self.A[0, 0])
        Gxy = (1/self.thickness)*self.A[2, 2]
        vxy = self.A[0, 1]/self.A[1, 1]
        return Ex, Ey, Gxy, vxy
