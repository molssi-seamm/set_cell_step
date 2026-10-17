#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Moving the contents with the cell: molecules rigidly, or atoms affinely."""

import numpy as np
import pytest

molsystem = pytest.importorskip("molsystem")

from set_cell_step.set_cell import SetCell, move_contents  # noqa: E402

L = 12.0
WATER = np.array([[0.0, 0.0, 0.0], [0.9572, 0.0, 0.0], [-0.24, 0.9266, 0.0]])


def waters(n_side=2, length=L):
    """Waters on a grid in a cubic cell, some across its faces."""
    db = molsystem.SystemDB(filename="file:water?mode=memory&cache=shared")
    configuration = db.create_system().create_configuration(periodicity=3)
    configuration.cell.parameters = (length, length, length, 90.0, 90.0, 90.0)
    configuration.coordinate_system = "Cartesian"
    xyz, symbols, i, j = [], [], [], []
    spacing = length / n_side
    for ix in range(n_side):
        for iy in range(n_side):
            for iz in range(n_side):
                origin = np.array([ix, iy, iz]) * spacing + 0.5
                first = len(xyz)
                for atom in WATER:
                    xyz.append(origin + atom)
                symbols += ["O", "H", "H"]
                i += [first, first]
                j += [first + 1, first + 2]
    xyz = np.array(xyz) % length  # wrapped into the cell
    ids = configuration.atoms.append(
        x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2], symbol=symbols
    )
    configuration.bonds.append(i=[ids[a] for a in i], j=[ids[b] for b in j])
    return db, configuration


def oh_lengths(configuration):
    """The O-H bond lengths, by the minimum image."""
    xyz = np.array(configuration.atoms.get_coordinates(fractionals=False))
    cell = np.array(configuration.cell.vectors())
    result = []
    for n in range(0, len(xyz), 3):
        for h in (1, 2):
            d = xyz[n + h] - xyz[n]
            f = d @ np.linalg.inv(cell)
            d = (f - np.round(f)) @ cell
            result.append(np.linalg.norm(d))
    return np.array(result)


def test_molecule_centers_keep_the_bonds():
    db, configuration = waters()
    before = oh_lengths(configuration)
    move_contents(configuration, (1.1 * L,) * 3 + (90.0,) * 3, "molecule centers")
    assert configuration.cell.parameters[0] == pytest.approx(1.1 * L)
    assert oh_lengths(configuration) == pytest.approx(before, abs=1e-6)
    db.close()


def test_atoms_scale_the_bonds():
    db, configuration = waters()
    before = oh_lengths(configuration)
    move_contents(configuration, (1.1 * L,) * 3 + (90.0,) * 3, "atoms")
    assert oh_lengths(configuration) == pytest.approx(1.1 * before, rel=1e-6)
    db.close()


def test_automatic_choice():
    db, configuration = waters()
    how, why = SetCell._scaling("automatic", configuration)
    assert how == "molecule centers" and "8 molecules" in why
    db.close()
    # One molecule: a connected structure, as a solid
    db, configuration = waters(n_side=1)
    how, why = SetCell._scaling("automatic", configuration)
    assert how == "atoms" and "one connected structure" in why
    db.close()
    # Molecules spanning half the cell
    db, configuration = waters(length=3.0)
    how, why = SetCell._scaling("automatic", configuration)
    assert how == "atoms" and "spans the cell" in why
    db.close()
