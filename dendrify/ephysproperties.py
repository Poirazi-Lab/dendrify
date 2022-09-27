from math import pi


class EphysProperties(object):
    """
    WARNING: This class is under development. Some of its features might change
    or become part of the Compartment & NeuronModel classes.

    A class that helps to declare all necessary model parameters.
    """

    def __init__(self, name=None, length=None, diameter=None, cm=None,
                 gl=None, r_axial=None, v_rest=None, scale_factor=1.0,
                 spine_factor=1.0):
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
        """
        Print useful information about an EphysProperties object.
        Usage -> print(object_name)"""
        attrs = self.__dict__
        details = [f"\u2192 {i}: \n{attrs[i]}\n" for i in attrs]
        msg = ("OBJECT:\n{0}\n"
               "\n=======================================================\n\n"
               "ATTRIBUTES:\n{1}")
        return msg.format(self.__class__, "\n".join(details))

    @property
    def total_area_factor(self):
        return self.scale_factor * self.spine_factor

    @property
    def area(self):
        """
        Returns the surface area a of a compartment (open cylinder) based
        on its length and diameter.

        Returns
        -------
        TYPE
            Description
        """
        try:
            return pi * self.length * self.diameter * self.total_area_factor
        except TypeError:
            print(("ERROR: Missing Parameters ('length' or 'diameter')\n"
                  f"Could not calculate the area of <{self.name}>, "
                   "returned None instead\n"))

    @property
    def capacitance(self):
        """
        Returns the absolute membrane capacitance of a single compartment
        based on its surface area and its specific membrane capacitance.
        """
        try:
            return self.area * self.cm
        except TypeError:
            print(("ERROR: Missing Parameters ('cm')\n"
                  f"Could not calculate the capacitance of <{self.name}>, "
                   "returned None instead"))

    @property
    def g_leakage(self):
        """
        Returns the absolute leakage conductance of a single compartment based
        on its surface area and its specific leakage conductance.
        """
        try:
            return self.area * self.gl
        except TypeError:
            print(("ERROR: Missing Parameters ('gl')\n"
                  f"Could not calculate the g_leakage of <{self.name}>, "
                   "returned None instead"))

    @property
    def parameters(self):
        """parameters _summary_

        Returns
        -------
        _type_
            _description_
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
    def g_cylinder(self):
        """
        The conductance (of coupling currents) passing through a cylindri_cal
        compartment based on its dimensions and its axial resistance. To be
        used when then the total number of compartments is low and the
        adjacent-to-soma compartments are highly coupled with the soma.
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
    def g_couple(comp1, comp2):
        """
        The conductance (of coupling currents) between the centers of
        two adjacent cylindrical compartments, based on their dimensions
        and the axial resistance.

        Parameters
        ----------
        comp1 : TYPE
            Description
        comp2 : TYPE
            Description

        Returns
        -------
        TYPE
            Description
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
