#!/usr/bin/python
import ast


class NodeRemover(ast.NodeTransformer):
    
    def __init__(self,file_name,func_list):
        super(NodeRemover,self).__init__()
        self.file = open(file_name,'r')
        self.func_list = func_list
    
    def remove(self):
        tree = ast.parse(self.file.read(),mode='exec')
        return ast.fix_missing_locations(self.visit(tree))
    
    def visit_Assert(self,node):
        return None
        
    def visit_Call(self,node):  
        try:
            name = node.func.id if isinstance(node.func,ast.Name) else node.func.attr
            if name in self.func_list:
                print "Removed: {}".format(name)
                return ast.Str('')
            else:
                return node
        except AttributeError as e:
            return node
