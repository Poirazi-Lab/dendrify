from __future__ import annotations

from math import pi
from typing import List, Optional, Tuple, Union

from brian2.units import Quantity

from .utils import *

logger = get_logger(__name__)


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
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF), by default ``None``
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS), by default ``None``
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
                 cm_abs: Optional[Quantity] = None,
                 gl_abs: Optional[Quantity] = None,
                 r_axial: Optional[Quantity] = None,
                 v_rest: Optional[Quantity] = None,
                 scale_factor: Optional[float] = 1.0,
                 spine_factor: Optional[float] = 1.0):
        self.name = name
        self.length = length
        self.diameter = diameter
        self.cm = cm
        self.gl = gl
        self.cm_abs = cm_abs
        self.gl_abs = gl_abs
        self.r_axial = r_axial
        self.v_rest = v_rest
        self.scale_factor = scale_factor
        self.spine_factor = spine_factor
        self._dimensionless = True if any([cm_abs, gl_abs]) else False
        self._check_dimensionless()

    def __str__(self):
        attrs = self.__dict__
        details = '\n'.join([f"\u2192 {i}: \n{attrs[i]}\n" for i in attrs])
        msg = (f"OBJECT:\n{self.__class__}\n\n"
               f"{'-'*55}\n\n"
               f"ATTRIBUTES:\n{details}"
               )
        return msg

    def _check_dimensionless(self):
        """
        Ensure that no redundant parameters are provided when a dimensionless
        compartment is created (i.e., when absolute values of capacitance and
        leakage conductance are provided).
        """
        not_dimensionless = [self.length, self.diameter,
                             self.cm, self.gl, self.r_axial]

        if self._dimensionless and any(not_dimensionless):
            raise ParametersError(
                ("Redundant or incompatible parameters were detected\n"
                 f"during the initialization of '{self.name}'. "
                 "When absolute values of capacitance\n[cm_abs] or leakage "
                 "conductance [gl_abs] are provided, a dimensionless\n"
                 "compartment is created by default. To resolve this error, "
                 "you can\nperform one of the following actions:\n\n"
                 "1. Discard these parameters [length, diameter, cm,"
                 "gl, r_axial]\n   if you want to create a dimensionless "
                 "compartment.\n\n"
                 "2. Discard these parameters [cm_abs, gl_abs] if you want to\n"
                 "   create a compartment with physical dimensions."
                 )
            )

    @property
    def _total_area_factor(self) -> float:
        """
        The total surface are factor.

        Returns
        -------
        float
        """
        return self.scale_factor * self.spine_factor

    @property
    def area(self) -> Quantity | None:
        """
        A compartment's surface area (open cylinder) based on its length and
        diameter.

        Returns
        -------
        ~brian2.units.fundamentalunits.Quantity
            A compartment's surface area
        """
        if self._dimensionless:
            logger.warning(
                (f"Surface area is not defined for the dimensionless "
                 f"compartment: '{self.name}'"
                 f"\nReturning None instead.\n"
                 )
            )
        else:
            try:
                return pi * self.length * self.diameter * self._total_area_factor
            except TypeError:
                logger.warning(
                    (f"Missing parameters [length | diameter] for '{self.name}'."
                     f"\nCould not calculate the area of '{self.name}', "
                     "returned None instead.\n"
                     )
                )

    @property
    def capacitance(self) -> Quantity | None:
        """
        Returns a compartment's capacitance based on its specific capacitance
        (cm) and surface area. If the absolute capacitance (cm_abs) has been
        provided by the user, it returns this value instead.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        if self._dimensionless:
            if self.cm_abs:
                return self.cm_abs
            else:
                logger.warning(
                    f"Missing parameter [cm_abs] for '{self.name}', "
                    "returned None instead."
                )
        else:
            try:
                return self.area * self.cm
            except TypeError:
                logger.warning(
                    (f"Missing parameter [cm] for '{self.name}'."
                     f"\nCould not calculate the capacitance of '{self.name}', "
                     "returned None instead.\n"
                     )
                )

    @property
    def g_leakage(self) -> Quantity:
        """
        A compartment's absolute leakage conductance based on its specific
        leakage conductance (gl) and surface area. If the absolute leakage
        conductance (gl_abs) has been provided by the user, it returns this
        value instead.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        if self._dimensionless:
            if self.gl_abs:
                return self.gl_abs
            else:
                logger.warning(
                    f"Missing parameter [gl_abs] for '{self.name}', "
                    "returned None instead."
                )
        else:
            try:
                return self.area * self.gl
            except TypeError:
                logger.warning(
                    (f"Missing parameter [gl] for '{self.name}'."
                     f"\nCould not calculate the g_leakage of '{self.name}', "
                     "returned None instead.\n"
                     )
                )

    @ property
    def parameters(self) -> dict:
        """
        Returns a dictionary of all electrophysiological parameters.

        Returns
        -------
        dict
        """
        d = {}
        EL, C, gL = self.v_rest, self.capacitance, self.capacitance

        for value, var in zip([EL, C, gL], ['EL', 'C', 'gL']):
            if value:
                d[f"{var}_{self.name}"] = value
            else:
                logger.error(f"Could not resolve '{var}_{self.name}'\n")

        # if self.v_rest:
        #     d[f"EL_{self.name}"] = self.v_rest
        # else:
        #     print(f"ERROR: Could not resolve 'EL_{self.name}'\n")
        #     error = True

        # if self.capacitance:
        #     d[f"C_{self.name}"] = self.capacitance
        # else:
        #     print(f"Could not resolve 'C_{self.name}'\n")
        #     error = True

        # if self.g_leakage:
        #     d[f"gL_{self.name}"] = self.capacitance
        # else:
        #     print(f"Could not resolve 'gL_{self.name}'")
        #     error = True

        # if error:
        #     print("\nWARNING: One or more parameters are "
        #           f"missing for '{self.name}' !!!\n")
        return d

    @ property
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

    @ staticmethod
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
