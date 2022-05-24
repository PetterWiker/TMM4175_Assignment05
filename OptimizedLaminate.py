from Assignment05 import matlib
from Assignment03 import laminatelib
from Laminate import Laminate
from Ply import Ply


class OptimizedLaminate(Laminate):

    def __init__(self, laminate: Laminate, ply_thickness: float, load_case: dict, deformation_limits: list) -> None:
        ABD = laminate.compute_ABD()
        loads, deformations = laminatelib.solveLaminateLoadCase(ABD, **load_case)

        exposure_factors = []
        for idx, deformation_limit in enumerate(deformation_limits):
            if deformation_limit is not None:
                exposure_factors.append(deformations[idx]/deformation_limit)

        # It is assumed that the adjustment_factor has a value between 0 and 1.
        # If not, the laminate is broken and cannot be optimized by reducing the ply thickness.
        adjustment_factor = max(exposure_factors)

        updated_layup = []
        for ply in laminate.layup:
            optimized_combined_layer_thickness = ply.thickness*adjustment_factor
            n_new_plies_per_combined_layer = optimized_combined_layer_thickness // ply_thickness
            if optimized_combined_layer_thickness % ply_thickness:
                n_new_plies_per_combined_layer += 1
            for i in range(int(n_new_plies_per_combined_layer)):
                updated_layup.append(Ply(material=ply.material, orientation=ply.orientation, thickness=ply_thickness))

        super().__init__(layup=updated_layup, name="Optimized_{}".format(laminate.name))

        # The mass reduction is directly related to the thickness_reduction
        self.mass_reduction = (1 - self.thickness/laminate.thickness)*100
        self.suboptimal_laminate = laminate
        self.optimized_load_case = load_case
        pass

    def __repr__(self) -> str:
        return "I am the {} mm thick optimized laminate '{}' that " \
               "saved you {} % mass over the {} mm thick suboptimal laminate" \
               " '{}' for the load case {}. Nice!".format(round(self.thickness, 2),
                                                          self.name,
                                                          round(self.mass_reduction, 2),
                                                          round(self.suboptimal_laminate.thickness, 2),
                                                          self.suboptimal_laminate.name,
                                                          self.optimized_load_case)


def main():
    material = matlib.get("Kevlar-49/Epoxy")

    THICKNESS = 1
    ALTERNATIVE_THICKNESS = 0.1
    LOAD_CASE = {"Nx": 600, "Nxy": 300}
    DEFORMATION_LIMITS = [0.005, None, 0.005]

    layup = [Ply(material=material, orientation=0,   thickness=THICKNESS),
             Ply(material=material, orientation=45,  thickness=THICKNESS),
             Ply(material=material, orientation=-45, thickness=THICKNESS),
             Ply(material=material, orientation=-45, thickness=THICKNESS),
             Ply(material=material, orientation=45,  thickness=THICKNESS),
             Ply(material=material, orientation=0,   thickness=THICKNESS)]

    laminate = Laminate(layup=layup, name="Kevlar_Laminate")
    optimized_laminate = OptimizedLaminate(laminate=laminate,
                                           ply_thickness=ALTERNATIVE_THICKNESS,
                                           load_case=LOAD_CASE,
                                           deformation_limits=DEFORMATION_LIMITS)
    print(optimized_laminate)

    pass


if __name__ == "__main__":
    main()
