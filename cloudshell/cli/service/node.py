from abc import ABCMeta, abstractmethod


class Node(object, metaclass=ABCMeta):
    """
    Node
    """

    def __init__(self):
        self.parent_node = None
        self.child_nodes = []

    def add_child_node(self, node):
        """
        Connect child node
        :param node:
        :type node: Node
        :return:
        """
        self.child_nodes.append(node)
        node.parent_node = self

    @abstractmethod
    def step_up(self, *args, **kwargs):
        pass

    @abstractmethod
    def step_down(self, *args, **kwargs):
        pass


class NodeOperations(object):
    @staticmethod
    def path_to_the_root(node):
        """
        Calculate path to the root node
        :param node:
        :type node: Node
        :return:
        """
        path = [node]
        while node.parent_node:
            node = node.parent_node
            path.append(node)
        return path

    @staticmethod
    def calculate_route_steps(source_node, dest_node):
        """
        Calculate route between two nodes, 
        :param source_node:
        :type source_node: Node
        :param dest_node:
        :type dest_node: Node
        :return: List of functions, needed to call to get from source to dest node
        :rtype: list
        """
        source_node_root_path = NodeOperations.path_to_the_root(source_node)
        dest_node_root_path = NodeOperations.path_to_the_root(dest_node)

        def down_steps(down_route):
            steps = []
            for node in down_route:
                steps.append(node.step_down)
            return steps

        def up_steps(up_route):
            steps = []
            for node in up_route:
                steps.append(node.step_up)
            return steps

        index = 0
        while True:
            if source_node_root_path[index] in dest_node_root_path:
                dest_index = len(source_node_root_path) - index
                return down_steps(source_node_root_path[:index]) + up_steps(dest_node_root_path[::-1][dest_index:])
            else:
                index += 1
