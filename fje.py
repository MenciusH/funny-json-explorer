from abc import ABC, abstractmethod
import json
import argparse

# 抽象工厂
class AbstractFactory(ABC):

    @abstractmethod
    def createJsonTree(self):
        pass
# 抽象工厂
class AbstractRectangleFactory(AbstractFactory):

    def __init__(self, file_path):
        self.tree_builder = None
        self.icon_family = None
        self.size = 60
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def createJsonTree(self):
        self.tree_builder = RecJsonTreeBuilder(self.icon_family, self.size)
        self.tree_builder.build_root()
        self.tree_builder.build_children(self.tree_builder.get_root(), self.data)
        self.tree_builder.setEvetyNodeTotalNum(self.tree_builder.get_root())
        return self.tree_builder.get_root()
# 具体工厂
class RecIcon1Factory(AbstractRectangleFactory):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.icon_family = {'container': '♢', 'leaf': '♤'}
# 具体工厂
class RecIcon2Factory(AbstractRectangleFactory):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.icon_family = {'container': '♡', 'leaf': '♧'}

# 生成器模式
class RecJsonTreeBuilder():

    def __init__(self, icon_family, size):
        self.root = None
        self.icon = icon_family
        self.count = 0
        self.size = size

    def build_root(self):
        self.root = RecContainer(None, {"container":None}, self.size)
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
            node = RecContainer(node_data[0], self.icon, self.size)
            node.setLevel(level)
            node.setNum(self.count)
            return node
        else:
            node = RecLeaf(node_data[0], self.icon, self.size)
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

# 抽象工厂模式
class AbstractTreeFactory(AbstractFactory):

    def __init__(self, file_path):
        self.tree_builder = None
        self.icon_family = None
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def createJsonTree(self):
        self.tree_builder = TreeJsonTreeBuilder(self.icon_family)
        self.tree_builder.build_root()
        self.tree_builder.build_children(self.tree_builder.get_root(), self.data)
        self.tree_builder.setEvetyNodeTotalNum(self.tree_builder.get_root())
        return self.tree_builder.get_root()

# 生成器模式
class TreeJsonTreeBuilder():

    def __init__(self, icon_family):
        self.root = None
        self.icon = icon_family
        self.count = 0

    def build_root(self):
        self.root = TreeContainer(None, {"container":None})
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
            node = TreeContainer(node_data[0], self.icon)
            node.setLevel(level)
            node.setNum(self.count)
            return node
        else:
            node = TreeLeaf(node_data[0], self.icon)
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
# 具体工厂
class TreeIcon1Factory(AbstractTreeFactory):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.icon_family = {'container': '♢', 'leaf': '♤'}
# 具体工厂
class TreeIcon2Factory(AbstractTreeFactory):

    def __init__(self, file_path):
        super().__init__(file_path)
        self.icon_family = {'container': '♡', 'leaf': '♧'}
# 抽象产品
class Node(ABC):

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.level = 0
        self.num = 0
        self.total_num = 0

    @abstractmethod
    def isContainer(self):
        pass

    def getName(self):
        return self.name
    
    def getIcon(self):
        return self.icon
    
    def getLevel(self):
        return self.level
    
    def setLevel(self, level):
        self.level = level
    
    def setNum(self, num): 
        self.num = num

    def setTotalNum(self, total_num):
        self.total_num = total_num
        #print("total_num:", self.total_num)

    @abstractmethod
    def draw(self):
        pass
# 具体产品
class RecContainer(Node):

    def __init__(self, name, icon, size):
        super().__init__(name, icon)
        self.icon = icon['container']
        self.children = []
        self.size = size

    def add_child(self, child):
        self.children.append(child)

    def isContainer(self):
        return True
    
    def draw(self):
        line = ''
        if self.num == 1:
            line = "┌─ " + str(self.icon) + str(self.name) + " "
        else:
            line = "├─ " + str(self.icon) + str(self.name) + " "
        # 向前补全
        for i in range(self.level - 1):
            line = "│  " + line
        # 向后补全
        for i in range(self.size - len(line) - 1):
            line += "─"
        if self.num == 1:
            line += "┐"
        else:
            line += "┤"
        if self.num > 0:
            print(line)
        for child in self.children:
            child.draw()
# 具体产品    
class RecLeaf(Node):

    def __init__(self, name, icon, size):
        super().__init__(name, icon)
        self.icon = icon['leaf']
        self.size = size

    def isContainer(self):
        return False

    def setName(self, name):
        self.name = self.name + ':' + str(name)

    def draw(self):
        if self.num == self.total_num:
            line = "└─ " + str(self.icon) + str(self.name) + " "
            # 向前补全
            for i in range(self.level - 1):
                line = "└──" + line
        else:
            line = "├─ " + str(self.icon) + str(self.name) + " "
            # 向前补全
            for i in range(self.level - 1):
                line = "│  " + line
        # 向后补全
        for i in range(self.size - len(line) - 1):
            line += "─"
        if self.num == self.total_num:
            line += "┘"
        else:
            line += "┤"
        print(line)
# 具体产品
class TreeContainer(Node):

    def __init__(self, name, icon):
        super().__init__(name, icon)
        self.icon = icon['container']
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def isContainer(self):
        return True
    
    def draw(self, isBottom=False, prefix=""):
        if isBottom:
            line = "└─ " + str(self.icon) + str(self.name) + " "
        else:
            line = "├─ " + str(self.icon) + str(self.name) + " "
        line = prefix + line
        if self.level > 0:
            print(line)
            if isBottom:
                prefix = prefix + "   "
            else:
                prefix = prefix + "│  "

        for i in range(len(self.children)):
            if(i == len(self.children) - 1):
                self.children[i].draw(True, prefix)
            else:
                self.children[i].draw(False, prefix)
# 具体产品    
class TreeLeaf(Node):

    def __init__(self, name, icon):
        super().__init__(name, icon)
        self.icon = icon['leaf']

    def isContainer(self):
        return False

    def setName(self, name):
        self.name = self.name + ':' + str(name)

    def draw(self, isBottom=False, prefix=""):
        if isBottom:
            line = "└─ " + str(self.icon) + str(self.name) + " "
        else:
            line = "├─ " + str(self.icon) + str(self.name) + " "
        line = prefix + line
        if self.level > 0:
            print(line)
# 客户端代码
class FunnyJsonExplorer():

    def __init__(self, file, AbstractFactory : AbstractFactory):
        self.root = None
        self.file_path = file
        self._load(AbstractFactory)
    
    def _load(self, AbstractFactory : AbstractFactory):
        self.root = AbstractFactory(self.file_path).createJsonTree()

    def show(self):
        self.root.draw()

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
        explorer = FunnyJsonExplorer(args.file, TreeIcon1Factory)
    elif args.style == 'tree' and args.icon_family == '2':
        explorer = FunnyJsonExplorer(args.file, TreeIcon2Factory)
    elif args.style == 'rec' and args.icon_family == '1':
        explorer = FunnyJsonExplorer(args.file, RecIcon1Factory)
    elif args.style == 'rec' and args.icon_family == '2':
        explorer = FunnyJsonExplorer(args.file, RecIcon2Factory)
    else:
        print('输入的风格或图标家族不正确')
    explorer.show()