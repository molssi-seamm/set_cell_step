# -*- coding: utf-8 -*-
"""The Set Cell dialog: the controls shown are those whose rules apply, for every
choice that drives the layout. Skipped when no display is available."""

import itertools

import pytest


@pytest.fixture()
def tk_node():
    import tkinter as tk

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("no display available for Tk")
    root.withdraw()
    import Pmw
    import seamm

    Pmw.initialise(root)
    flowchart = seamm.Flowchart(namespace="org.molssi.seamm", directory=".")
    tk_flowchart = seamm.TkFlowchart(
        master=root, flowchart=flowchart, namespace="org.molssi.seamm.tk"
    )
    node = flowchart.create_node("Set Cell")
    flowchart.add_node(node)
    plugin = tk_flowchart.plugin_manager.get("Set Cell")
    tk_node = plugin.create_tk_node(
        tk_flowchart=tk_flowchart, node=node, canvas=tk_flowchart.canvas, x=100, y=100
    )
    yield tk_node
    root.destroy()


def test_dialog_layouts(tk_node):
    tk_node.create_dialog()
    P = tk_node.node.parameters
    choices = {
        "method": P["method"].enumeration,
        "scaling": P["scaling"].enumeration,
    }
    for combination in itertools.product(*choices.values()):
        settings = dict(zip(choices, combination))
        for key, value in settings.items():
            tk_node[key].set(value)
        tk_node.reset_dialog()
        values = {k: tk_node[k].get() for k in P}
        for key in P:
            shown = tk_node[key].grid_info() != {}
            assert shown == P.applies(key, values), (key, settings)
