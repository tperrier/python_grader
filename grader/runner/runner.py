#!/usr/bin/python
import ast #abstract syntax tree
import abc #abstract base class
import traceback,sys

import grader.utils as utils

class GraderException(Exception):
    pass

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


class BaseRunner(object):
    
    # Make BaseGradeRunner an Abstract Base Class
    __metaclass__ = abc.ABCMeta 
    
    # All files in grading_scripts that must be copied into the grading_sandbox
    required_for_grading = frozenset()

    # All files that students submit - these are copied from submissions/ta_name
    solution_files = frozenset()
    
    # Main file to run and grade 
    @abc.abstractproperty
    def main_file(self):
	return 'FILE NAME OF DEFAULT FILE TO EXECUTE'
	
    # List of functions to remove from abstract syntax tree of parsed code
    remove_func_list = frozenset()

    # All files that student code should generate.
    generated_files = frozenset()

    #All files to export to the student's graded directory
    export_files = frozenset()
    
    #AST NodeTransformer Class
    ParserClass = NodeRemover
    
    
    def __init__(self,show_feedback=False):
	self.show_feedback = show_feedback
	
    def run_hw(self):
	return self.execute_file()
	
    def execute_file(self,file_name=None):
	if file_name is None:
	    file_name = self.main_file
	
	#Parse and execute file
	parsed = self.parse_file(file_name)
	return self.exec_parsed(parsed)
	
	
    def parse_file(self,file_name):
	try:
	    tree = self.ParserClass(file_name,self.remove_func_list).remove()
	    parsed = compile(tree,filename=file_name,mode='exec')
	except Exception as e:
	    self._exception_handler(e)
	return parsed
	    
    def exec_parsed(self,parsed):
	#Make name space for student code to execute in
	env = {}
	#Make output logger
	hw_output = utils.output.PrintLogger(end='')
	
	#Change standard out to hw_output
	sys.stdout = hw_output

	try:
	    exec(parsed,env) #exectute students code.
	except Exception as e:
	    self._exception_handler(e)
	    
	#Reset standard out
	sys.stdout = sys.__stdout__
	
	return env,hw_output
	    
    def _exception_handler(self,e):
	err_str = "EXPECTION EXECUTING CODE: {}".format(e)
	utils.output.PROGRESS_LOG.error(err_str)
	with open('output.txt','w') as fp:
	    traceback.print_exc(file=fp)
	sys.stdout = sys.__stdout__
	raise GraderException(str(e))
