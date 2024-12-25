import math
import random


class HamiltonianCycle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.spanning_tree: list[HEdge] = []
        self.spanning_tree_nodes: list[HNode] = []
        self.cycle: list[HNode] = []

        self.create_cycle()

        print("Hamiltonian Cycle created", len(self.cycle))

    def create_cycle(self):
        self.create_spanning_tree()

        cycle_nodes: list[HNode] = []
        for i in range(0, self.width):
            for j in range(0, self.height):
                cycle_nodes.append(HNode(i, j))
        for n in cycle_nodes:
            n.set_edges(cycle_nodes)
        for i in range(0, len(self.spanning_tree_nodes)):
            current_spanning_tree_node = self.spanning_tree_nodes[i]
            for other in current_spanning_tree_node.spanning_tree_adjacent_nodes:
                def connect_nodes(x1, y1, x2, y2):
                    if y1 + self.height * x1 >= len(cycle_nodes) or y2 + self.height * x2 >= len(cycle_nodes):
                        return
                    a = cycle_nodes[y1 + self.height * x1]
                    b = cycle_nodes[y2 + self.height * x2]
                    a.spanning_tree_adjacent_nodes.append(b)
                    b.spanning_tree_adjacent_nodes.append(a)

                direction = current_spanning_tree_node.get_direction_to(other)
                x = current_spanning_tree_node.x * 2
                y = current_spanning_tree_node.y * 2
                if direction['x'] == 1:
                    connect_nodes(x + 1, y, x + 2, y)
                    connect_nodes(x + 1, y + 1, x + 2, y + 1)
                elif direction['y'] == 1:
                    connect_nodes(x, y + 1, x, y + 2)
                    connect_nodes(x + 1, y + 1, x + 1, y + 2)

        degree_1_nodes = [n for n in cycle_nodes if len(n.spanning_tree_adjacent_nodes) == 1]
        new_edges: list[HEdge] = []
        for n in degree_1_nodes:
            d = n.spanning_tree_adjacent_nodes[0].get_direction_to(n)
            d['x'] += n.x
            d['y'] += n.y
            new_edge = HEdge(cycle_nodes[d['y'] + self.height * d['x']], n)
            unique_edge = True
            for e in new_edges:
                if e.is_equal_to(new_edge):
                    unique_edge = False
                    break
            if unique_edge:
                new_edges.append(new_edge)

        for e in new_edges:
            e.connect_nodes()

        degree_1_nodes = [n for n in cycle_nodes if len(n.spanning_tree_adjacent_nodes) == 1]
        new_edges: list[HEdge] = []
        for n in degree_1_nodes:
            for m in degree_1_nodes:
                if dist(n.x, n.y, m.x, m.y) == 1:
                    if n.x // 2 == m.x // 2 and n.y // 2 == m.y // 2:
                        new_edge = HEdge(m, n)
                        unique_edge = True
                        for e in new_edges:
                            if e.is_equal_to(new_edge):
                                unique_edge = False
                                break
                        if unique_edge:
                            new_edges.append(new_edge)
                        break

        for e in new_edges:
            e.connect_nodes()

        cycle: list[HNode] = [random.choice(cycle_nodes)]

        previous = cycle[0]
        node = cycle[0].spanning_tree_adjacent_nodes[0]

        while node != cycle[0]:
            next_node = node.spanning_tree_adjacent_nodes[0]
            if next_node == previous:
                next_node = node.spanning_tree_adjacent_nodes[1]
            cycle.append(node)
            previous = node
            node = next_node

        self.cycle = cycle
        for i in range(0, len(self.cycle)):
            self.cycle[i].cycle_no = i

    def create_spanning_tree(self):
        st_nodes: list[HNode] = []
        for i in range(0, self.width // 2):
            for j in range(0, self.height // 2):
                st_nodes.append(HNode(i, j))

        for n in st_nodes:
            n.set_edges(st_nodes)

        spanning_tree: list[HEdge] = []
        random_node = st_nodes[random.randint(0, len(st_nodes) - 1)]
        spanning_tree.append(HEdge(random_node, random_node.edges[0]))
        nodes_in_spanning_tree = [random_node, random_node.edges[0]]

        while len(nodes_in_spanning_tree) < len(st_nodes):
            random_node = random.choice(nodes_in_spanning_tree)
            edges = [n for n in random_node.edges if n not in nodes_in_spanning_tree]
            if len(edges) != 0:
                random_edge = random.choice(edges)
                nodes_in_spanning_tree.append(random_edge)
                spanning_tree.append(HEdge(random_node, random_edge))

        for n in st_nodes:
            n.set_spanning_tree_edges(spanning_tree)

        self.spanning_tree = spanning_tree
        self.spanning_tree_nodes = st_nodes

    def get_node_no(self, x, y) -> int:
        for i in range(0, len(self.cycle)):
            if self.cycle[i].x == x and self.cycle[i].y == y:
                return i
        return -1

    def get_possible_positions_from(self, x, y):
        current_node = self.cycle[self.get_node_no(x, y)]
        node_nos = []
        for n in current_node.edges:
            node_nos.append(self.get_node_no(n.x, n.y))
        return node_nos


class HNode:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.spanning_tree_adjacent_nodes: list[HNode] = []
        self.cycle_no = -1
        self.already_visited = False
        self.shortest_distance_to_this_point = 0
        self.edges: list[HNode] = []

    def set_edges(self, all_nodes: list["HNode"]):
        self.edges = [n for n in all_nodes if (dist(n.x, n.y, self.x, self.y) == 1)]

    def set_spanning_tree_edges(self, spanning_tree: list["HEdge"]):
        for e in spanning_tree:
            if e.contains(self):
                self.spanning_tree_adjacent_nodes.append(e.get_other_node(self))

    def get_direction_to(self, other):
        return {'x': other.x - self.x, 'y': other.y - self.y}

    def reset_for_a_star(self):
        self.already_visited = False
        self.shortest_distance_to_this_point = 0

    def __repr__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'


class HEdge:
    def __init__(self, node1: HNode, node2: HNode):
        self.node1 = node1
        self.node2 = node2

    def is_equal_to(self, other_edge: "HEdge") -> bool:
        return (self.node1 == other_edge.node1 and self.node2 == other_edge.node2) or (
                self.node1 == other_edge.node2 and self.node2 == other_edge.node1)

    def contains(self, n: HNode) -> bool:
        return n == self.node1 or n == self.node2

    def get_other_node(self, n: HNode) -> HNode:
        if n == self.node1:
            return self.node2
        else:
            return self.node1

    def connect_nodes(self) -> None:
        self.node1.spanning_tree_adjacent_nodes.append(self.node2)
        self.node2.spanning_tree_adjacent_nodes.append(self.node1)

    def __repr__(self):
        return '(' + str(self.node1.x) + ', ' + str(self.node1.y) + ') (' + str(self.node2.x) + ', ' + str(self.node2.y) + ')'


class HPath:
    def __init__(self, starting_node, finishing_node):
        self.path_length = 0
        self.nodes_in_path = [starting_node]
        self.finish_node = finishing_node

        self.distance_to_apple = 0
        self.set_distance_to_apple()
        self.path_counter = 0

    def set_distance_to_apple(self):
        self.distance_to_apple = dist(self.finish_node.x, self.finish_node.y, self.get_last_node().x, self.get_last_node().y)

    def add_to_tail(self, node):
        self.nodes_in_path.append(node)
        self.path_length += 1
        self.set_distance_to_apple()

    def get_last_node(self):
        return self.nodes_in_path[-1]

    def get_snake_tail_position_after_following_path(self, snake):
        if self.path_length - snake.add_count < len(snake.tail_blocks):
            return snake.tail_blocks[max(0, self.path_length - snake.add_count)]
        tail_moved = self.path_length - snake.add_count
        return self.nodes_in_path[tail_moved - len(snake.tail_blocks)]

    def get_next_move(self):
        x = self.nodes_in_path[self.path_counter + 1].x - self.nodes_in_path[self.path_counter].x
        y = self.nodes_in_path[self.path_counter + 1].y - self.nodes_in_path[self.path_counter].y
        self.path_counter += 1
        return {'x': x, 'y': y}

    def clone(self) -> "HPath":
        clone = HPath(self.nodes_in_path[0], self.finish_node)
        clone.nodes_in_path = self.nodes_in_path.copy()
        clone.path_length = self.path_length
        clone.distance_to_apple = self.distance_to_apple

        return clone

    def __str__(self):
        s = ''
        for n in self.nodes_in_path:
            s += '(' + str(n.x) + ', ' + str(n.y) + ') '
        s += 'Distance to apple: ' + str(self.distance_to_apple)
        s += ' Path length: ' + str(self.path_length)
        s += ' Path counter: ' + str(self.path_counter)
        return s


def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


if __name__ == '__main__':
    hc = HamiltonianCycle(40, 20)
    print(hc.spanning_tree_nodes)
