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
            
        #update environment
        env.update(copy.deepcopy(self.env))
        correct,pos = 0,0
        for test in self.tests:
            if isinstance(test,OutputCheck):
                check_pass,pos = self.check(env,output,pos=pos)
            else:
                correct += 1 if test.check(env,output) else 0
        total = correct*self.points/len(self.tests)

        print utils.output.colorify('\tCorrectness: {}/{}'.format(total,self.points),'green')
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
        main_obj = eval(self.eval_str,None,env)
        check = equals.eq(main_obj,self.cmp_obj)

        print '\tassert {}'.format(self.eval_str),
        if not check:
            print '  (FAIL!)\n\t  {} != {}'.format(out,result)
            return False
        else:
            print '  (OK)'
            return True
        
class OutputCheck(BaseCheck):
    
    def __init__(self,eval_str,regex,consume=True,pos=0,**kwargs):
        self.regex = regex
        self.consume = consume
        self.regex_groups = kwargs
        
    def check(self,env,output):
        match = self.regex.search(output[pos:],re.M)
        if match:
            groups = match.groupdict()
            next_pos = pos+match.end() if self.consueme else pos
            #First check all groups if they exist
            if len(self.regex_groups) != 0 and len(groups) != 0:
                #Compare equality on groups
                for key,value in self.regex_groups.iteritems():
                    if not equals.eq(groups[key],value):
                        return False, next_pos
            return True, next_pos
        else:
            return False,pos

def check_problems(problem_list,env):

    total = vector.Vector(0,0,0)

    try:
        for problem in problem_list:
            total += problem.check(env)
    except Exception as e:
        #Reset stdout
        sys.stdout = sys.__stdout__
        #Print Error message
        err_str = "EXPECTION RUNNING CODE {}".format(e)
        utils.output.PROGRESS_LOG(err_str,color='error')

        #Get string traceback
        error_output = utils.output.PrintLogger()
        traceback.print_exc(file=error_output)
        error_output.write_file('output.txt')
        raise runner.GraderException(str(error_output))

    return total
