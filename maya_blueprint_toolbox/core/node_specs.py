# -*- coding: utf-8 -*-
"""Built-in node specifications for the blueprint canvas."""


PORT_LABELS = {
    "value": "值",
    "nodes": "节点",
    "selected_nodes": "已选择节点",
    "renamed_nodes": "重命名节点",
    "group_node": "组节点",
    "attrs": "属性引用",
    "report": "报告",
    "drivers": "驱动节点",
    "driven": "被驱动节点",
    "constraints": "约束节点",
    "file_path": "文件路径",
    "imported_nodes": "导入节点",
    "target_path": "目标路径",
    "result": "结果",
}


class PortSpec(object):
    """Describes a typed node input or output port."""

    def __init__(self, name, port_type, label=None, required=True):
        self.name = name
        self.port_type = port_type
        self.label = label or PORT_LABELS.get(name, name)
        self.required = required

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.port_type,
            "label": self.label,
            "required": self.required,
        }


class ParameterSpec(object):
    """Describes an editable node parameter."""

    def __init__(
        self,
        name,
        param_type,
        label=None,
        default=None,
        choices=None,
        required=False,
        choice_labels=None,
    ):
        self.name = name
        self.param_type = param_type
        self.label = label or name
        self.default = default
        self.choices = choices or []
        self.required = required
        self.choice_labels = choice_labels or list(self.choices)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.param_type,
            "label": self.label,
            "default": self.default,
            "choices": list(self.choices),
            "choice_labels": list(self.choice_labels),
            "required": self.required,
        }


class NodeSpec(object):
    """Describes a node type that can be instantiated on the canvas."""

    def __init__(self, node_type, title, category, inputs=None, outputs=None, parameters=None):
        self.node_type = node_type
        self.title = title
        self.category = category
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.parameters = parameters or []

    def default_parameters(self):
        values = {}
        for parameter in self.parameters:
            values[parameter.name] = parameter.default
        return values

    def to_dict(self):
        return {
            "type": self.node_type,
            "title": self.title,
            "category": self.category,
            "inputs": [port.to_dict() for port in self.inputs],
            "outputs": [port.to_dict() for port in self.outputs],
            "parameters": [parameter.to_dict() for parameter in self.parameters],
        }


def _built_in_specs():
    return [
        NodeSpec(
            "constant.text",
            "文本",
            "常量",
            outputs=[PortSpec("value", "STRING")],
            parameters=[
                ParameterSpec("value", "text", "值", "", required=False),
            ],
        ),
        NodeSpec(
            "constant.number",
            "数字",
            "常量",
            outputs=[PortSpec("value", "NUMBER")],
            parameters=[
                ParameterSpec("value", "number", "值", 0.0, required=False),
            ],
        ),
        NodeSpec(
            "constant.bool",
            "布尔",
            "常量",
            outputs=[PortSpec("value", "BOOL")],
            parameters=[
                ParameterSpec("value", "bool", "值", False, required=False),
            ],
        ),
        NodeSpec(
            "constant.path",
            "路径",
            "常量",
            outputs=[PortSpec("value", "PATH")],
            parameters=[
                ParameterSpec("value", "path", "路径", "", required=True),
            ],
        ),
        NodeSpec(
            "maya.nodes.node_names",
            "节点名称",
            "Maya / 节点",
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("names", "text", "名称", "", required=True),
            ],
        ),
        NodeSpec(
            "maya.selection.current",
            "当前选择",
            "Maya / 选择",
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("include_shapes", "bool", "包含 Shape", False),
            ],
        ),
        NodeSpec(
            "maya.selection.select_nodes",
            "选择节点",
            "Maya / 选择",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("selected_nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.nodes.rename",
            "重命名节点",
            "Maya / 节点",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("renamed_nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("base_name", "text", "基础名称", "renamed", required=True),
                ParameterSpec("start_index", "number", "起始编号", 1.0),
                ParameterSpec("padding", "number", "补零位数", 2.0),
            ],
        ),
        NodeSpec(
            "maya.nodes.group",
            "打组节点",
            "Maya / 节点",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("group_node", "NODE_LIST")],
            parameters=[
                ParameterSpec("group_name", "text", "组名称", "blueprint_grp", required=True),
            ],
        ),
        NodeSpec(
            "maya.nodes.delete",
            "删除节点",
            "Maya / 节点",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[],
        ),
        NodeSpec(
            "maya.attributes.make_ref",
            "创建属性引用",
            "Maya / 属性",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("attrs", "ATTR_LIST")],
            parameters=[
                ParameterSpec("attribute", "text", "属性", "", required=True),
            ],
        ),
        NodeSpec(
            "maya.attributes.inspect",
            "检查属性",
            "Maya / 属性",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[
                PortSpec("value", "VALUE"),
                PortSpec("report", "STRING"),
            ],
        ),
        NodeSpec(
            "maya.attributes.set",
            "设置属性",
            "Maya / 属性",
            inputs=[
                PortSpec("attrs", "ATTR_LIST"),
                PortSpec("value", "VALUE"),
            ],
            outputs=[],
            parameters=[
                ParameterSpec(
                    "value_type",
                    "choice",
                    "值类型",
                    "auto",
                    choices=["auto", "text", "number", "bool"],
                    choice_labels=["自动", "文本", "数字", "布尔"],
                ),
            ],
        ),
        NodeSpec(
            "maya.attributes.get",
            "获取属性",
            "Maya / 属性",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[PortSpec("value", "VALUE")],
        ),
        NodeSpec(
            "maya.constraints.parent",
            "父子约束",
            "Maya / 约束",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.point",
            "点约束",
            "Maya / 约束",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.orient",
            "方向约束",
            "Maya / 约束",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.scale",
            "缩放约束",
            "Maya / 约束",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.io.import_file",
            "导入文件",
            "Maya / 文件",
            inputs=[PortSpec("file_path", "PATH")],
            outputs=[
                PortSpec("imported_nodes", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec(
                    "mode",
                    "choice",
                    "模式",
                    "import",
                    choices=["import", "reference"],
                    choice_labels=["导入", "引用"],
                ),
                ParameterSpec("namespace", "text", "命名空间", ""),
                ParameterSpec("preserve_references", "bool", "保留引用", True),
            ],
        ),
        NodeSpec(
            "maya.io.export_fbx",
            "导出 FBX",
            "Maya / 文件",
            inputs=[
                PortSpec("nodes", "NODE_LIST"),
                PortSpec("target_path", "PATH"),
            ],
            outputs=[PortSpec("result", "FILE_RESULT")],
            parameters=[
                ParameterSpec("bake_animation", "bool", "烘焙动画", False),
                ParameterSpec("frame_start", "number", "起始帧", 1.0),
                ParameterSpec("frame_end", "number", "结束帧", 120.0),
                ParameterSpec("overwrite_existing", "bool", "覆盖已有文件", False),
            ],
        ),
    ]


def default_node_specs():
    specs = {}
    for spec in _built_in_specs():
        specs[spec.node_type] = spec
    return specs
