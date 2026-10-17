=======
History
=======
2026.10.17 -- Set the cell to the mean volume of an NPT run, moving molecules rigidly
    * A new way to set the cell: the mean volume of the last NPT run earlier in the
      flowchart, over its equilibrated part -- the usual preparation of
      constant-volume runs of a liquid at its equilibrium density. Setting a density
      or a volume, including from a variable, works as before.
    * A new option, how the contents follow the cell: the molecules moved rigidly with
      their centers, so their bonds are unchanged, or the atoms scaled with the cell.
      By default the molecules for a system of separate molecules and the atoms for a
      solid or an extended network. Before, the atoms were scaled, which stretched the
      bonds of every molecule; a rigid water model could then fail in its first step.
    * Bugfix: "uniform contraction/expansion" with a percentage (the default, "1%")
      failed.
    * The volume, density and cell parameters are results, for variables and tables.
    * Internal: the package, its tests, documentation and CI are brought up to date
      (Python 3.12, current SEAMM).


2021.2.12 (12 February 2021)
----------------------------

* Updated the README file to give a better description.
* Updated the short description in setup.py to work with the new installer.
* Added keywords for better searchability.

2021.2.4 (4 February 2021)
--------------------------

* Updated for compatibility with the new system classes in MolSystem
  2021.2.2 release.

2020.12.5 (5 December 2020)
---------------------------

* Internal: switching CI from TravisCI to GitHub Actions, and in the
  process moving documentation from ReadTheDocs to GitHub Pages where
  it is consolidated with the main SEAMM documentation.


2020.11.13 (13 November 2020)
-----------------------------

* First release on PyPI.
