# -*- coding: utf-8 -*-
"""Workflow execution engine for Maya Blueprint Toolbox."""

from ..maya_api import attributes, constraints, export, io, scene_nodes, selection
from ..maya_api.common import MayaApiError


class WorkflowExecutionError(RuntimeError):
    """Raised when a workflow cannot be executed."""


class WorkflowExecutor(object):
    """Executes serialized blueprint workflow data."""

    def __init__(self, node_specs):
        self.node_specs = node_specs

    def execute(self, workflow_data, status_callback=None):
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", [])
        nodes_by_id = dict((node["id"], node) for node in nodes)
        order = self._topological_order(nodes_by_id, connections)
        results = {}

        for node_id in order:
            node_data = nodes_by_id[node_id]
            input_values = self._collect_inputs(node_id, connections, results)
            self._emit_status(status_callback, node_id, "running", "运行中")
            try:
                outputs = self._execute_node(node_data, input_values)
            except Exception as error:
                self._emit_status(status_callback, node_id, "failed", str(error))
                raise
            results[node_id] = outputs
            self._emit_status(status_callback, node_id, "success", "成功")

        return results

    def _emit_status(self, status_callback, node_id, status, message):
        if status_callback is not None:
            status_callback(node_id, status, message)

    def _topological_order(self, nodes_by_id, connections):
        dependencies = dict((node_id, set()) for node_id in nodes_by_id)
        dependents = dict((node_id, set()) for node_id in nodes_by_id)

        for connection in connections:
            source_node = connection.get("source_node")
            target_node = connection.get("target_node")
            if source_node not in nodes_by_id or target_node not in nodes_by_id:
                continue
            dependencies[target_node].add(source_node)
            dependents[source_node].add(target_node)

        ready = sorted(node_id for node_id, deps in dependencies.items() if not deps)
        ordered = []

        while ready:
            node_id = ready.pop(0)
            ordered.append(node_id)
            for dependent_id in sorted(dependents[node_id]):
                dependencies[dependent_id].discard(node_id)
                if not dependencies[dependent_id] and dependent_id not in ordered and dependent_id not in ready:
                    ready.append(dependent_id)
            ready.sort()

        if len(ordered) != len(nodes_by_id):
            raise WorkflowExecutionError("Workflow has a cycle or unresolved dependency.")

        return ordered

    def _collect_inputs(self, node_id, connections, results):
        input_values = {}
        for connection in connections:
            if connection.get("target_node") != node_id:
                continue
            source_node = connection.get("source_node")
            source_port = connection.get("source_port")
            target_port = connection.get("target_port")
            source_outputs = results.get(source_node, {})
            input_values[target_port] = source_outputs.get(source_port)
        return input_values

    def _execute_node(self, node_data, input_values):
        node_type = node_data.get("type")
        parameters = node_data.get("parameters", {})

        if node_type == "constant.text":
            return {"value": parameters.get("value", "")}
        if node_type == "constant.number":
            return {"value": float(parameters.get("value", 0.0) or 0.0)}
        if node_type == "constant.bool":
            return {"value": bool(parameters.get("value", False))}
        if node_type == "constant.path":
            return {"value": parameters.get("value", "")}
        if node_type == "maya.nodes.node_names":
            return self._execute_node_names(parameters)
        if node_type == "maya.selection.current":
            return self._execute_current_selection(parameters)
        if node_type == "maya.selection.select_nodes":
            return self._execute_select_nodes(input_values)
        if node_type == "maya.nodes.rename":
            return self._execute_rename_nodes(parameters, input_values)
        if node_type == "maya.nodes.group":
            return self._execute_group_nodes(parameters, input_values)
        if node_type == "maya.nodes.delete":
            return self._execute_delete_nodes(input_values)
        if node_type == "maya.attributes.make_ref":
            return self._execute_make_attribute_refs(parameters, input_values)
        if node_type == "maya.attributes.inspect":
            return self._execute_inspect_attributes(input_values)
        if node_type == "maya.attributes.set":
            return self._execute_set_attribute(parameters, input_values)
        if node_type == "maya.attributes.get":
            return self._execute_get_attribute(parameters, input_values)
        if node_type.startswith("maya.constraints."):
            return self._execute_constraint(node_type, parameters, input_values)
        if node_type == "maya.io.import_file":
            return self._execute_import_file(parameters, input_values)
        if node_type == "maya.io.export_fbx":
            return self._execute_export_fbx(parameters, input_values)

        raise WorkflowExecutionError("No executor registered for node type: {0}".format(node_type))

    def _execute_node_names(self, parameters):
        return {"nodes": scene_nodes.parse_node_names(parameters.get("names", ""))}

    def _execute_current_selection(self, parameters):
        include_shapes = bool(parameters.get("include_shapes", False))
        try:
            nodes = selection.get_current_selection(include_shapes=include_shapes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"nodes": nodes}

    def _execute_select_nodes(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            selected_nodes = scene_nodes.select_nodes(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {
            "selected_nodes": selected_nodes,
            "done": True,
        }

    def _execute_rename_nodes(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        try:
            renamed_nodes = scene_nodes.rename_nodes(
                nodes,
                parameters.get("base_name", ""),
                start_index=parameters.get("start_index", 1.0),
                padding=parameters.get("padding", 2.0),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"renamed_nodes": renamed_nodes}

    def _execute_group_nodes(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        try:
            group_node = scene_nodes.group_nodes(
                nodes,
                parameters.get("group_name", ""),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"group_node": group_node}

    def _execute_delete_nodes(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            done = scene_nodes.delete_nodes(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"done": done}

    def _execute_set_attribute(self, parameters, input_values):
        value = input_values.get("value")
        value_type = parameters.get("value_type", "auto")

        if input_values.get("attrs"):
            try:
                changed_attrs = attributes.set_attribute_refs(
                    input_values.get("attrs"),
                    value,
                    value_type=value_type,
                )
            except MayaApiError as error:
                raise WorkflowExecutionError(str(error))
            return {
                "done": True,
            }

        raise WorkflowExecutionError("设置属性需要连接 属性引用 输入。")

    def _execute_get_attribute(self, parameters, input_values):
        if input_values.get("attrs"):
            try:
                value = attributes.get_attribute_refs(input_values.get("attrs"))
            except MayaApiError as error:
                raise WorkflowExecutionError(str(error))
            return {"value": value}

        raise WorkflowExecutionError("获取属性需要连接 属性引用 输入。")

    def _execute_make_attribute_refs(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        attribute = parameters.get("attribute", "")
        try:
            attr_refs = attributes.make_attribute_refs(nodes, attribute)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"attrs": attr_refs}

    def _execute_inspect_attributes(self, input_values):
        attr_refs = input_values.get("attrs")
        try:
            packets = attributes.inspect_attributes(attr_refs)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        values = [packet.value for packet in packets]
        return {
            "value": values[0] if len(values) == 1 else values,
            "report": attributes.packets_report(packets),
        }

    def _execute_constraint(self, node_type, parameters, input_values):
        drivers = input_values.get("drivers") or []
        driven = input_values.get("driven") or []
        constraint_type = node_type.rsplit(".", 1)[-1]
        try:
            created_constraints = constraints.create_constraint(
                constraint_type,
                drivers,
                driven,
                maintain_offset=parameters.get("maintain_offset", True),
                weight=parameters.get("weight", 1.0),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {
            "constraints": created_constraints,
            "done": True,
        }

    def _execute_import_file(self, parameters, input_values):
        file_path = input_values.get("file_path")
        if not file_path:
            raise WorkflowExecutionError("Import File requires file_path input.")

        mode = parameters.get("mode", "import")
        namespace = parameters.get("namespace", "")
        preserve_references = bool(parameters.get("preserve_references", True))

        try:
            imported_nodes = io.import_file(
                file_path,
                mode=mode,
                namespace=namespace,
                preserve_references=preserve_references,
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        return {
            "imported_nodes": imported_nodes,
            "done": True,
        }

    def _execute_export_fbx(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        target_path = input_values.get("target_path")
        if not nodes:
            raise WorkflowExecutionError("Export FBX requires nodes input.")
        if not target_path:
            raise WorkflowExecutionError("Export FBX requires target_path input.")

        overwrite_existing = bool(parameters.get("overwrite_existing", False))
        bake_animation = bool(parameters.get("bake_animation", False))
        frame_start = float(parameters.get("frame_start", 1.0))
        frame_end = float(parameters.get("frame_end", 120.0))

        try:
            result_path = export.export_fbx(
                nodes,
                target_path,
                bake_animation=bake_animation,
                frame_start=frame_start,
                frame_end=frame_end,
                overwrite_existing=overwrite_existing,
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        return {"result": result_path}
