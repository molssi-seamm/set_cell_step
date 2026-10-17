.. _user-guide:

**********
User Guide
**********

The Set Cell step changes the periodic cell of the current structure and moves its
contents with it.

How the cell is changed
=======================

"Adjust cell by" chooses how:

* **density** or **volume**: scale the cell uniformly to a density or a volume. Either
  may be a variable, e.g. a density saved from an earlier step.
* **the mean volume of the last NPT run**: scale the cell uniformly to the mean
  volume of the last NPT run earlier in the flowchart, over its equilibrated part
  (the mean volume, not the cube of the mean length). This is the usual way to
  prepare constant-volume production runs of a liquid at its equilibrium density:

  .. code-block:: text

      Model Chemistry, Packmol, minimization
      LAMMPS: velocities, NPT equilibration
      Set Cell: the mean volume of the last NPT run
      LAMMPS: NVT equilibration, then the production runs

* **cell parameters**: set a, b, c and the angles.
* **uniform contraction/expansion**: change the volume by a fraction, e.g. "1%" or
  "-2%".

How the contents move
=====================

"Move the contents by" chooses how the atoms follow the cell:

* **molecule centers**: each molecule is made whole and moved rigidly with its center
  of mass, so its bonds and angles are unchanged. This is what a liquid of molecules
  needs: scaling the atoms instead would stretch every bond, which a rigid water
  model's constraints (SHAKE) cannot recover from in the first step.
* **atoms**: every atom is scaled with the cell (an affine transformation, keeping the
  fractional coordinates), as for a crystal or an extended network.
* **automatic** (the default): molecule centers when the system is made of separate
  molecules, none of them spanning the cell; the atoms otherwise. The output says
  which was used and why.

The velocities are not changed.

Results
=======

The new volume, density and cell parameters, which can be stored in variables or
tables.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
