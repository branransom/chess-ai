import time
import uuid
import sys
from treelib import Tree

def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0
    helper.__name__= func.__name__

    return helper

def timer(func):
    def helper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        toc = time.perf_counter()
        print(f"{func.__name__} took {toc - tic:0.4f} seconds to execute")
        return result
    helper.__name__= func.__name__

    return helper

def generate_move_tree(func):
    def helper(*args, **kwargs):
        node_id = uuid.uuid4()
        board = args[1]
        alpha = args[3]
        beta = args[4]
        try:
            move = board.peek()
        except:
            move = 'root'

        # caller function (parent)
        parent_kwargs = sys._getframe(0).f_locals["kwargs"]
        parent_id = parent_kwargs.get("node_id", "root")
        tree = parent_kwargs.get("tree", None)
        if not tree:
            tree = Tree()
            tree.create_node("root", "root")

        tree.create_node(f"{move} a={alpha} b={beta} white={board.turn}", node_id, parent=parent_id)

        kwargs.update({ "node_id": node_id, "tree": tree })
        result = func(*args, **kwargs)

        node = tree.get_node(node_id)
        node.tag = f"{node.tag} {result}"

        return result

    helper.__name__= func.__name__

    return helper
