from __future__ import annotations

from math import pi
from typing import List, Optional, Tuple, Union

from brian2.units import Quantity


class EphysProperties(object):
    """
    A class for calculating various important electrophysiological properties
    for a single compartment.

    Note
    ----
    An EphysProperties object is automatically created and linked to a 
    :class:`.Compartment`, :class:`.Soma`, or :class:`.Dendrite` object
    during the instantiation of the latter.

    Parameters
    ----------

    name : str, optional
        A compartment's name, by default ``None``
    length : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's length, by default ``None``
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's diameter, by default ``None``
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2), by default ``None``
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2), by default ``None``
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm), by default ``None``
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage, by default ``None``
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``
    """

    def __init__(self, name: Optional[str] = None,
                 length: Optional[Quantity] = None,
                 diameter: Optional[Quantity] = None,
                 cm: Optional[Quantity] = None,
                 gl: Optional[Quantity] = None,
                 r_axial: Optional[Quantity] = None,
                 v_rest: Optional[Quantity] = None,
                 scale_factor: float = 1.0,
                 spine_factor: float = 1.0):
        self.name = name
        self.length = length
        self.diameter = diameter
        self.cm = cm
        self.gl = gl
        self.r_axial = r_axial
        self.v_rest = v_rest
        self.scale_factor = scale_factor
        self.spine_factor = spine_factor

    def __str__(self):
        attrs = self.__dict__
        details = [f"\u2192 {i}: \n{attrs[i]}\n" for i in attrs]
        msg = ("OBJECT:\n{0}\n"
               "\n=======================================================\n\n"
               "ATTRIBUTES:\n{1}")
        return msg.format(self.__class__, "\n".join(details))

    @property
    def total_area_factor(self) -> float:
        """
        The total surface are factor.

        Returns
        -------
        float
        """
        return self.scale_factor * self.spine_factor

    @property
    def area(self) -> Quantity:
        """
        A compartment's surface area (open cylinder) based on its length and
        diameter.

        Returns
        -------
        ~brian2.units.fundamentalunits.Quantity
            A compartment's surface area
        """
        try:
            return pi * self.length * self.diameter * self.total_area_factor
        except TypeError:
            print(("ERROR: Missing Parameters ('length' or 'diameter')\n"
                  f"Could not calculate the area of <{self.name}>, "
                   "returned None instead\n"))

    @property
    def capacitance(self) -> Quantity:
        """
        A compartment's absolute capacitance based on its specific capacitance
        (cm) and surface area.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        try:
            return self.area * self.cm
        except TypeError:
            print(("ERROR: Missing Parameters ('cm')\n"
                  f"Could not calculate the capacitance of <{self.name}>, "
                   "returned None instead"))

    @property
    def g_leakage(self) -> Quantity:
        """
        A compartment's absolute leakage conductance based on its specific
        leakage conductance (gl) and surface area.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        try:
            return self.area * self.gl
        except TypeError:
            print(("ERROR: Missing Parameters ('gl')\n"
                  f"Could not calculate the g_leakage of <{self.name}>, "
                   "returned None instead"))

    @property
    def parameters(self) -> dict:
        """
        Returns a dictionary of all electrophysiological parameters.

        Returns
        -------
        dict
        """
        d = {}
        error = None

        if self.v_rest:
            d[f"EL_{self.name}"] = self.v_rest
        else:
            print(f"ERROR: Could not resolve 'EL_{self.name}'\n")
            error = True

        if self.capacitance:
            d[f"C_{self.name}"] = self.capacitance
        else:
            print(f"Could not resolve 'C_{self.name}'\n")
            error = True

        if self.g_leakage:
            d[f"gL_{self.name}"] = self.g_leakage
        else:
            print(f"Could not resolve 'gL_{self.name}'")
            error = True

        if error:
            print("\nWARNING: One or more parameters are "
                  f"missing for '{self.name}' !!!\n")
        return d

    @property
    def g_cylinder(self) -> Quantity:
        """
        The conductance (of coupling currents) passing through a cylindrical
        compartment based on its dimensions and its axial resistance. To be
        used when then the total number of compartments is low and the
        adjacent-to-soma compartments are highly coupled with the soma.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        try:
            ri = (4*self.r_axial*self.length) / (pi*self.diameter**2)
        except TypeError:
            print(("ERROR: Missing Parameters <length / diameter / r_axial>\n"
                  f"Could not calculate the g_cylinder of <{self.name}>, "
                   "returned None instead."))
        else:
            return 1/ri

    @staticmethod
    def g_couple(comp1: EphysProperties, comp2: EphysProperties) -> Quantity:
        """
        The conductance (of coupling currents) between the centers of
        two adjacent cylindrical compartments, based on their dimensions
        and the axial resistance.

        Parameters
        ----------
        comp1 : EphysProperties
            An EphysProperties object
        comp2 : EphysProperties
            An EphysProperties object

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        try:
            r1 = (4 * comp1.r_axial * comp1.length) / (pi * comp1.diameter**2)
            r2 = (4 * comp2.r_axial * comp2.length) / (pi * comp2.diameter**2)
            ri = (r1+r2) / 2
        except TypeError:
            print(("ERROR: Missing Parameters <length / diameter / r_axial>\n"
                   f"Could not calculate the g_couple of <{comp1.name}> "
                   f"& <{comp2.name}>, returned None instead."))
        else:
            return 1/ri
