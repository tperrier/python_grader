import sys,copy,abc,re,inspect
import traceback,linecache
import code

import grader.utils as utils
import equals, runner

class CheckerProblem(object):
    
    def __init__(self,name,tests,points=None,env=None,style=0):
        self.name = name
        self.tests = tests
        points = points if points is not None else len(self.checks)
        self.points = float(points)
        self.style = float(style)
        self.env = env if env is not None else {}
        
    def check(self,env,output):
        
        print utils.output.colorify(self.name,'header')
        
        #If there are no tests to run return 0
        if len(self.tests) == 0:
            print '\tNo tests'
            return 0,self.points,self.style
            
        #Create new local environment 
        local_env = copy.copy(env)
        #Add problem globals to the environment 
        local_env.update(copy.deepcopy(self.env))
        correct,pos = 0,0
        for test in self.tests:
            if isinstance(test,OutputCheck):
                check_pass,pos = test.check(local_env,output,pos=pos)
                correct += 1 if check_pass else 0
            else:
                correct += 1 if test.check(local_env,output) else 0
        total = correct*self.points/len(self.tests)

        print utils.output.colorify('\tCorrectness: {}/{}'.format(round(total,2),self.points),'green')
        if self.style != 0:
            print utils.output.colorify('\tStyle: */{}'.format(self.style),'green')
        print ''
        return total,self.points,self.style
            
class BaseCheck(object):
    
    # Make BaseGradeRunner an Abstract Base Class
    __metaclass__ = abc.ABCMeta 
    
    @abc.abstractmethod
    def check(self,env,output):
        return 'Run the check'
        
    @staticmethod
    def fail(answer,solution):
        answer,solution = str(answer), str(solution)
        if len(answer) < 25 and len(solution) < 25:
            return '  (FAIL!)\n\t  {} != {}'.format(answer,solution)
        else:
            return '  (FAIL!)\n\tA: {}\n\tS: {}'.format(answer[:100],solution[:100])
            
    @staticmethod
    def get_error_str():
        #From: http://stackoverflow.com/questions/14519177/python-exception-handling-line-number/20264059#20264059
        exc_type, exc_obj, tb = sys.exc_info()
        stack = traceback.extract_tb(tb)
        filename, lineno, func_name, line = stack[-1]
        return '\t  {}.{} at line {} "{}"\n\t  {}: {}'.format(filename,func_name,lineno,line.strip(),exc_obj.__class__.__name__, exc_obj)


    
class EqualsCheck(BaseCheck):
    
    def __init__(self,eval_str,cmp_obj):
        self.eval_str = eval_str
        self.cmp_obj = cmp_obj
        
    def check(self,env,output):
        try:
            test_obj = eval(self.eval_str,None,env)
        except Exception as e:
            check = None
            err_str = self.get_error_str()
        else:
            check = equals.eq(test_obj,self.cmp_obj)

        print '\tassert {}'.format(self.eval_str),
        if check is None: #There was an exception 
            print '  (EXCEPTION!)\n\{}'.format(err_str)
            return False
        elif not check:
            print self.fail(test_obj,self.cmp_obj)
            return False
        else:
            print '  (OK)'
            return True
        
class OutputCheck(BaseCheck):
    
    def __init__(self,regex_str,label=None,consume=True,**kwargs):
        self.regex_str = regex_str
        self.label = label if label else regex_str
        self.consume = consume
        self.regex_groups = kwargs
        
    def check(self,env,output,pos=0):
        match = re.search(self.regex_str,output[pos:],re.M)
        print '\toutput: %s'%self.label,
        if match:
            groups = match.groupdict()
            next_pos = pos+match.end() if self.consume else pos
            #First check all groups if they exist
            if len(self.regex_groups) != 0 and len(groups) != 0:
                #Compare equality on groups
                for key,value in self.regex_groups.iteritems():
                    if not equals.eq(groups[key],value):
                        print '  (NOT FOUND)'
                        return False, next_pos
            print '  (OK)'
            return True, next_pos
        else:
            print '  (NOT FOUND)'
            return False,pos

class SolutionCheck(BaseCheck):
    
    def __init__(self,eval_str,solution_env):
        self.eval_str = eval_str
        self.solution_env = solution_env
        
    def check(self,env,output):
        
        #Replace environment with solution environment
        solution_env = copy.copy(env)
        #Update with the __dict__ of solution
        solution_env.update(self.solution_env.__dict__)
        solution_obj = eval(self.eval_str,None,solution_env)
        
        try:
            test_obj = eval(self.eval_str,None,env)
        except Exception as e:
            check = None
            err_str = self.get_error_str()
        else:
            check = equals.eq(test_obj,solution_obj)

        print '\tassert {}'.format(self.eval_str),
        if check is None:
            print '  (EXCEPTION!)\n{}'.format(err_str)
            return False
        elif not check:
            print self.fail(out,result)
            return False
        else:
            print '  (OK)'
            return True
            
class MethodCheck(BaseCheck):
    
    def __init__(self,method_name,nargs,varargs=None,keywords=None):
        self.method_name = method_name
        self.nargs,self.varargs,self.keywords = nargs,varargs,keywords
        
    def check(self,env,output):
        
        print '\tcheck method {0.method_name} args: {0.nargs}'.format(self),
        try:
            func = env[self.method_name]
        except KeyError as e:
            print '  (FAIL!)\n\t  {0.method_name} does not exist!'
            return False
        
        arg_spec = inspect.getargspec(func)
        
        if len(arg_spec.args) != self.nargs:
            print '  (FAIL!)\n\t found {} arguments expected {}'.format(len(arg_spec.args),self.nargs)
            return False
        elif bool(self.varargs) != bool(arg_spec.varargs) or bool(self.keywords) != bool(arg_spec.keywords):
            print '  (FAIL!)\n\t invalid *args ({}) or **kwargs ({})'.format(arg_spec.varargs,arg_spec.keywords)
            return False
        else:
            print '  (OK)'
            return True
            
