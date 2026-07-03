"""Scene node helpers for blueprint Maya operations."""

from .common import MayaApiError, UndoChunk, maya_modules
from .selection import replace_selection


def parse_node_names(names_text):
    """Parse comma/newline separated Maya node names."""
    if not names_text:
        return []

    normalized = names_text.replace("\n", ",").replace(";", ",")
    names = []
    for raw_name in normalized.split(","):
        name = raw_name.strip()
        if name:
            names.append(name)
    return names


def existing_nodes(nodes, label="nodes"):
    """Return existing nodes, raising when no input nodes exist."""
    cmds = maya_modules()
    found_nodes = [node for node in (nodes or []) if cmds.objExists(node)]
    if not found_nodes:
        raise MayaApiError("No existing {0} found.".format(label))
    return found_nodes


def select_nodes(nodes):
    """Select nodes and return the nodes that were selected."""
    selected_nodes = replace_selection(existing_nodes(nodes))
    print("Select Nodes: {0} node(s).".format(len(selected_nodes)))
    return selected_nodes


def rename_nodes(nodes, base_name, start_index=1, padding=2):
    """Rename nodes using base_name plus an incrementing index."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not base_name:
        raise MayaApiError("Rename base name is required.")

    renamed_nodes = []
    start_index = int(start_index)
    padding = max(0, int(padding))

    with UndoChunk("Blueprint Rename Nodes"):
        for offset, node in enumerate(source_nodes):
            index_text = str(start_index + offset).zfill(padding)
            new_name = "{0}_{1}".format(base_name, index_text)
            renamed_name = cmds.rename(node, new_name)
            long_names = cmds.ls(renamed_name, long=True) or [renamed_name]
            renamed_nodes.append(long_names[0])

    print("Rename Nodes: {0} node(s).".format(len(renamed_nodes)))
    return renamed_nodes


def group_nodes(nodes, group_name):
    """Group nodes under a new transform and return the group node."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not group_name:
        raise MayaApiError("Group name is required.")

    with UndoChunk("Blueprint Group Nodes"):
        group_node = cmds.group(source_nodes, name=group_name)

    long_names = cmds.ls(group_node, long=True) or [group_node]
    print("Group Nodes: {0} node(s) into {1}.".format(len(source_nodes), group_node))
    return [long_names[0]]


def delete_nodes(nodes):
    """Delete nodes from the Maya scene."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    with UndoChunk("Blueprint Delete Nodes"):
        cmds.delete(source_nodes)
    print("Delete Nodes: {0} node(s).".format(len(source_nodes)))
    return True
