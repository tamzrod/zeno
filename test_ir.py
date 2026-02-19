from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor

store = IRStore()
root_id = store.create_root(NodeType.OBJECT)

processor = OperationProcessor(store)

op = Operation.create(
    operation_type="add_node",
    target_node_id=None,
    payload={
        "parent_id": root_id,
        "node_type": NodeType.SCALAR,
        "key": "name",
    },
)

processor.apply(op)

root = store.get_node(root_id)
print("Children count:", len(root.children))
