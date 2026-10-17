# -*- coding: utf-8 -*-

"""Non-graphical part of the Set Cell step in a SEAMM flowchart"""

import logging

import numpy as np
import pprint  # noqa: F401

import set_cell_step
import seamm
from seamm_util import ureg, Q_  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: 'job' and 'printer'. 'job' send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# 'printer' sends output to the file 'step.out' in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Set Cell")


def move_contents(configuration, parameters, how):
    """Set a new cell and move the contents with it.

    Parameters
    ----------
    configuration : molsystem._Configuration
        The periodic structure to change.
    parameters : (a, b, c, alpha, beta, gamma)
        The new cell parameters, in Å and degrees.
    how : str
        "molecule centers" to make each molecule whole and move it rigidly with its
        center of mass, keeping its bonds; "atoms" for an affine transformation of
        every atom.
    """
    old_cell = np.array(configuration.cell.vectors(), dtype=float)
    if how == "molecule centers":
        configuration.reimage_bonded_atoms(reimage_molecules=False)
        xyz = np.array(configuration.atoms.get_coordinates(fractionals=False))
        masses = np.array(configuration.atoms.atomic_masses, dtype=float)
        configuration.cell.parameters = parameters
        new_cell = np.array(configuration.cell.vectors(), dtype=float)
        transform = np.linalg.inv(old_cell) @ new_cell
        for molecule in configuration.find_molecules(as_indices=True):
            m = masses[molecule]
            center = (m[:, None] * xyz[molecule]).sum(axis=0) / m.sum()
            xyz[molecule] += center @ transform - center
        configuration.atoms.set_coordinates(xyz, fractionals=False)
    elif how == "atoms":
        # The fractional coordinates stay the same
        fractionals = configuration.atoms.get_coordinates(fractionals=True)
        configuration.cell.parameters = parameters
        configuration.atoms.set_coordinates(fractionals, fractionals=True)
    else:
        raise ValueError(f"Don't know how to move the contents: '{how}'")


