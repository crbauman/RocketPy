from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

from .plot_helpers import show_or_save_plot


class _AeroSurfacePlots(ABC):
    """Abstract class that contains all aero surface plots."""

    def __init__(self, aero_surface):
        """Initialize the class

        Parameters
        ----------
        aero_surface : rocketpy.AeroSurface
            AeroSurface object to be plotted

        Returns
        -------
        None
        """
        self.aero_surface = aero_surface

    @abstractmethod
    def draw(self, *, filename=None):
        pass

    def lift(self):
        """Plots the lift coefficient of the aero surface as a function of Mach
        and the angle of attack. A 3D plot is expected. See the rocketpy.Function
        class for more information on how this plot is made.

        Returns
        -------
        None
        """
        self.aero_surface.cl()

    def all(self):
        """Plots all aero surface plots.

        Returns
        -------
        None
        """
        self.draw()
        self.lift()


class _NoseConePlots(_AeroSurfacePlots):
    """Class that contains all nosecone plots. This class inherits from the
    _AeroSurfacePlots class."""

    def draw(self, *, filename=None):
        """Draw the nosecone shape along with some important information,
        including the center line and the center of pressure position.

        Parameters
        ----------
        filename : str | None, optional
            The path the plot should be saved to. By default None, in which case
            the plot will be shown instead of saved. Supported file endings are:
            eps, jpg, jpeg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
            and webp (these are the formats supported by matplotlib).

        Returns
        -------
        None
        """
        # Create the vectors X and Y with the points of the curve
        nosecone_x, nosecone_y = self.aero_surface.shape_vec

        # Figure creation and set up
        _, ax = plt.subplots()
        ax.set_xlim(-0.05, self.aero_surface.length * 1.02)  # Horizontal size
        ax.set_ylim(
            -self.aero_surface.base_radius * 1.05, self.aero_surface.base_radius * 1.05
        )  # Vertical size
        ax.set_aspect("equal")  # Makes the graduation be the same on both axis
        ax.set_facecolor("#EEEEEE")  # Background color
        ax.grid(True, linestyle="--", linewidth=0.5)

        cp_plot = (self.aero_surface.cpz, 0)
        # Plotting
        ax.plot(
            nosecone_x,
            nosecone_y,
            linestyle="-",
            color="#A60628",
        )  # Ogive's upper side
        ax.plot(
            nosecone_x,
            -nosecone_y,
            linestyle="-",
            color="#A60628",
        )  # Ogive's lower side
        ax.scatter(
            *cp_plot, label="Center Of Pressure", color="red", s=100, zorder=10
        )  # Center of pressure inner circle
        ax.scatter(
            *cp_plot, facecolors="none", edgecolors="red", s=500, zorder=10
        )  # Center of pressure outer circle
        # Center Line
        ax.plot(
            [0, nosecone_x[len(nosecone_x) - 1]],
            [0, 0],
            linestyle="--",
            color="#7A68A6",
            linewidth=1.5,
            label="Center Line",
        )
        # Vertical base line
        ax.plot(
            [
                nosecone_x[len(nosecone_x) - 1],
                nosecone_x[len(nosecone_x) - 1],
            ],
            [
                nosecone_y[len(nosecone_y) - 1],
                -nosecone_y[len(nosecone_y) - 1],
            ],
            linestyle="-",
            color="#A60628",
            linewidth=1.5,
        )

        # Labels and legend
        ax.set_xlabel("Length")
        ax.set_ylabel("Radius")
        ax.set_title(self.aero_surface.kind + " Nose Cone")
        ax.legend(bbox_to_anchor=(1, -0.2))
        show_or_save_plot(filename)


