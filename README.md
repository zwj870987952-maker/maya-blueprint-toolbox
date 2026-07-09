# Maya Blueprint Toolbox

Maya Blueprint Toolbox is the starting point for a ComfyUI-style node canvas inside Maya.

The current milestone focuses on the canvas foundation and the first node rules:

- PySide6-first, PySide2 fallback Qt compatibility.
- A Maya-parented toolbox window with a graphics canvas.
- Built-in node specs for constants, data acquisition, selection, import, and FBX export nodes.
- First executable node batch includes selection, naming, grouping, deleting, attributes, and common constraints.
- Minimal runtime type system for values, node references, attribute references, and execution ports.
- Movable nodes with typed input and output ports.
- Drag connections from output ports to matching input ports.
- Delete selected nodes or connections with Delete/Backspace.
- Pan the canvas with middle mouse drag or Space + left mouse drag.
- Double-click the canvas to search and add a node at the cursor position.
- Right-click the canvas to add nodes from a category menu.
- Nodes display run status in the header and border color: IDLE, RUN, OK, ERR, SKIP.
- A property panel for selected node parameters.
- Workflow save/load as JSON.
- Basic workflow validation, execution, and serialization through `Print Workflow`.
- Maya operations are routed through unified API wrappers under `maya_blueprint_toolbox/maya_api`.
- The Run button executes the selected node workflow when nodes are selected, otherwise it executes all nodes.
- Node header color follows functional node type. Port and connection color follow data type.

## Node Rule Docs

- General node rules: `docs/node_type_rules.md`
- Type 1, constants: `docs/node_types/01_constant.md`
- Type 2, data acquisition: `docs/node_types/02_data_get.md`
- Type 3, data transform: `docs/node_types/03_data_transform.md`
- Type 4, animation workflow planning: `docs/node_types/04_animation_workflow_nodes.md`
- Tool breakdown, copy/paste world transform: `docs/tool_breakdowns/world_transform_copy_paste_v4.md`
- Data transform test workflow: `examples/workflows/data_transform_test.json`
- Copy frame JSON test workflow: `examples/workflows/copy_frame_json_test.json`

New node types should be designed from Maya operation habits first, then implemented with accurate DAG / DG / attribute-reference logic underneath.

## Run In Maya

Add this repository to Maya's Python path, then run:

```python
import maya_blueprint_toolbox
maya_blueprint_toolbox.show()
```

## Current Canvas Rules

- Double-click empty canvas space to open the node search dialog.
- Right-click empty canvas space to open a category menu. Categories come from each node spec's `category`, split by `/`.
- Connections start from output ports.
- Connections end on input ports.
- A connection is valid when port types are compatible. Legacy types like `text`, `path`, and `maya_node_list` are normalized to canonical types like `STRING`, `PATH`, and `NODE_LIST`.
- Nodes cannot connect to themselves.
- Node parameters are edited in the right-side property panel.
- Required parameters and required input connections are checked by `Validate`.
- `Run` executes supported nodes including constants, data acquisition, selection, node operations, attribute operations, constraints, import, and FBX export.
- `Node Names` accepts comma, semicolon, or newline separated Maya node names and outputs a node list.
- Data acquisition nodes include `当前选择`, `节点名称`, `按 Maya 类型获取节点`, `获取 SkinCluster`, `获取 BlendShape`, `获取变形器`, `获取材质`, `获取约束`, `获取属性`, and `检查属性`.
- `节点名称` can record the current Maya selection into an editable list, and selected entries can be removed freely.
- Data transform nodes include paired node-list and attribute-list merge, unique, name filter, item pick, count, name sort, reverse, and hierarchy sort nodes.
- Animation workflow nodes include `当前帧`, `范围帧`, `变换通道`, `获取通道栏选择`, and `复制帧`.
- `复制帧` captures world transform frame data from `复制对象`. If its `帧数据` output is not connected, it writes a JSON file; if connected to `设置属性.值`, the frame data can be pasted onto connected attribute references and keyed.
- Copy-frame paste uses strict list-order 1-to-1 mapping. Insert node-list sorting nodes on the source side or target side to change which objects correspond.
- `打印结果` can connect to any output type, prints the value to Maya's Script Editor, and shows the latest value in the right-side property panel.
- New executable nodes include Select Nodes, Rename Nodes, Group Nodes, Delete Nodes, Set/Get Attribute, and Parent/Point/Orient/Scale Constraint.
- Attribute reference nodes let you build safer Maya attribute workflows:
  - `创建属性引用` records reusable attribute names. Channel Box capture stores only the selected attribute name, not the selected object's name.
  - Attribute entries can be added repeatedly, saved with the workflow, and deleted from the property panel.
  - `获取属性` reads `ATTR_LIST` and outputs the current value.
  - `检查属性` reads `ATTR_LIST` and outputs the current value plus a readable report.
  - `设置属性` writes `VALUE` into `ATTR_LIST`.
- `Run` updates each node's visual status as it executes.
- If one or more nodes are selected, `Run` executes those nodes plus their upstream dependencies only.
- The numeric field beside `Run` controls how many times to execute, defaulting to 1.
- FBX export restores the previous Maya selection after exporting.

## Attribute Reference Test

To test the new typed attribute flow:

1. Select or name one Maya transform node.
2. Add `当前选择` or `节点名称`.
3. Add `创建属性引用`, set `属性` to `translateX`, and connect `节点 -> 节点`.
4. Add `数字`, set `值` to a test number.
5. Add `设置属性`, connect `属性引用 -> 属性引用` and `值 -> 值`.
6. Select the final `设置属性` node and press `运行`.

For inspection, connect `创建属性引用.属性引用` into `检查属性.属性引用`, then run `检查属性`. The node returns current value and capability data such as keyable, writable, locked, connected, and Maya attribute type.

## Copy Frame Test

To test JSON output:

1. Select one or more transform controls in Maya.
2. Add `当前选择`, `当前帧`, `变换通道`, and `复制帧`.
3. Connect `当前选择.节点 -> 复制帧.复制对象`, `当前帧.帧 -> 复制帧.帧`, and `变换通道.通道 -> 复制帧.通道`.
4. Leave `复制帧.帧数据` unconnected and run `复制帧`; it writes a JSON file. Set `JSON 路径` on the node to choose the file location.

To test direct paste through attributes:

1. Build the same source side as above.
2. Add a target `节点名称` or `当前选择`, then add `创建属性引用` with attributes such as `translateX, translateY, translateZ, rotateX, rotateY, rotateZ`.
3. Add `设置属性`.
4. Connect `复制帧.帧数据 -> 设置属性.值` and `创建属性引用.属性引用 -> 设置属性.属性引用`.
5. Run `设置属性`; it applies copied frame values to matching target attributes and sets keys on those frames.

## Next Steps

- Add more executable Maya operation nodes.
- If native Qt canvas interaction is not enough, bundle approved third-party UI libraries under a local `vendor` package so other Maya installs can load them through the toolbox path.
