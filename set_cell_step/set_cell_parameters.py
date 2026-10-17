# -*- coding: utf-8 -*-
"""
Control parameters for the Set Cell step in a SEAMM flowchart
"""

import logging
import seamm
import pprint  # noqa: F401

logger = logging.getLogger(__name__)


class SetCellParameters(seamm.Parameters):
    """
    The control parameters for Set Cell.

    The developer will add a dictionary of Parameters to this class.
    The keys are parameters for the current plugin, which themselves
    might be dictionaries.

    You need to replace the 'time' example below with one or more
    definitions of the control parameters for your plugin and application.

    Attributes
    ----------
    parameters : {'kind', 'default', 'default_units', 'enumeration',
                  'format_string', description', help_text'}
        A dictionary containing the parameters for the current step.
        Each key of the dictionary is a dictionary that contains the
        the following keys: kind, default, default_units, enumeration,
        format_string, description and help text.

    parameters['kind']: custom
        Specifies the kind of a variable. While the 'kind' of a variable might
        be a numeric value, it may still have enumerated custom values
        meaningful to the user. For instance, if the parameter is
        a convergence criterion for an optimizer, custom values like 'normal',
        'precise', etc, might be adequate. In addition, any
        parameter can be set to a variable of expression, indicated by having
        '$' as the first character in the field. For example, $OPTIMIZER_CONV.

    parameters['default'] : 'integer' or 'float' or 'string' or 'boolean' or
        'enum' The default value of the parameter, used to reset it.

    parameters['default_units'] : str
        The default units, used for resetting the value.

    parameters['enumeration']: tuple
        A tuple of enumerated values.

    parameters['format_string']: str
        A format string for 'pretty' output.

    parameters['description']: str
        A short string used as a prompt in the GUI.

    parameters['help_text']: tuple
        A longer string to display as help for the user.

    See Also
    --------
    SetCell, TkSetCell, SetCell
    SetCellParameters, Set CellStep

    Examples
    --------
    parameters = {
        "time": {
            "default": 100.0,
            "kind": "float",
            "default_units": "ps",
            "enumeration": tuple(),
            "format_string": ".1f",
            "description": "Simulation time:",
            "help_text": ("The time to simulate in the dynamics run.")
        },
    }
    """

    parameters = {
        "method": {
            "default": "density",
            "kind": "enumeration",
            "default_units": None,
            "enumeration": (
                "density",
                "volume",
                "the mean volume of the last NPT run",
                "cell parameters",
                "uniform contraction/expansion",
            ),
            "format_string": "",
            "description": "Adjust cell by:",
            "help_text": (
                "How to adjust the cell: to a density or volume, which may be "
                "variables; to the mean volume of the last NPT run earlier in the "
                "flowchart, over its equilibrated part; to given cell parameters; "
                "or by a uniform contraction or expansion."
            ),
        },
        "scaling": {
            "default": "automatic",
            "kind": "enumeration",
            "default_units": None,
            "enumeration": ("automatic", "molecule centers", "atoms"),
            "format_string": "",
            "description": "Move the contents by:",
            "help_text": (
                "How the contents follow the cell. 'molecule centers' moves each "
                "molecule rigidly with its center of mass, as a liquid of molecules "
                "needs: scaling the atoms would stretch the bonds. 'atoms' scales "
                "every atom with the cell (an affine transformation), as for a "
                "solid. 'automatic' moves the molecules' centers when the system is "
                "made of separate molecules, none spanning the cell, and the atoms "
                "otherwise."
            ),
        },
        "density": {
            "applies_when": {"method": "density"},
            "default": "1",
            "kind": "float",
            "default_units": "g/mL",
            "enumeration": tuple(),
            "format_string": ".3f",
            "description": "Density:",
            "help_text": ("The target density of the cell."),
        },
        "volume": {
            "applies_when": {"method": "volume"},
            "default": "1000",
            "kind": "float",
            "default_units": "Å^3",
            "enumeration": tuple(),
            "format_string": ".3f",
            "description": "Volume:",
            "help_text": ("The target volume of the cell."),
        },
        "expansion": {
            "applies_when": {"method": "uniform contraction/expansion"},
            "default": "1%",
            "kind": "str",
            "default_units": None,
            "enumeration": tuple(),
            "format_string": "",
            "description": "Percent contraction (-)/expansion(+):",
            "help_text": (
                "The amount to contract (negative value) or expand (positive "
                "value). The change is proportional to current cell lengths "
                " and does not affect the angles."
            ),
        },
        "a": {
            "applies_when": {"method": "cell parameters"},
            "default": "10",
            "kind": "float",
            "default_units": "Å",
            "enumeration": None,
            "format_string": ".2f",
            "description": "a:",
            "help_text": ("The length of the first side of the cell."),
        },
        "b": {
            "applies_when": {"method": "cell parameters"},
            "default": "10",
            "kind": "float",
            "default_units": "Å",
            "enumeration": None,
            "format_string": ".2f",
            "description": "b:",
            "help_text": ("The length of the second side of the cell."),
        },
        "c": {
            "applies_when": {"method": "cell parameters"},
            "default": "10",
            "kind": "float",
            "default_units": "Å",
            "enumeration": None,
            "format_string": ".2f",
            "description": "c:",
            "help_text": ("The length of the third side of the cell."),
        },
        "alpha": {
            "applies_when": {"method": "cell parameters"},
            "default": 90.0,
            "kind": "float",
            "default_units": "degree",
            "enumeration": None,
            "format_string": ".1f",
            "description": "alpha:",
            "help_text": ("The angle between a and b."),
        },
        "beta": {
            "applies_when": {"method": "cell parameters"},
            "default": 90.0,
            "kind": "float",
            "default_units": "degree",
            "enumeration": None,
            "format_string": ".1f",
            "description": "beta:",
            "help_text": ("The angle between a and c."),
        },
        "gamma": {
            "applies_when": {"method": "cell parameters"},
            "default": 90.0,
            "kind": "float",
            "default_units": "degree",
            "enumeration": None,
            "format_string": ".1f",
            "description": "gamma:",
            "help_text": ("The angle between b and c."),
        },
    }

    def __init__(self, defaults={}, data=None):
        """
        Initialize the parameters, by default with the parameters defined above

        Parameters
        ----------
        defaults: dict
            A dictionary of parameters to initialize. The parameters
            above are used first and any given will override/add to them.
        data: dict
            A dictionary of keys and a subdictionary with value and units
            for updating the current, default values.

        Returns
        -------
        None
        """

        logger.debug("SetCellParameters.__init__")

        super().__init__(
            defaults={**SetCellParameters.parameters, **defaults}, data=data
        )
