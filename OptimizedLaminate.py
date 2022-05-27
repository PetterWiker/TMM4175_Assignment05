import copy
from operator import attrgetter
import matlib
from Laminate import Laminate
from Ply import Ply


class OptimizedLaminate(Laminate):

    def __init__(self, laminate: Laminate, ply_thickness: float, load_case: dict, deformation_limits: list, hard_optimization: bool = True) -> None:
        self.optimized_load_case = load_case
        self.deformation_limits = deformation_limits
        exposure_factors = laminate.calculate_exposure_factors(load_case=load_case, deformation_limits=deformation_limits)
        # It is assumed that the adjustment_factor has a value between 0 and 1.
        # If not, the laminate is broken and cannot be optimized by reducing the ply thickness.
        adjustment_factor = max(exposure_factors)

        # A first rough optimization
        updated_layup = []
        for ply in laminate.layup:
            optimized_combined_layer_thickness = ply.thickness*adjustment_factor
            n_new_plies_per_combined_layer = optimized_combined_layer_thickness // ply_thickness
            if optimized_combined_layer_thickness % ply_thickness:
                n_new_plies_per_combined_layer += 1
            for i in range(int(n_new_plies_per_combined_layer)):
                updated_layup.append(Ply(material=ply.material, orientation=ply.orientation, thickness=ply_thickness))

        # Attempts at making a better optimization by removing layers
        if hard_optimization:
            self.branch_optimal_laminates = []
            unique_orientations = list(set([ply.orientation for ply in updated_layup]))
            tmp_laminate = Laminate(layup=updated_layup, name="")

            # Do the recursive iteration, filling the self.branch_optimal_laminates list
            self.strip_ply(orientations=unique_orientations, laminate=tmp_laminate)
            optimized_laminate = min(self.branch_optimal_laminates, key=attrgetter("thickness"))
            updated_layup = optimized_laminate.layup

        super().__init__(layup=updated_layup, name="Optimized_{}".format(laminate.name))

        # The mass reduction is directly related to the thickness_reduction
        self.mass_reduction = (1 - self.thickness/laminate.thickness)*100
        self.suboptimal_laminate = laminate
        pass

    def strip_ply(self, orientations: list[int], laminate: Laminate) -> None:
        tmp_laminates = []
        max_exposure_factors = []

        for i, orientation in enumerate(orientations):
            tmp_layup = copy.deepcopy(laminate.layup)
            for j, ply in enumerate(tmp_layup):
                if ply.orientation == orientation:
                    # Need to remove plies symmetrically
                    tmp_layup.pop(-j-1)
                    tmp_layup.pop(j)
                    tmp_laminate = Laminate(layup=tmp_layup, name="tmp_layup")
                    tmp_laminates.append(tmp_laminate)
                    exposure_factors = tmp_laminate.calculate_exposure_factors(load_case=self.optimized_load_case,
                                                                               deformation_limits=self.deformation_limits)
                    max_exposure_factors.append(max(exposure_factors))
                    break

        # Not very elegant, but gets the job done
        idx_to_pop = []
        for idx in range(len(max_exposure_factors)):
            if max_exposure_factors[idx] >= 1:
                idx_to_pop.append(idx)

        for idx in idx_to_pop[::-1]:
            max_exposure_factors.pop(idx)
            #orientations.pop(idx)
            tmp_laminates.pop(idx)

        for tmp_laminate in tmp_laminates:
            self.strip_ply(orientations=orientations, laminate=tmp_laminate)

        # Recursion break criteria
        if len(tmp_laminates) == 0:
            self.branch_optimal_laminates.append(laminate)

    def __repr__(self) -> str:
        return "I am the {} mm thick optimized laminate '{}' that " \
               "saved you {} % mass over the {} mm thick suboptimal laminate" \
               " '{}' for the load case {}. Nice!\nMy exposure factors are {}".format(round(self.thickness, 2),
                                                                                      self.name,
                                                                                      round(self.mass_reduction, 2),
                                                                                      round(self.suboptimal_laminate.thickness, 2),
                                                                                      self.suboptimal_laminate.name,
                                                                                      self.optimized_load_case,
                                                                                      self.calculate_exposure_factors(self.optimized_load_case,
                                                                                                                      self.deformation_limits))


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

    # Optimization using the simple algorithm detailed in the assignment report
    simple_optimized_laminate = OptimizedLaminate(laminate=laminate,
                                                  ply_thickness=ALTERNATIVE_THICKNESS,
                                                  load_case=LOAD_CASE,
                                                  deformation_limits=DEFORMATION_LIMITS,
                                                  hard_optimization=False)
    print(simple_optimized_laminate)

    # Optimization using the more advanced algorithm detailed in the assignment report
    advanced_optimized_laminate = OptimizedLaminate(laminate=laminate,
                                                    ply_thickness=ALTERNATIVE_THICKNESS,
                                                    load_case=LOAD_CASE,
                                                    deformation_limits=DEFORMATION_LIMITS,
                                                    hard_optimization=True)
    print(advanced_optimized_laminate)

    pass


if __name__ == "__main__":
    main()