class _FinsPlots(_AeroSurfacePlots):
    """Abstract class that contains all fin plots. This class inherits from the
    _AeroSurfacePlots class."""

    @abstractmethod
    def draw(self, *, filename=None):
        pass

    def airfoil(self):
        """Plots the airfoil information when the fin has an airfoil shape. If
        the fin does not have an airfoil shape, this method does nothing.

        Returns
        -------
        None
        """

        if self.aero_surface.airfoil:
            print("Airfoil lift curve:")
            self.aero_surface.airfoil_cl.plot_1d(force_data=True)

    def roll(self):
        """Plots the roll parameters of the fin set.

        Returns
        -------
        None
        """
        print("Roll parameters:")
        # TODO: lacks a title in the plots
        self.aero_surface.roll_parameters[0]()
        self.aero_surface.roll_parameters[1]()

    def lift(self):
        """Plots the lift coefficient of the aero surface as a function of Mach
        and the angle of attack. A 3D plot is expected. See the rocketpy.Function
        class for more information on how this plot is made. Also, this method
        plots the lift coefficient considering a single fin and the lift
        coefficient considering all fins.

        Returns
        -------
        None
        """
        print("Lift coefficient:")
        self.aero_surface.cl()
        self.aero_surface.clalpha_single_fin()
        self.aero_surface.clalpha_multiple_fins()

    def all(self):
        """Plots all available fin plots.

        Returns
        -------
        None
        """
        self.draw()
        self.airfoil()
        self.roll()
        self.lift()


class _TrapezoidalFinsPlots(_FinsPlots):
    """Class that contains all trapezoidal fin plots."""

    # pylint: disable=too-many-statements
    def draw(self, *, filename=None):
        """Draw the fin shape along with some important information, including
        the center line, the quarter line and the center of pressure position.

        Parameters
        ----------
        filename : str | None, optional
            The path the plot should be saved to. By default None, in which case
            the plot will be shown instead of saved. Supported file endings are:
            eps, jpg, jpeg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
            and webp (these are the formats supported by matplotlib).

        Returns
        -------
        None
        """
        # Color cycle [#348ABD, #A60628, #7A68A6, #467821, #D55E00, #CC79A7,
        # #56B4E9, #009E73, #F0E442, #0072B2]
        # Fin
        leading_edge = plt.Line2D(
            (0, self.aero_surface.sweep_length),
            (0, self.aero_surface.span),
            color="#A60628",
        )
        tip = plt.Line2D(
            (
                self.aero_surface.sweep_length,
                self.aero_surface.sweep_length + self.aero_surface.tip_chord,
            ),
            (self.aero_surface.span, self.aero_surface.span),
            color="#A60628",
        )
        back_edge = plt.Line2D(
            (
                self.aero_surface.sweep_length + self.aero_surface.tip_chord,
                self.aero_surface.root_chord,
            ),
            (self.aero_surface.span, 0),
            color="#A60628",
        )
        root = plt.Line2D((self.aero_surface.root_chord, 0), (0, 0), color="#A60628")

        # Center and Quarter line
        center_line = plt.Line2D(
            (
                self.aero_surface.root_chord / 2,
                self.aero_surface.sweep_length + self.aero_surface.tip_chord / 2,
            ),
            (0, self.aero_surface.span),
            color="#7A68A6",
            alpha=0.35,
            linestyle="--",
            label="Center Line",
        )
        quarter_line = plt.Line2D(
            (
                self.aero_surface.root_chord / 4,
                self.aero_surface.sweep_length + self.aero_surface.tip_chord / 4,
            ),
            (0, self.aero_surface.span),
            color="#7A68A6",
            alpha=1,
            linestyle="--",
            label="Quarter Line",
        )

        # Center of pressure
        cp_point = [self.aero_surface.cpz, self.aero_surface.Yma]

        # Mean Aerodynamic Chord
        yma_start = (
            self.aero_surface.sweep_length
            * (self.aero_surface.root_chord + 2 * self.aero_surface.tip_chord)
            / (3 * (self.aero_surface.root_chord + self.aero_surface.tip_chord))
        )
        yma_end = (
            2 * self.aero_surface.root_chord**2
            + self.aero_surface.root_chord * self.aero_surface.sweep_length
            + 2 * self.aero_surface.root_chord * self.aero_surface.tip_chord
            + 2 * self.aero_surface.sweep_length * self.aero_surface.tip_chord
            + 2 * self.aero_surface.tip_chord**2
        ) / (3 * (self.aero_surface.root_chord + self.aero_surface.tip_chord))
        yma_line = plt.Line2D(
            (yma_start, yma_end),
            (self.aero_surface.Yma, self.aero_surface.Yma),
            color="#467821",
            linestyle="--",
            label="Mean Aerodynamic Chord",
        )

        # Plotting
        fig = plt.figure(figsize=(7, 4))
        with plt.style.context("bmh"):
            ax = fig.add_subplot(111)

        # Fin
        ax.add_line(leading_edge)
        ax.add_line(tip)
        ax.add_line(back_edge)
        ax.add_line(root)

        ax.add_line(center_line)
        ax.add_line(quarter_line)
        ax.add_line(yma_line)
        ax.scatter(*cp_point, label="Center of Pressure", color="red", s=100, zorder=10)
        ax.scatter(*cp_point, facecolors="none", edgecolors="red", s=500, zorder=10)

        # Plot settings
        xlim = (
            self.aero_surface.root_chord
            if self.aero_surface.sweep_length + self.aero_surface.tip_chord
            < self.aero_surface.root_chord
            else self.aero_surface.sweep_length + self.aero_surface.tip_chord
        )
        ax.set_xlim(0, xlim * 1.1)
        ax.set_ylim(0, self.aero_surface.span * 1.1)
        ax.set_xlabel("Root chord (m)")
        ax.set_ylabel("Span (m)")
        ax.set_title("Trapezoidal Fin Cross Section")
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")

        plt.tight_layout()
        show_or_save_plot(filename)


