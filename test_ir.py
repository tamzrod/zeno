from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor

store = IRStore()
root_id = store.create_root(NodeType.OBJECT)

processor = OperationProcessor(store)

# Add scalar node
op_add = Operation.create(
    operation_type="add_node",
    target_node_id=None,
    payload={
        "parent_id": root_id,
        "node_type": NodeType.SCALAR,
        "key": "name",
    },
)

processor.apply(op_add)

root = store.get_node(root_id)
child_id = root.children[0]

# Update scalar value
op_update = Operation.create(
    operation_type="update_scalar",
    target_node_id=None,
    payload={
        "node_id": child_id,
        "value": "Zeno",
    },
)

processor.apply(op_update)

child = store.get_node(child_id)

print("Children count:", len(root.children))
print("Child value:", child.value)

# Remove node
op_remove = Operation.create(
    operation_type="remove_node",
    target_node_id=None,
    payload={
        "node_id": child_id,
    },
)

processor.apply(op_remove)

print("Children after remove:", len(store.get_node(root_id).children))