class SetCell(seamm.Node):
    """
    The non-graphical part of a Set Cell step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : SetCellParameters
        The control parameters for Set Cell.

    See Also
    --------
    TkSetCell,
    SetCell, SetCellParameters
    """

    def __init__(self, flowchart=None, title="Set Cell", extension=None, logger=logger):
        """A step for Set Cell in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug("Creating Set Cell {}".format(self))

        super().__init__(
            flowchart=flowchart,
            title="Set Cell",
            extension=extension,
            module=__name__,
            logger=logger,
        )  # yapf: disable

        self.parameters = set_cell_step.SetCellParameters()

    @property
    def version(self):
        """The semantic version of this module."""
        return set_cell_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return set_cell_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.

        Returns
        -------
        str
            A description of the current step.
        """
        if not P:
            P = self.parameters.values_to_dict()

        method = P["method"]

        if method == "density":
            density = P["density"]
            if self.is_expr(density):
                text = (
                    "The cell will be adjusted isotropically to a density "
                    f"given by '{density}'."
                )
            else:
                text = (
                    "The cell will be adjusted isotropically to a density "
                    f"of {density}."
                )
        elif method == "volume":
            volume = P["volume"]
            if self.is_expr(volume):
                text = (
                    "The cell will be adjusted isotropically to a volume "
                    f"given by '{volume}'."
                )
            else:
                text = (
                    "The cell will be adjusted isotropically to a volume "
                    f"of {volume}."
                )
        elif method == "the mean volume of the last NPT run":
            text = (
                "The cell will be adjusted isotropically to the mean volume of the "
                "last NPT run earlier in the flowchart, over its equilibrated part."
            )
        elif method == "cell parameters":
            text = "The cell parameters will be set as follows:"
            for parameter in ("a", "b", "c", "alpha", "beta", "gamma"):
                text += f"  {parameter:>5}: {P[parameter]}"
        elif method == "uniform contraction/expansion":
            text = (
                f"The cell will be adjusted isotropically by {P['expansion']} "
                "in each direction."
            )
        else:
            raise RuntimeError(f"Don't recognize method '{method}'!")

        scaling = P.get("scaling", "automatic")
        if scaling == "automatic":
            text += (
                " The molecules will move rigidly with their centers if the system "
                "is made of separate molecules; otherwise the atoms are scaled."
            )
        elif scaling == "molecule centers":
            text += " The molecules will move rigidly with their centers."
        elif scaling == "atoms":
            text += " The atoms will be scaled with the cell."
        else:
            text += f" The contents will be moved as '{scaling}' gives."

        return self.header + "\n" + __(text, **P, indent=4 * " ").__str__()

    def run(self):
        """Run a Set Cell step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)
        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Print what we are doing -- getting formatted values for printing
        PP = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data, formatted=True, units=False
        )
        self.logger.debug(f"Formatted values:\n{pprint.pformat(PP)}")
        printer.normal(__(self.description_text(PP), indent=self.indent))

        method = P["method"]
        system_db = self.get_variable("_system_db")
        configuration = system_db.system.configuration

        cell = configuration.cell
        a, b, c, alpha, beta, gamma = cell.parameters
        if method in ("density", "volume", "the mean volume of the last NPT run"):
            if method == "density":
                rho = P["density"].to("g/mL").magnitude
                delta = (configuration.density / rho) ** (1 / 3)
            else:
                if method == "volume":
                    V = P["volume"].to("Å^3").magnitude
                else:
                    V, where = self._npt_volume()
                    printer.normal(
                        __(
                            f"The mean volume of the NPT run {where} is {V:.1f} Å^3.",
                            indent=self.indent + 4 * " ",
                        )
                    )
                delta = (V / configuration.volume) ** (1 / 3)
            a, b, c = a * delta, b * delta, c * delta
        elif method == "cell parameters":
            a = P["a"].to("Å").magnitude
            b = P["b"].to("Å").magnitude
            c = P["c"].to("Å").magnitude
            alpha = P["alpha"].to("degree").magnitude
            beta = P["beta"].to("degree").magnitude
            gamma = P["gamma"].to("degree").magnitude
        elif method == "uniform contraction/expansion":
            expansion = P["expansion"]
            if isinstance(expansion, str):
                value = expansion.strip()
                expansion = (
                    float(value[:-1]) / 100 if value.endswith("%") else float(value)
                )
            delta = (1 + expansion) ** (1 / 3)
            a, b, c = a * delta, b * delta, c * delta
        else:
            raise RuntimeError(f"Don't recognize method '{method}'!")

        scaling, why = self._scaling(P.get("scaling", "automatic"), configuration)
        move_contents(configuration, (a, b, c, alpha, beta, gamma), scaling)

        text = "\nAdjusted the cell:\n"
        text += f"         a: {a:8.3f}\n"
        text += f"         b: {b:8.3f}\n"
        text += f"         c: {c:8.3f}\n"
        text += f"     alpha: {alpha:7.2f}\n"
        text += f"      beta: {beta:7.2f}\n"
        text += f"     gamma: {gamma:7.2f}\n"
        text += "\n"
        text += f"    volume: {configuration.volume:10.1f} Å^3\n"
        text += f"   density: {configuration.density:11.4f} g/mL\n"
        printer.normal(__(text, indent=self.indent + 4 * " ", wrap=False))
        printer.normal(__(why, indent=self.indent + 4 * " "))
        printer.normal("")

        self.store_results(
            configuration=configuration,
            data={
                "volume": configuration.volume,
                "density": configuration.density,
                "a": a,
                "b": b,
                "c": c,
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
            },
        )

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return next_node

    def _npt_volume(self):
        """The mean volume of the last NPT run, over its equilibrated part.

        Returns
        -------
        (float, str)
            The volume in Å^3, and which run it is, for the output.
        """
        from seamm_md_analysis import open_md, run_state

        records = []
        if self.variable_exists("_md_runs"):
            records = self.get_variable("_md_runs")
        for record in reversed(list(records)):
            if record.get("ensemble") != "NPT":
                continue
            with open_md(record["path"]) as md:
                volume = run_state(md).volume
            if volume is not None:
                return volume, f"of step {record.get('step', record['path'])}"
        raise RuntimeError(
            "Set Cell is to use the mean volume of the last NPT run, but no NPT run "
            "earlier in the flowchart recorded its volume."
        )

    @staticmethod
    def _scaling(scaling, configuration):
        """How to move the contents, and why, for the output."""
        if scaling == "molecule centers":
            return scaling, "The molecules were moved rigidly with their centers."
        if scaling == "atoms":
            return scaling, "The atoms were scaled with the cell."
        if scaling != "automatic":
            raise RuntimeError(f"Don't recognize how to move the contents: {scaling}")

        from seamm_md_analysis.step_support import cell_widths, molecule_extents

        molecules = configuration.find_molecules(as_indices=True)
        if len(molecules) < 2:
            return "atoms", (
                "The atoms were scaled with the cell: the system is one connected "
                "structure, as in a solid."
            )
        if configuration.periodicity == 3:
            width = min(cell_widths(configuration.cell.vectors()))
            longest = max(molecule_extents(configuration))
            if longest >= width / 2:
                return "atoms", (
                    "The atoms were scaled with the cell: a molecule spans the cell, "
                    "as in an extended network or a solid."
                )
        return "molecule centers", (
            f"The {len(molecules)} molecules were moved rigidly with their centers, "
            "so their bonds are unchanged."
        )
