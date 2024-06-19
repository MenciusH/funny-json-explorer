from abc import ABC, abstractmethod
import json
import argparse
from collections.abc import Iterable, Iterator

# 迭代器模式：实现树的迭代器，遍历树，拿到节点，调用draw方法，实现树的绘制
# 策略模式：不同的绘制方法对应不同具体策略

class JsonTreeIterator(Iterator):

    def __init__(self, root):
        self.root = root
        self.stack = []
        self.stack.append(root)

    def __next__(self):
        if len(self.stack) == 0:
            raise StopIteration
        node = self.stack.pop()
        children = node.children
        children.reverse()
        prefix = ""
        if node.level > 0:
            if node.isBottom:
                prefix = node.prefix + "   "
            else:
                prefix = node.prefix + "│  "
        for i in range(len(children)):
            child = children[i]
            child.prefix = prefix
            if i == 0:
                child.set_isBottom(True)
            else:
                child.set_isBottom(False)
            self.stack.append(child)
        return node

class NodesCollection(Iterable):

    def __init__(self, file_path):
        self.tree_builder = None
        self.icon_family = None
        self.size = 60
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.root = self.createJsonTree()
        self.style = None
        self.icon_family = None

    def set_style(self, style):
        self.style = style

    def set_icon_family(self, icon_family):
        self.icon_family = icon_family

    def createJsonTree(self):
        self.tree_builder = JsonTreeBuilder(self.size)
        self.tree_builder.build_root()
        self.tree_builder.build_children(self.tree_builder.get_root(), self.data)
        self.tree_builder.setEvetyNodeTotalNum(self.tree_builder.get_root())
        return self.tree_builder.get_root()

    def __iter__(self) -> JsonTreeIterator:
        return JsonTreeIterator(self.root)

    def draw(self):
        if self.style is None:
            print("No style set!")
            return
        if self.icon_family is None:
            print("No icon family set!")
            return
        for node in self:
            self.style.draw_node(node, self.icon_family)

class DrawStyle(ABC):

    @abstractmethod
    def draw_node(self, node, icon_family):
        pass

class RectangleDrawStyle(DrawStyle):

    def draw_node(self, node, icon_family):
        if node.isContainer():
            icon = icon_family['container']
            line = ''
            if node.num == 1:
                line = "┌─ " + str(icon) + str(node.name) + " "
            else:
                line = "├─ " + str(icon) + str(node.name) + " "
            # 向前补全
            for i in range(node.level - 1):
                line = "│  " + line
            # 向后补全
            for i in range(node.size - len(line) - 1):
                line += "─"
            if node.num == 1:
                line += "┐"
            else:
                line += "┤"
            if node.num > 0:
                print(line)
        else:
            icon = icon_family['leaf']
            if node.num == node.total_num:
                line = "└─ " + str(icon) + str(node.name) + " "
                # 向前补全
                for i in range(node.level - 1):
                    line = "└──" + line
            else:
                line = "├─ " + str(icon) + str(node.name) + " "
                # 向前补全
                for i in range(node.level - 1):
                    line = "│  " + line
            # 向后补全
            for i in range(node.size - len(line) - 1):
                line += "─"
            if node.num == node.total_num:
                line += "┘"
            else:
                line += "┤"
            print(line)           
        return None

class TreeDrawStyle(DrawStyle):

    def draw_node(self, node, icon_family):
        if node.isContainer():
            icon = icon_family['container']
        else:
            icon = icon_family['leaf']
        if node.isBottom:
            line = "└─ " + str(icon) + str(node.name) + " "
        else:
            line = "├─ " + str(icon) + str(node.name) + " "
        line = node.prefix + line
        if node.level > 0:
            print(line)

class JsonTreeBuilder():

    def __init__(self, size):
        self.root = None
        self.count = 0
        self.size = size

    def build_root(self):
        self.root = Container(None, self.size)
        self.root.setLevel(0)
        self.root.setNum(0)

    def build_children(self, key_node, values):
        #print("values:",values)
        for child in values.items():
            self.count += 1
            child_node = self.build_node(child, key_node.getLevel() + 1)
            key_node.add_child(child_node)
            if child_node.isContainer():
                self.build_children(child_node, child[1])
            elif child[1] is not None:
                child_node.setName(child[1])

    def build_node(self, node_data, level):
        #print("node_data:", node_data)
        if isinstance(node_data[1], dict):
            node = Container(node_data[0], self.size)
            node.setLevel(level)
            node.setNum(self.count)
            return node
        else:
            node = Leaf(node_data[0], self.size)
            node.setLevel(level)
            node.setNum(self.count)
            return node
    
    def setEvetyNodeTotalNum(self, node):
        #print("self.count:", self.count)
        node.setTotalNum(self.count)
        if node.isContainer():
            for child in node.children:
                self.setEvetyNodeTotalNum(child)

    def get_root(self):
        return self.root

class Node(ABC):

    def __init__(self, name, size):
        self.name = name
        self.level = 0
        self.num = 0
        self.total_num = 0
        self.children = []
        self.size = size
        self.isBottom = False
        self.prefix = ""

    def set_isBottom(self, isBottom):
        self.isBottom = isBottom
    
    @abstractmethod
    def isContainer(self):
        pass

    def getName(self):
        return self.name
    
    def getLevel(self):
        return self.level
    
    def setLevel(self, level):
        self.level = level
    
    def setNum(self, num): 
        self.num = num

    def setTotalNum(self, total_num):
        self.total_num = total_num
        #print("total_num:", self.total_num)

class Container(Node):

    def add_child(self, child):
        self.children.append(child)

    def isContainer(self):
        return True

class Leaf(Node):

    def setName(self, name):
        self.name = self.name + ':' + str(name)

    def isContainer(self):
        return False

class FunnyJsonExplorer():

    def __init__(self, file, style: DrawStyle, icon_family):
        self.tree = None
        self.file_path = file
        self.style = style
        self.icon_family = icon_family
        self._load()
    
    def _load(self):
        self.tree = NodesCollection(self.file_path)
        self.tree.set_style(self.style)
        self.tree.set_icon_family(self.icon_family)
        self.tree.createJsonTree()

    def show(self):
        self.tree.draw()

if __name__ == '__main__':

    # 创建一个解析器对象
    parser = argparse.ArgumentParser(description='处理JSON文件的程序。')

    # 添加选项
    parser.add_argument('-f', '--file', type=str, help='输入的JSON文件路径')
    parser.add_argument('-s', '--style', type=str, help='指定的风格')
    parser.add_argument('-i', '--icon_family', type=str, help='图标家族')

    # 解析命令行参数
    args = parser.parse_args()

    # 实例化FunnyJsonExplorer对象
    if args.style == 'tree' and args.icon_family == '1':
        explorer = FunnyJsonExplorer(args.file, TreeDrawStyle(), {'container': '♢', 'leaf': '♤'})
    elif args.style == 'tree' and args.icon_family == '2':
        explorer = FunnyJsonExplorer(args.file, TreeDrawStyle(), {'container': '♡', 'leaf': '♧'})
    elif args.style == 'rec' and args.icon_family == '1':
        explorer = FunnyJsonExplorer(args.file, RectangleDrawStyle(), {'container': '♢', 'leaf': '♤'})
    elif args.style == 'rec' and args.icon_family == '2':
        explorer = FunnyJsonExplorer(args.file, RectangleDrawStyle(), {'container': '♡', 'leaf': '♧'})
    else:
        print('输入的风格或图标家族不正确')
    explorer.show()