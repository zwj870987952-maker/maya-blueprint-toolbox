"""Attribute helpers for blueprint Maya operations."""

from ..core.types import AttrPacket, AttrRef, normalize_attr_refs, normalize_node_list
from .common import MayaApiError, UndoChunk, maya_modules
from .scene_nodes import existing_nodes


def set_attribute(nodes, attribute, value, value_type="text"):
    """Set one attribute on each input node."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    converted_value = _convert_value(value, value_type)
    changed_attrs = []

    with UndoChunk("Blueprint Set Attribute"):
        for node in source_nodes:
            attr_path = "{0}.{1}".format(node, attribute)
            if not cmds.objExists(attr_path):
                raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
            if value_type == "text":
                cmds.setAttr(attr_path, converted_value, type="string")
            else:
                cmds.setAttr(attr_path, converted_value)
            changed_attrs.append(attr_path)

    print("Set Attribute: {0} attribute(s).".format(len(changed_attrs)))
    return changed_attrs


def make_attribute_refs(nodes, attribute):
    """Build attribute references for existing nodes."""
    cmds = maya_modules()
    source_nodes = existing_nodes(normalize_node_list(nodes))
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    refs = []
    for node in source_nodes:
        attr_path = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(attr_path):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
        refs.append(AttrRef(node, attribute))

    print("Make Attribute Ref: {0} attribute(s).".format(len(refs)))
    return refs


def inspect_attributes(attr_refs):
    """Return attribute packets with runtime Maya capability data."""
    refs = _existing_attr_refs(attr_refs)
    packets = []
    for attr_ref in refs:
        packets.append(_inspect_attr_ref(attr_ref))

    print("Inspect Attribute: {0} attribute(s).".format(len(packets)))
    return packets


def set_attribute_refs(attr_refs, value, value_type="auto"):
    """Set attributes from AttrRef values."""
    cmds = maya_modules()
    refs = _existing_attr_refs(attr_refs)
    changed_attrs = []

    with UndoChunk("Blueprint Set Attribute Ref"):
        for attr_ref in refs:
            converted_value = _convert_value_for_attr(attr_ref, value, value_type)
            if value_type == "text" or _attr_type(attr_ref) == "string":
                cmds.setAttr(attr_ref.full_attr, "" if converted_value is None else str(converted_value), type="string")
            else:
                cmds.setAttr(attr_ref.full_attr, converted_value)
            changed_attrs.append(attr_ref.full_attr)

    print("Set Attribute Ref: {0} attribute(s).".format(len(changed_attrs)))
    return changed_attrs


def get_attribute_refs(attr_refs):
    """Read values from AttrRef values."""
    cmds = maya_modules()
    refs = _existing_attr_refs(attr_refs)
    values = []
    for attr_ref in refs:
        values.append(cmds.getAttr(attr_ref.full_attr))

    print("Get Attribute Ref: {0} value(s).".format(len(values)))
    if len(values) == 1:
        return values[0]
    return values


def get_attribute(nodes, attribute):
    """Get one attribute from each input node and return values as text."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    values = []
    for node in source_nodes:
        attr_path = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(attr_path):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
        values.append(cmds.getAttr(attr_path))

    value_text = ", ".join(str(value) for value in values)
    print("Get Attribute: {0} value(s).".format(len(values)))
    return value_text


def packets_report(packets):
    """Return a compact, readable report for inspected attributes."""
    lines = []
    for packet in packets or []:
        lines.append(
            "{0} = {1} ({2}, keyable={3}, writable={4}, locked={5}, connected={6})".format(
                packet.attr_ref.full_attr,
                packet.value,
                packet.maya_attr_type or "unknown",
                packet.keyable,
                packet.writable,
                packet.locked,
                packet.connected,
            )
        )
    return "\n".join(lines)


def _existing_attr_refs(attr_refs):
    cmds = maya_modules()
    refs = normalize_attr_refs(attr_refs)
    if not refs:
        raise MayaApiError("No attribute references found.")
    for attr_ref in refs:
        if not cmds.objExists(attr_ref.full_attr):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_ref.full_attr))
    return refs


def _inspect_attr_ref(attr_ref):
    cmds = maya_modules()
    value = None
    try:
        value = cmds.getAttr(attr_ref.full_attr)
    except Exception:
        value = None

    maya_attr_type = _attr_type(attr_ref)
    return AttrPacket(
        attr_ref,
        value=value,
        maya_attr_type=maya_attr_type,
        semantic=_semantic_for_attr(attr_ref.attr),
        axis=_axis_for_attr(attr_ref.attr),
        keyable=_attribute_query(attr_ref, "keyable"),
        writable=_attribute_query(attr_ref, "writable"),
        readable=_attribute_query(attr_ref, "readable"),
        connectable=_attribute_query(attr_ref, "connectable"),
        locked=bool(cmds.getAttr(attr_ref.full_attr, lock=True)),
        connected=bool(cmds.listConnections(attr_ref.full_attr, source=True, destination=True, plugs=True) or []),
        numeric=_is_numeric_attr_type(maya_attr_type),
    )


def _attribute_query(attr_ref, query_flag):
    cmds = maya_modules()
    try:
        return bool(cmds.attributeQuery(attr_ref.attr, node=attr_ref.node, **{query_flag: True}))
    except Exception:
        return False


def _attr_type(attr_ref):
    cmds = maya_modules()
    try:
        return cmds.getAttr(attr_ref.full_attr, type=True) or ""
    except Exception:
        return ""


def _semantic_for_attr(attr):
    clean_attr = attr.rsplit(".", 1)[-1]
    lower_attr = clean_attr.lower()
    if lower_attr.startswith("translate"):
        return "translate"
    if lower_attr.startswith("rotate"):
        return "rotate"
    if lower_attr.startswith("scale"):
        return "scale"
    if lower_attr == "visibility":
        return "visibility"
    return ""


def _axis_for_attr(attr):
    clean_attr = attr.rsplit(".", 1)[-1]
    if clean_attr and clean_attr[-1] in ("X", "Y", "Z"):
        return clean_attr[-1]
    return ""


def _is_numeric_attr_type(maya_attr_type):
    return maya_attr_type in (
        "bool",
        "byte",
        "short",
        "long",
        "float",
        "double",
        "doubleLinear",
        "doubleAngle",
        "enum",
        "time",
    )


def _convert_value_for_attr(attr_ref, value, value_type):
    if value_type and value_type != "auto":
        return _convert_value(value, value_type)

    maya_attr_type = _attr_type(attr_ref)
    if maya_attr_type == "string":
        return "" if value is None else str(value)
    if maya_attr_type == "bool":
        return _convert_value(value, "bool")
    if _is_numeric_attr_type(maya_attr_type):
        return _convert_value(value, "number")
    return value


def _convert_value(value, value_type):
    if value_type == "number":
        return float(value)
    if value_type == "bool":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")
    return "" if value is None else str(value)
