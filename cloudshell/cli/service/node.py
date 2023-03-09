from __future__ import annotations

from abc import ABC, abstractmethod

from typing_extensions import Self


class Node(ABC):
    def __init__(self):
        self.parent_node: Self | None = None
        self.child_nodes: list[Self] = []

    def add_child_node(self, node: Node) -> None:
        self.child_nodes.append(node)
        node.parent_node = self

    @abstractmethod
    def step_up(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def step_down(self, *args, **kwargs) -> None:
        pass


class NodeOperations:
    @staticmethod
    def path_to_the_root(node: Node) -> list[Node]:
        path = [node]
        while node.parent_node:
            node = node.parent_node
            path.append(node)
        return path

    @staticmethod
    def calculate_route_steps(source_node: Node, dest_node: Node) -> list[callable]:
        """Calculate route between two nodes.

        :return: List of functions, needed to call to get from source to dest node
        """
        source_node_root_path = NodeOperations.path_to_the_root(source_node)
        dest_node_root_path = NodeOperations.path_to_the_root(dest_node)

        def down_steps(down_route: list[Node]) -> list[callable]:
            steps = []
            for node in down_route:
                steps.append(node.step_down)
            return steps

        def up_steps(up_route: list[Node]) -> list[callable]:
            steps = []
            for node in up_route:
                steps.append(node.step_up)
            return steps

        index = 0
        while True:
            if source_node_root_path[index] in dest_node_root_path:
                dest_index = len(source_node_root_path) - index
                return down_steps(source_node_root_path[:index]) + up_steps(
                    dest_node_root_path[::-1][dest_index:]
                )
            else:
                index += 1
