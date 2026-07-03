"""Runtime data types used by blueprint node execution."""


class PortTypes(object):
    """Canonical port type names for graph validation."""

    ANY = "ANY"
    EXEC = "EXEC"
    STRING = "STRING"
    PATH = "PATH"
    NUMBER = "NUMBER"
    BOOL = "BOOL"
    VALUE = "VALUE"
    NODE_REF = "NODE_REF"
    NODE_LIST = "NODE_LIST"
    ATTR_REF = "ATTR_REF"
    ATTR_LIST = "ATTR_LIST"
    ATTR_PACKET = "ATTR_PACKET"
    FILE_RESULT = "FILE_RESULT"


_ALIASES = {
    "any": PortTypes.ANY,
    "execution": PortTypes.EXEC,
    "text": PortTypes.STRING,
    "path": PortTypes.PATH,
    "number": PortTypes.NUMBER,
    "bool": PortTypes.BOOL,
    "maya_node": PortTypes.NODE_REF,
    "maya_node_list": PortTypes.NODE_LIST,
    "attr_ref": PortTypes.ATTR_REF,
    "attr_list": PortTypes.ATTR_LIST,
    "attr_packet": PortTypes.ATTR_PACKET,
    "file_result": PortTypes.FILE_RESULT,
}


def canonical_port_type(port_type):
    """Return the canonical type name while keeping unknown custom types intact."""
    if port_type is None:
        return ""
    text = str(port_type)
    return _ALIASES.get(text, _ALIASES.get(text.lower(), text.upper()))


def port_types_compatible(source_type, target_type):
    """Return whether an output port may connect to an input port."""
    source = canonical_port_type(source_type)
    target = canonical_port_type(target_type)
    if source == PortTypes.ANY or target == PortTypes.ANY:
        return True
    if source == target:
        return True

    value_sources = set([PortTypes.STRING, PortTypes.PATH, PortTypes.NUMBER, PortTypes.BOOL])
    if target == PortTypes.VALUE and source in value_sources:
        return True
    if source == PortTypes.VALUE and target in value_sources:
        return True

    if source == PortTypes.NODE_REF and target == PortTypes.NODE_LIST:
        return True
    if source == PortTypes.ATTR_REF and target == PortTypes.ATTR_LIST:
        return True

    return False


class NodeRef(object):
    """Reference to a Maya node by name."""

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"type": PortTypes.NODE_REF, "name": self.name}

    def __str__(self):
        return self.name

    def __repr__(self):
        return "NodeRef({0!r})".format(self.name)


class AttrRef(object):
    """Reference to a Maya attribute plug."""

    def __init__(self, node, attr):
        self.node = node
        self.attr = attr
        self.full_attr = "{0}.{1}".format(node, attr)

    @classmethod
    def from_full_attr(cls, full_attr):
        if "." not in full_attr:
            raise ValueError("Attribute reference must look like node.attr: {0}".format(full_attr))
        node, attr = full_attr.split(".", 1)
        return cls(node, attr)

    def to_dict(self):
        return {
            "type": PortTypes.ATTR_REF,
            "node": self.node,
            "attr": self.attr,
            "full_attr": self.full_attr,
        }

    def __str__(self):
        return self.full_attr

    def __repr__(self):
        return "AttrRef({0!r})".format(self.full_attr)


class AttrPacket(object):
    """Attribute reference plus runtime inspection data."""

    def __init__(
        self,
        attr_ref,
        value=None,
        maya_attr_type="",
        semantic="",
        axis="",
        keyable=False,
        writable=False,
        readable=False,
        connectable=False,
        locked=False,
        connected=False,
        numeric=False,
    ):
        self.attr_ref = attr_ref
        self.value = value
        self.maya_attr_type = maya_attr_type
        self.semantic = semantic
        self.axis = axis
        self.keyable = bool(keyable)
        self.writable = bool(writable)
        self.readable = bool(readable)
        self.connectable = bool(connectable)
        self.locked = bool(locked)
        self.connected = bool(connected)
        self.numeric = bool(numeric)

    def to_dict(self):
        return {
            "type": PortTypes.ATTR_PACKET,
            "attr_ref": self.attr_ref.to_dict(),
            "node": self.attr_ref.node,
            "attr": self.attr_ref.attr,
            "full_attr": self.attr_ref.full_attr,
            "value": self.value,
            "maya_attr_type": self.maya_attr_type,
            "semantic": self.semantic,
            "axis": self.axis,
            "keyable": self.keyable,
            "writable": self.writable,
            "readable": self.readable,
            "connectable": self.connectable,
            "locked": self.locked,
            "connected": self.connected,
            "numeric": self.numeric,
        }

    def __repr__(self):
        return "AttrPacket({0!r})".format(self.attr_ref.full_attr)


def normalize_node_list(value):
    """Convert strings, NodeRef objects, or lists into a list of Maya node names."""
    if value is None:
        return []
    if isinstance(value, NodeRef):
        return [value.name]
    if isinstance(value, str):
        return [value]
    nodes = []
    for item in value:
        if isinstance(item, NodeRef):
            nodes.append(item.name)
        else:
            nodes.append(str(item))
    return nodes


def normalize_attr_refs(value):
    """Convert strings, AttrRef objects, AttrPackets, or lists into AttrRef objects."""
    if value is None:
        return []
    if isinstance(value, AttrPacket):
        return [value.attr_ref]
    if isinstance(value, AttrRef):
        return [value]
    if isinstance(value, str):
        return [AttrRef.from_full_attr(value)]

    refs = []
    for item in value:
        if isinstance(item, AttrPacket):
            refs.append(item.attr_ref)
        elif isinstance(item, AttrRef):
            refs.append(item)
        else:
            refs.append(AttrRef.from_full_attr(str(item)))
    return refs
