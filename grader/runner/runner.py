#!/usr/bin/python
import ast #abstract syntax tree
import abc #abstract base class
import traceback,sys,StringIO,copy,code

import grader.utils as utils
import checker, collections

class GraderException(Exception):
    
    ERROR_STR = "EXCEPTION RUNNING CODE: {err}"
    
    def __init__(self,e,**kwargs):
        #Print error message
        err_str = self.ERROR_STR.format(err=e)
        utils.output.PROGRESS_LOG.error(err_str)
        
        #Get traceback as string
        error_output = StringIO.StringIO()
        traceback.print_exc(file=error_output)
        
        #Get feedback and output if they exist
        self.feedback = kwargs.get('feedback',False)
        self.output = kwargs.get('output',False)
        
        #Set print args
        self.args = [error_output.getvalue()]
        
    
class GraderSyntaxError(GraderException):
    ERROR_STR = "EXCEPTION PARSING CODE: {err}"

class GraderRunTimeError(GraderException):
    pass
    
class GraderExecuteError(GraderException):
    ERROR_STR = "EXCEPTION EXECUTING CODE: {err}"

class NodeRemover(ast.NodeTransformer):
    '''
    NodeRemover Class is a subclass of ast.NodeTransformer. 
    It parses a python file and removes all assert statements.
    
    Documentation for ast can be found here:
    https://greentreesnakes.readthedocs.org/en/latest/index.html
    '''
    
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
    
    # Filename for python script to get output from
    # Defaults to env_file
    @property
    def main_file(self):
        return self.env_file

    # Filename for python script to get environment from
    @abc.abstractproperty
    def env_file(self):
        return 'FILENAME OF DEFAULT HOMEWORK ENVIRONMENT'
    
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
    
    def make_header(self,total):
        '''Make the header and prepend to feedback'''
        return ''
        
    def make_footer(self):
        '''make the footer for feedback'''
        return ''
        
    
    
    def grade(self):
        '''Main grading entry point'''
        
        #Run main file and parse into env with stdout going to output
        env,output = self.run_hw()
        
        #Check problems and create base feedback with a total
        feedback,total = self.check_hw(env,output)
        
        #Add footer to feedback
        feedback.write(self.make_footer())
        
        #Make the header and prepend to feedback
        feedback.prepend(self.make_header(total))
        
        if not self.show_feedback:
            utils.output.PROGRESS_LOG('Total: {0[total]}/{0[points]}'.format(total),color='green')
       
        return feedback,output
    
    def __init__(self,show_feedback=False):
        self.show_feedback = show_feedback
        
    def run_hw(self):
        ''' Main homework runner
        Runs self.env_file and returns the environment.
        Runs self.main_file and returns the output.
        '''
        #Parse env file into abstract syntax tree
        try:
            tree = self.ParserClass(self.env_file,self.remove_func_list).remove()
            parsed = compile(tree,filename=self.env_file,mode='exec')
        except Exception as e:
            raise GraderSyntaxError(e)
            
        #Execute file into black environment
        #Make name space for student code to execute in
        env = {}
        #Make output logger and set as stdout
        output = utils.output.PrintLogger(end='')
        sys.stdout = output
        
        if self.env_file != self.main_file:
            # Enviornment File and Main File are different
            # Execute the enviornment file and then get output from main_file
            try:
                exec(parsed,env) #execute students code into environment
            except Exception as e:
                # Reset standard out
                sys.stdout = sys.__stdout__
                raise GraderExecuteError(e,output=output)
                
            # Set parsed to main_file to get output from
            parsed = open(self.main_file,'r')
        
        #Execute main_file
        try:
            exec(parsed,env) #exectute students code.
        except Exception as e:
            raise GraderRunTimeError(e,output=output)
        finally:
            # Reset standard out
            sys.stdout = sys.__stdout__
            
        return env,output
        
    def check_hw(self,env,output,show_feedback=False):
        '''Checks all hw problems'''
        feedback = utils.output.PrintLogger(enable=show_feedback or self.show_feedback)
        sys.stdout = feedback
        str_output = str(output)
        total = collections.Counter()
        for test in self.get_problems():
            total += test.check(env,str_output)

        #Reset standard out
        sys.stdout = sys.__stdout__
            
        #Round total points
        total['total'] = round(total['total'],2)
        
        return feedback,total
