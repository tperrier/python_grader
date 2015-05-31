import sys,traceback,copy,abc,re

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
    
class EqualsCheck(BaseCheck):
    
    def __init__(self,eval_str,cmp_obj):
        self.eval_str = eval_str
        self.cmp_obj = cmp_obj
        
    def check(self,env,output):
        err_str = None
        try:
            test_obj = eval(self.eval_str,None,env)
            check = equals.eq(test_obj,self.cmp_obj)
        except Exception as e:
            check = None
            err_str = str(e)

        print '\tassert {}'.format(self.eval_str),
        if check is None: #There was an exception 
            print '  (EXCEPTION!)\n\t *** {} ***'.format(err_str)
            return False
        elif not check:
            print '  (FAIL!)\n\t  {} != {}'.format(test_obj,self.cmp_obj)
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
        test_obj = eval(self.eval_str,None,env)
        
        #Replace environment with solution environment
        solution_env = copy.copy(env)
        solution_env.update(self.solution_env)
        solution_obj = eval(self.eval_str,None,solution_env)
        
        check = equals.eq(test_obj,solution_obj)

        print '\tassert {}'.format(self.eval_str),
        if not check:
            print '  (FAIL!)\n\t  {} != {}'.format(out,result)
            return False
        else:
            print '  (OK)'
            return True