class _EllipticalFinsPlots(_FinsPlots):
    """Class that contains all elliptical fin plots."""

    # pylint: disable=too-many-statements
    def draw(self, *, filename=None):
        """Draw the fin shape along with some important information.
        These being: the center line and the center of pressure position.

        Parameters
        ----------
        filename : str | None, optional
            The path the plot should be saved to. By default None, in which case
            the plot will be shown instead of saved. Supported file endings are:
            eps, jpg, jpeg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
            and webp (these are the formats supported by matplotlib).

        Returns
        -------
        None
        """
        # Ellipse
        ellipse = Ellipse(
            (self.aero_surface.root_chord / 2, 0),
            self.aero_surface.root_chord,
            self.aero_surface.span * 2,
            fill=False,
            edgecolor="#A60628",
            linewidth=2,
        )

        # Mean Aerodynamic Chord # From Barrowman's theory
        yma_length = 8 * self.aero_surface.root_chord / (3 * np.pi)
        yma_start = (self.aero_surface.root_chord - yma_length) / 2
        yma_end = (
            self.aero_surface.root_chord
            - (self.aero_surface.root_chord - yma_length) / 2
        )
        yma_line = plt.Line2D(
            (yma_start, yma_end),
            (self.aero_surface.Yma, self.aero_surface.Yma),
            label="Mean Aerodynamic Chord",
            color="#467821",
        )

        # Center Line
        center_line = plt.Line2D(
            (self.aero_surface.root_chord / 2, self.aero_surface.root_chord / 2),
            (0, self.aero_surface.span),
            color="#7A68A6",
            alpha=0.35,
            linestyle="--",
            label="Center Line",
        )

        # Center of pressure
        cp_point = [self.aero_surface.cpz, self.aero_surface.Yma]

        # Plotting
        fig = plt.figure(figsize=(7, 4))
        with plt.style.context("bmh"):
            ax = fig.add_subplot(111)
        ax.add_patch(ellipse)
        ax.add_line(yma_line)
        ax.add_line(center_line)
        ax.scatter(*cp_point, label="Center of Pressure", color="red", s=100, zorder=10)
        ax.scatter(*cp_point, facecolors="none", edgecolors="red", s=500, zorder=10)

        # Plot settings
        ax.set_xlim(0, self.aero_surface.root_chord)
        ax.set_ylim(0, self.aero_surface.span * 1.1)
        ax.set_xlabel("Root chord (m)")
        ax.set_ylabel("Span (m)")
        ax.set_title("Elliptical Fin Cross Section")
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")

        plt.tight_layout()
        show_or_save_plot(filename)


