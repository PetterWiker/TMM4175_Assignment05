import laminatelib
import copy


class Ply:

    def __init__(self, material: dict, orientation: int, thickness: float) -> None:
        """
        Simple class for storing ply information in an object.
        :param material: The material comprising the ply. On the format used in "matlib.py".
        :param orientation: The ply orientation in degrees relative to the xyz-coordinate system.
        :param thickness: The thickness of the ply.
        """
        self.material = copy.deepcopy(material)  # Deepcopy to remove pointer to original material, allowing for change
        self.orientation = orientation
        self.thickness = thickness
        self.Te = laminatelib.T2De(self.orientation)
        self.Q = laminatelib.Q2D(self.material)
        pass
