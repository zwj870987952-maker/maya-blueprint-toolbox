# Maya Blueprint Toolbox

Maya Blueprint Toolbox is the starting point for a ComfyUI-style node canvas inside Maya.

The first milestone focuses on the canvas foundation:

- PySide6-first, PySide2 fallback Qt compatibility.
- A Maya-parented toolbox window with a graphics canvas.
- Built-in node specs for constants, selection, import, and FBX export nodes.
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
- `Run` executes supported nodes including constants, selection, node operations, attribute operations, constraints, import, and FBX export.
- `Node Names` accepts comma, semicolon, or newline separated Maya node names and outputs a node list.
- New executable nodes include Select Nodes, Rename Nodes, Group Nodes, Delete Nodes, Set/Get Attribute, and Parent/Point/Orient/Scale Constraint.
- Attribute reference nodes let you build safer Maya attribute workflows:
  - `创建属性引用` converts a node list plus its `属性` parameter into `ATTR_LIST`.
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

## Next Steps

- Add more executable Maya operation nodes.
- If native Qt canvas interaction is not enough, bundle approved third-party UI libraries under a local `vendor` package so other Maya installs can load them through the toolbox path.