class _FreeFormFinsPlots(_FinsPlots):
    """Class that contains all free form fin plots."""

    # pylint: disable=too-many-statements
    def draw(self, *, filename=None):
        """Draw the fin shape along with some important information.
        These being: the center line and the center of pressure position.

        Parameters
        ----------
        filename : str | None, optional
            The path the plot should be saved to. By default None, in which case
            the plot will be shown instead of saved. Supported file endings are:
            eps, jpg, jpeg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
            and webp (these are the formats supported by matplotlib).

        Returns
        -------
        None
        """
        # Color cycle [#348ABD, #A60628, #7A68A6, #467821, #D55E00, #CC79A7,
        # #56B4E9, #009E73, #F0E442, #0072B2]

        # Center of pressure
        cp_point = [self.aero_surface.cpz, self.aero_surface.Yma]

        # Mean Aerodynamic Chord
        yma_line = plt.Line2D(
            (
                self.aero_surface.mac_lead,
                self.aero_surface.mac_lead + self.aero_surface.mac_length,
            ),
            (self.aero_surface.Yma, self.aero_surface.Yma),
            color="#467821",
            linestyle="--",
            label="Mean Aerodynamic Chord",
        )

        # Plotting
        fig = plt.figure(figsize=(7, 4))
        with plt.style.context("bmh"):
            ax = fig.add_subplot(111)

        # Fin
        ax.scatter(
            self.aero_surface.shape_vec[0],
            self.aero_surface.shape_vec[1],
            color="#A60628",
        )
        ax.plot(
            self.aero_surface.shape_vec[0],
            self.aero_surface.shape_vec[1],
            color="#A60628",
        )
        # line from the last point to the first point
        ax.plot(
            [self.aero_surface.shape_vec[0][-1], self.aero_surface.shape_vec[0][0]],
            [self.aero_surface.shape_vec[1][-1], self.aero_surface.shape_vec[1][0]],
            color="#A60628",
        )

        ax.add_line(yma_line)
        ax.scatter(*cp_point, label="Center of Pressure", color="red", s=100, zorder=10)
        ax.scatter(*cp_point, facecolors="none", edgecolors="red", s=500, zorder=10)

        # Plot settings
        ax.set_xlabel("Root chord (m)")
        ax.set_ylabel("Span (m)")
        ax.set_title("Free Form Fin Cross Section")
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")

        plt.tight_layout()
        show_or_save_plot(filename)


class _TailPlots(_AeroSurfacePlots):
    """Class that contains all tail plots."""

    def draw(self, *, filename=None):
        # This will de done in the future
        pass


class _AirBrakesPlots(_AeroSurfacePlots):
    """Class that contains all air brakes plots."""

    def drag_coefficient_curve(self):
        """Plots the drag coefficient curve of the air_brakes."""
        if self.aero_surface.clamp is True:
            return self.aero_surface.drag_coefficient.plot(0, 1)
        else:
            return self.aero_surface.drag_coefficient.plot()

    def draw(self, *, filename=None):
        raise NotImplementedError

    def all(self):
        """Plots all available air_brakes plots.

        Returns
        -------
        None
        """
        self.drag_coefficient_curve()


class _GenericSurfacePlots(_AeroSurfacePlots):
    """Class that contains all generic surface plots."""

    def draw(self, *, filename=None):
        pass


class _LinearGenericSurfacePlots(_AeroSurfacePlots):
    """Class that contains all linear generic surface plots."""

    def draw(self, *, filename=None):
        pass
