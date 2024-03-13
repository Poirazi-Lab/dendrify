"""
This module contains the EphysProperties class which is used for calculating
various important ephys properties for a single compartment. It
also contains utility functions to get and update the default ephys
parameters.

Classes:
    EphysProperties: A class for calculating various important ephys
                     properties for a single compartment.

Functions:
    default_params() -> dict: Returns the default ephys parameters.
    update_default_params(params: dict) -> None: Updates the default ephys parameters.
"""

from __future__ import annotations

import pprint as pp
from math import pi
from typing import Optional

from brian2.units import Quantity, mV

from .utils import DimensionlessCompartmentError, get_logger

logger = get_logger(__name__)


def default_params() -> dict:
    """
    Returns the default ephys parameters.

    Returns
    -------
    dict
    """
    return EphysProperties.DEFAULT_PARAMS


def update_default_params(params: dict) -> None:
    """
    Updates the default ephys parameters.

    Parameters
    ----------
    params : dict
        A dictionary of ionic parameters
    """
    EphysProperties.DEFAULT_PARAMS.update(params)


class EphysProperties:
    """
    A class for calculating various important electrophysiological properties
    for a single compartment.

    Note
    ----
    An EphysProperties object is automatically created and linked to a
    single compartment during the initialization of the latter.

    Parameters
    ----------

    name : str, optional
        A compartment's name.
    length : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's length.
    diameter : ~brian2.units.fundamentalunits.Quantity, optional
        A compartment's diameter.
    cm : ~brian2.units.fundamentalunits.Quantity, optional
        Specific capacitance (usually μF / cm^2).
    gl : ~brian2.units.fundamentalunits.Quantity, optional
        Specific leakage conductance (usually μS / cm^2).
    cm_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute capacitance (usually pF).
    gl_abs : ~brian2.units.fundamentalunits.Quantity, optional
        Absolute leakage conductance (usually nS).
    r_axial : ~brian2.units.fundamentalunits.Quantity, optional
        Axial resistance (usually Ohm * cm).
    v_rest : ~brian2.units.fundamentalunits.Quantity, optional
        Resting membrane voltage.
    scale_factor : float, optional
        A global area scale factor, by default ``1.0``.
    spine_factor : float, optional
        A dendritic area scale factor to account for spines, by default ``1.0``.
    """

    DEFAULT_PARAMS = {
        "E_AMPA": 0 * mV,
        "E_NMDA": 0 * mV,
        "E_GABA": -80 * mV,
        "E_Na": 70 * mV,
        "E_K": -89 * mV,
        "E_Ca": 136 * mV,
        "Mg_con": 1.0,
        "Alpha_NMDA": 0.062,
        "Beta_NMDA": 3.57,
        "Gamma_NMDA": 0
    }

    def __init__(
        self,
        name: Optional[str] = None,
        length: Optional[Quantity] = None,
        diameter: Optional[Quantity] = None,
        cm: Optional[Quantity] = None,
        gl: Optional[Quantity] = None,
        cm_abs: Optional[Quantity] = None,
        gl_abs: Optional[Quantity] = None,
        r_axial: Optional[Quantity] = None,
        v_rest: Optional[Quantity] = None,
        scale_factor: Optional[float] = 1.0,
        spine_factor: Optional[float] = 1.0
    ):
        self.name = name
        self.length = length
        self.diameter = diameter
        self.cm = cm
        self.gl = gl
        self.cm_abs = cm_abs
        self.gl_abs = gl_abs
        self.r_axial = r_axial
        self.v_rest = v_rest
        self.scale_factor = scale_factor if not any([cm_abs, gl_abs]) else None
        self.spine_factor = spine_factor if not any([cm_abs, gl_abs]) else None
        self._dimensionless = bool(any([cm_abs, gl_abs]))
        self._check_dimensionless()

    def __str__(self):
        attrs = pp.pformat(self.__dict__)
        txt = (f"OBJECT:\n{self.__class__}\n\n"
               f"ATTRIBUTES:\n{attrs}"
               )
        return txt

    def _check_dimensionless(self):
        """
        Ensure that no redundant parameters are provided when a dimensionless
        compartment is created (i.e., when absolute values of capacitance and
        leakage conductance are provided).
        """
        not_dimensionless = [self.length, self.diameter,
                             self.cm, self.gl, self.r_axial]

        if self._dimensionless and any(not_dimensionless):
            raise DimensionlessCompartmentError(
                ("\nRedundant or incompatible parameters were detected "
                 f"during \nthe initialization of '{self.name}'. "
                 "When absolute values of \ncapacitance [cm_abs] or leakage "
                 "conductance [gl_abs] are \nused, a dimensionless "
                 "compartment is created by default. \nTo resolve this error, "
                 "you can perform one of the following:\n\n"
                 "1. Discard these parameters [length, diameter, cm,"
                 "gl, r_axial]\n   if you want to create a dimensionless "
                 "compartment.\n\n"
                 "2. Discard these parameters [cm_abs, gl_abs] if you want to\n"
                 "   create a compartment with physical dimensions."
                 )
            )

    @property
    def _total_area_factor(self) -> float | None:
        """
        The total surface are factor.

        Returns
        -------
        float
        """
        if self._dimensionless:
            return None
        return self.scale_factor * self.spine_factor

    @property
    def area(self) -> Quantity | None:
        """
        Returns  compartment's surface area (open cylinder) based on its length
        and diameter.

        Returns
        -------
        ~brian2.units.fundamentalunits.Quantity
            A compartment's surface area
        """
        if self._dimensionless:
            logger.warning(
                "Surface area is not defined for the dimensionless "
                "compartment: '%s'\nReturning None instead.",
                self.name
            )
            return None
        try:
            return pi * self.length * self.diameter * self._total_area_factor
        except TypeError:
            logger.warning(
                "Missing parameters [length | diameter] for '%s'."
                "\nCould not calculate the area of '%s', returned None.",
                self.name, self.name
            )
            return None

    @property
    def capacitance(self) -> Quantity | None:
        """
        Returns a compartment's capacitance based on its specific capacitance
        (cm) and surface area. If an absolute capacitance (cm_abs) has been
        provided by the user, it returns this value instead.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        if self._dimensionless:
            if self.cm_abs:
                return self.cm_abs
            logger.warning(
                "Missing parameter [cm_abs] for '%s', returned None.",
                self.name
            )
            return None
        try:
            return self.area * self.cm
        except TypeError:
            logger.warning(
                "Could not calculate the [capacitance] of '%s', returned None.",
                self.name
            )
            return None

    @property
    def g_leakage(self) -> Quantity | None:
        """
        Returns a compartment's absolute leakage conductance based on its 
        specific leakage conductance (gl) and surface area. If an absolute
        leakage conductance (gl_abs) has been provided by the user, it returns
        this value instead.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        if self._dimensionless:
            if self.gl_abs:
                return self.gl_abs
            logger.warning(
                "Missing parameter [gl_abs] for '%s', returned None.",
                self.name
            )
            return None
        try:
            return self.area * self.gl
        except TypeError:
            logger.warning(
                "Could not calculate the [g_leakage] of '%s', returned None.",
                self.name
            )
            return None

    @property
    def parameters(self) -> dict:
        """
        Returns a dictionary of all the major electrophysiological parameters
        that describe a single compartment.

        Returns
        -------
        dict
        """
        d_out = {}
        for value, var in zip([self.v_rest, self.capacitance, self.g_leakage],
                              ['EL', 'C', 'gL']):
            if value:
                if self.name:
                    d_out[f"{var}_{self.name}"] = value
                else:
                    d_out[f"{var}"] = value
            else:
                logger.error(
                    "Could not resolve [%s_%s] for '%s'.",
                    var, self.name, self.name
                )
        d_out.update(self.DEFAULT_PARAMS)
        return d_out

    @property
    def g_cylinder(self) -> Quantity | None:
        """
        The conductance (of coupling currents) passing through a cylindrical
        compartment based on its dimensions and its axial resistance. To be
        used when then the total number of compartments is low and the
        adjacent-to-soma compartments are highly coupled with the soma.

        Returns
        -------
        :class:`~brian2.units.fundamentalunits.Quantity`
        """
        if self._dimensionless:
            raise DimensionlessCompartmentError(
                f"Calculating [g_cylinder] is invalid for '{
                    self.name}', since\n"
                "it is a dimensionless compartment. To connect two dimensionless"
                " compartments, an exact \nvalue for g_couple must be provided."
            )
        try:
            ri = (4*self.r_axial*self.length) / (pi*self.diameter**2)
        except TypeError:
            logger.warning(
                "Could not calculate [g_cylinder] for '%s'.\n"
                "Please make sure that [length, diameter, r_axial]\n"
                "are available.", self.name
            )
            return None
        return 1/ri

    @staticmethod
    def g_couple(comp1: EphysProperties,
                 comp2: EphysProperties) -> Quantity | None:
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
        if any([comp1._dimensionless, comp2._dimensionless]):
            raise DimensionlessCompartmentError(
                ("Cannot automatically calculate the coupling \nconductance of "
                 "dimensionless compartments. To resolve this error, perform\n"
                 "one of the following:\n\n"
                 f"1. Provide [length, diameter, r_axial] for both '{
                     comp1.name}'"
                 f" and '{comp2.name}'.\n\n"
                 f"2. Turn both compartment into dimensionless by providing only"
                 " values for \n   [cm_abs, gl_abs] and then connect them using "
                 "an exact coupling conductance."
                 )
            )
        try:
            r1 = (4 * comp1.r_axial * comp1.length) / (pi * comp1.diameter**2)
            r2 = (4 * comp2.r_axial * comp2.length) / (pi * comp2.diameter**2)
            ri = (r1+r2) / 2
        except TypeError:
            logger.error(
                "Could not calculate the g_couple for '%s' and '%s'.\n"
                "Please make sure that [length, diameter, r_axial] are\n"
                "available for both compartments.", comp1.name, comp2.name
            )
            return None
        return 1/ri
