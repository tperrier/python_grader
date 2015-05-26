#!/usr/bin/python
import ast #abstract syntax tree
import abc #abstract base class
import traceback,sys

import grader.utils as utils
import checker

class GraderException(Exception):
    pass
    
class GraderSyntaxError(GraderException):
    pass

class GraderRunTimeError(GraderException):
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
    required_for_grading = set()

    # All files that students submit - these are copied from submissions/ta_name
    solution_files = set()
    
    # Main file to run and grade 
    @abc.abstractproperty
    def main_file(self):
	return 'FILE NAME OF DEFAULT FILE TO EXECUTE'
	
    # List of functions calls to remove from abstract syntax tree of parsed code
    remove_func_list = set()

    # All files that student code should generate.
    generated_files = set()

    #All files to export to the student's graded directory
    export_files = set()
    
    #AST NodeTransformer Class
    ParserClass = NodeRemover
    
    @abc.abstractmethod
    def get_problems(self):
	return 'A list of all problems to check'
    
    
    def __init__(self,show_feedback=False):
	self.show_feedback = show_feedback
	
    def run_hw(self):
	'''Runs self.main_file and returns the environment and output '''
	env,output = self.execute_file()
	return env,output
	
    def check_hw(self,env,output,show_feedback=False):
	'''Checks all hw problems'''
	feedback = utils.output.PrintLogger(enable=show_feedback or self.show_feedback)
	sys.stdout = feedback
	
	try:
	    total = checker.check_problems(self.get_problems(),env)
	except Exception as e:
	    self._exception_handler(e)
	finally:
	    #Reset standard out
	    sys.stdout = sys.__stdout__
	
	return feedback,total
	
	
    def execute_file(self,file_name=None):
	if file_name is None:
	    file_name = self.main_file
	
	#Parse file into abstract syntax tree
	try:
	    tree = self.ParserClass(file_name,self.remove_func_list).remove()
	    parsed = compile(tree,filename=file_name,mode='exec')
	except Exception as e:
	    self._exception_handler(e)
	    
	#Execute file into black environment
	#Make name space for student code to execute in
	env = {}
	#Make output logger and set as stdout
	output = utils.output.PrintLogger(end='')
	sys.stdout = output

	try:
	    exec(parsed,env) #exectute students code.
	except Exception as e:
	    self._exception_handler(e)
	finally:
	    #Reset standard out
	    sys.stdout = sys.__stdout__
	    
	return env,output
	    
    def _exception_handler(self,e):
	#Print error message
	err_str = "EXPECTION EXECUTING CODE: {}".format(e)
	utils.output.PROGRESS_LOG.error(err_str)
	#Get string traceback
	error_output = StringIO.String()
	traceback.print_exc(file=error_output)
	raise GraderException(error_output.getvalue())
