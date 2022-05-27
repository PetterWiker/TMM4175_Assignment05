import numpy as np
import copy
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Slider, Button

import matlib
from Ply import Ply
from Laminate import Laminate

DIMENSION = 20
DEVIATION_MIN = 50
DEVIATION_MAX = 50
LAMINATE_ORIENTATION = 0

GFRP = copy.deepcopy(matlib.get("E-glass/Epoxy"))
CFRP = copy.deepcopy(matlib.get("Carbon/Epoxy(a)"))


class LaminateTestBench:

    def __init__(self, material: dict, layup: list[Ply] = None, layup_name: str = None, fig=None, axs=None) -> None:
        self.material = material

        self.fig = fig
        self.axs = axs
        self.layup = layup
        self.layup_name = layup_name

        self.X = None
        self.Y = None
        self.E2s = np.linspace(-DEVIATION_MIN, DEVIATION_MAX, DIMENSION)
        self.G12s = np.linspace(-DEVIATION_MIN, DEVIATION_MAX, DIMENSION)
        self.X, self.Y = np.meshgrid(self.E2s, self.G12s)

        # Temporary containers that are constantly overwritten. Put here for easy accessibility.
        self.Exs = np.zeros((DIMENSION, DIMENSION))
        self.Eys = np.zeros((DIMENSION, DIMENSION))
        self.Gxys = np.zeros((DIMENSION, DIMENSION))
        self.vxys = np.zeros((DIMENSION, DIMENSION))

        self.layup_A = [Ply(material=material, orientation=0,   thickness=1),
                        Ply(material=material, orientation=90,  thickness=1),
                        Ply(material=material, orientation=90,  thickness=1),
                        Ply(material=material, orientation=0,   thickness=1)]

        self.layup_B = [Ply(material=material, orientation=45,  thickness=1),
                        Ply(material=material, orientation=-45, thickness=1),
                        Ply(material=material, orientation=-45, thickness=1),
                        Ply(material=material, orientation=45,  thickness=1)]

        self.layup_C = [Ply(material=material, orientation=0,   thickness=1),
                        Ply(material=material, orientation=90,  thickness=1),
                        Ply(material=material, orientation=45,  thickness=1),
                        Ply(material=material, orientation=-45, thickness=1),
                        Ply(material=material, orientation=-45, thickness=1),
                        Ply(material=material, orientation=45,  thickness=1),
                        Ply(material=material, orientation=90,  thickness=1),
                        Ply(material=material, orientation=0,   thickness=1)]
        pass

    @staticmethod
    def substitute_layup_material(layup: list[Ply], substitute: dict) -> list[Ply]:
        new_layup = copy.deepcopy(layup)
        for ply in new_layup:
            ply.material = substitute
        return new_layup

    @staticmethod
    def substitute_layup_orientation(layup: list[Ply], new_orientation: float) -> list[Ply]:
        new_layup = copy.deepcopy(layup)
        for ply in new_layup:
            ply.orientation += new_orientation
        return new_layup

    def calculate_effective_properties(self, layup: list[Ply], orientation: float) -> None:
        rotated_layup = self.substitute_layup_orientation(layup=layup, new_orientation=orientation)
        laminate = Laminate(layup=rotated_layup, name="base_laminate")
        np.set_printoptions(precision=2, suppress=True)
        Ex0, Ey0, Gxy0, vxy0 = laminate.calculate_laminate_properties()

        for i, E2_correction in enumerate(self.E2s):
            for j, G12_correction in enumerate(self.G12s):
                m = copy.deepcopy(self.material)
                m["E2"] *= (1+E2_correction/100)
                m["G12"] *= (1+G12_correction/100)
                corrected_layup = self.substitute_layup_material(layup=rotated_layup, substitute=m)
                laminate = Laminate(layup=corrected_layup, name="{}_{}_{}".format(self.material["name"], i, j))
                Ex, Ey, Gxy, vxy = laminate.calculate_laminate_properties()
                self.Exs[j, i] = 100*(Ex-Ex0)/Ex0
                self.Eys[j, i] = 100*(Ey-Ey0)/Ey0
                self.Gxys[j, i] = 100*(Gxy-Gxy0)/Gxy0
                self.vxys[j, i] = 100*(vxy-vxy0)/vxy0
        pass

    def plot_surfaces(self) -> None:
        self.axs[0, 0].cla()
        surf1 = self.axs[0, 0].plot_surface(self.X, self.Y, self.Exs, cmap=cm.RdYlGn_r, linewidth=0, antialiased=False)
        self.axs[0, 0].set_zlabel("E_x (% dev)")

        self.axs[0, 1].cla()
        surf2 = self.axs[0, 1].plot_surface(self.X, self.Y, self.Eys, cmap=cm.RdYlGn_r, linewidth=0, antialiased=False)
        self.axs[0, 1].set_zlabel("E_y (% dev)")

        self.axs[1, 0].cla()
        surf3 = self.axs[1, 0].plot_surface(self.X, self.Y, self.Gxys, cmap=cm.RdYlGn_r, linewidth=0, antialiased=False)
        self.axs[1, 0].set_zlabel("G_xy (% dev)")

        self.axs[1, 1].cla()
        surf4 = self.axs[1, 1].plot_surface(self.X, self.Y, self.vxys, cmap=cm.RdYlGn_r, linewidth=0, antialiased=False)
        self.axs[1, 1].set_zlabel("v_xy (% dev)")
        for ax in self.axs.flatten():
            ax.set_zlim(-100, 100)
            ax.set_xlabel("E_2 (% dev)")
            ax.set_ylabel("G_12 (% dev)")
        pass

    def plot_layup_surface(self, layup: list[Ply], layup_name: str) -> None:

        self.layup = layup
        self.layup_name = layup_name

        # Make the surface plots
        self.fig, self.axs = plt.subplots(2, 2, subplot_kw={"projection": "3d"})
        self.fig.suptitle("material={}, layup={}, dimensions={}x{}, orientation={}°".format(
            self.material["name"], self.layup_name, DIMENSION, DIMENSION, LAMINATE_ORIENTATION))

        self.calculate_effective_properties(layup=self.layup, orientation=LAMINATE_ORIENTATION)
        self.plot_surfaces()

        # Incorporate a slider for the laminate orientation
        ax_orientation = plt.axes([0.25, 0.01, 0.65, 0.03])
        orientation_slider = Slider(
            ax=ax_orientation,
            label='Laminate Orientation (°)',
            valmin=0,
            valmax=90,
            valinit=LAMINATE_ORIENTATION,
            valfmt='%0.0f',
        )

        # Incorporate a slider for the plot dimensions
        ax_dimension = plt.axes([0.25, 0.03, 0.65, 0.03])
        dimension_slider = Slider(
            ax=ax_dimension,
            label='Plot dimensions',
            valmin=5,
            valmax=50,
            valinit=DIMENSION,
            valfmt='%0.0f',
        )

        def update_plot_dimension(val):
            global DIMENSION
            DIMENSION = round(dimension_slider.val)
            self.__init__(material=self.material, layup=self.layup, layup_name=self.layup_name, fig=self.fig, axs=self.axs)
            update_surface_plot(val=None)
            pass

        dimension_slider.on_changed(update_plot_dimension)

        # Incorporate a slider for the plot dimensions
        ax_deviation = plt.axes([0.25, 0.05, 0.65, 0.03])
        deviation_slider = Slider(
            ax=ax_deviation,
            label='Max/min deviation (%)',
            valmin=10,
            valmax=90,
            valinit=DEVIATION_MAX,
            valfmt='%0.0f',
        )

        def update_plot_deviation(val):
            global DEVIATION_MAX
            global DEVIATION_MIN
            DEVIATION_MAX = round(deviation_slider.val)
            DEVIATION_MIN = round(deviation_slider.val)
            self.__init__(material=self.material, layup=self.layup, layup_name=self.layup_name, fig=self.fig, axs=self.axs)
            update_surface_plot(val=None)
            pass

        deviation_slider.on_changed(update_plot_deviation)

        # Incorporate a button for each layup
        layup_A_ax = plt.axes([0.05, 0.9, 0.1, 0.04])
        layup_A_button = Button(layup_A_ax, 'Layup A', hovercolor='0.975')

        def A_button(event):
            self.layup = self.layup_A
            self.layup_name = "layup_A"
            update_surface_plot(val=None)
            pass
        layup_A_button.on_clicked(A_button)

        layup_B_ax = plt.axes([0.05, 0.85, 0.1, 0.04])
        layup_B_button = Button(layup_B_ax, 'Layup B', hovercolor='0.975')

        def B_button(event):
            self.layup = self.layup_B
            self.layup_name = "layup_B"
            update_surface_plot(val=None)
            pass
        layup_B_button.on_clicked(B_button)

        layup_C_ax = plt.axes([0.05, 0.80, 0.1, 0.04])
        layup_C_button = Button(layup_C_ax, 'Layup C', hovercolor='0.975')

        def C_button(event):
            self.layup = self.layup_C
            self.layup_name = "layup_C"
            update_surface_plot(val=None)
            pass
        layup_C_button.on_clicked(C_button)

        # Incorporate a button for each material
        GFRP_ax = plt.axes([0.05, 0.70, 0.1, 0.04])
        GFRP_button = Button(GFRP_ax, 'GFRP', hovercolor='0.975')

        def _GFRP_button(event):
            self.layup = self.substitute_layup_material(layup=self.layup, substitute=GFRP)
            self.__init__(material=GFRP, layup=self.layup, layup_name=self.layup_name, fig=self.fig, axs=self.axs)
            update_surface_plot(val=None)
            pass
        GFRP_button.on_clicked(_GFRP_button)

        CFRP_ax = plt.axes([0.05, 0.65, 0.1, 0.04])
        CFRP_button = Button(CFRP_ax, 'CFRP', hovercolor='0.975')

        def _CFRP_button(event):
            self.layup = self.substitute_layup_material(layup=self.layup, substitute=CFRP)
            self.__init__(material=CFRP, layup=self.layup, layup_name=self.layup_name, fig=self.fig, axs=self.axs)
            update_surface_plot(val=None)
            pass
        CFRP_button.on_clicked(_CFRP_button)

        def update_surface_plot(val):
            self.calculate_effective_properties(layup=self.layup, orientation=orientation_slider.val)
            self.plot_surfaces()
            self.fig.suptitle("material={}, layup={}, dimensions={}x{}, orientation={}°".format(
                self.material["name"], self.layup_name, DIMENSION, DIMENSION, round(orientation_slider.val, 0)))
            self.fig.canvas.draw_idle()
            pass

        orientation_slider.on_changed(update_surface_plot)
        plt.show()
        pass


def main():
    testbench = LaminateTestBench(material=GFRP)
    testbench.plot_layup_surface(layup=testbench.layup_A, layup_name="layup_A")
    pass


if __name__ == "__main__":
    main()
