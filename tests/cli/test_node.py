from unittest import TestCase

from cloudshell.cli.service.node import Node, NodeOperations

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class NodeImplementation(Node):
    def step_down(self, *args, **kwargs):
        pass

    def step_up(self, *args, **kwargs):
        pass


class TestNode(TestCase):
    def setUp(self):
        self._node = NodeImplementation()

    def test_attribute_parent_node_exist(self):
        self.assertTrue(hasattr(self._node, "parent_node"))

    def test_attribute_child_nodes_exist(self):
        self.assertTrue(hasattr(self._node, "child_nodes"))

    def test_add_child_node_append_child(self):
        child_node = NodeImplementation()
        self._node.add_child_node(child_node)
        self.assertTrue(child_node in self._node.child_nodes)

    def test_add_child_node_set_parent(self):
        child_node = NodeImplementation
        self._node.add_child_node(child_node)
        self.assertTrue(child_node.parent_node == self._node)


class TestNodeOperations(TestCase):
    def setUp(self):
        pass

    def test_path_to_the_root_single_node(self):
        node = NodeImplementation()
        self.assertTrue(len(NodeOperations.path_to_the_root(node)) == 1)

    def test_path_to_the_root_multiple_node(self):
        node1 = NodeImplementation()
        node2 = NodeImplementation()
        node3 = NodeImplementation()
        node1.add_child_node(node2)
        node2.add_child_node(node3)
        self.assertTrue(len(NodeOperations.path_to_the_root(node3)) == 3)

    @patch("cloudshell.cli.service.node.NodeOperations.path_to_the_root")
    def test_calculate_route_steps_source_node_root_path_call(self, path_to_the_root):
        source_node = Mock()
        dest_node = Mock()
        path_to_the_root.side_effect = [
            [source_node, dest_node],
            [dest_node, source_node],
        ]
        NodeOperations.calculate_route_steps(source_node, dest_node)
        path_to_the_root.assert_any_call(source_node)
        path_to_the_root.assert_any_call(dest_node)
        self.assertEqual(2, path_to_the_root.call_count)

    @patch("cloudshell.cli.service.node.NodeOperations.path_to_the_root")
    def test_calculate_route_steps_dest_node_root_path_call(self, path_to_the_root):
        source_node = Mock()
        dest_node = Mock()
        path_to_the_root.side_effect = [
            [source_node, dest_node],
            [dest_node, source_node],
        ]
        NodeOperations.calculate_route_steps(source_node, dest_node)
        path_to_the_root.assert_any_call(source_node)
        path_to_the_root.assert_any_call(dest_node)
        self.assertEqual(2, path_to_the_root.call_count)
