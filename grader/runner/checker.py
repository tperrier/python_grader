import sys,copy,abc,re,inspect
import traceback,linecache,collections
import code
import filecmp

import grader.utils as utils
import equals, runner

class CheckerProblem(object):

    def __init__(self,name,tests,env=None,atomic=False,points=None,extra_points=None):
        self.name = name
        self.tests = tests
        self.env = env if env is not None else {}
        self.atomic = atomic
        self.points = float(points if points is not None else len(tests))
        self.extra_points = [ (e[0].lower(),e[1]) for e in extra_points ] if extra_points is not None else []

    def check(self,env,output):

        print utils.output.colorify(self.name,'header')

        #If there are no tests to run return 0
        if len(self.tests) == 0:
            print '\tNo tests'
            return 0,self.points,self.extra_points

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
        if self.atomic:
            total = total if total == self.points else 0

        print utils.output.colorify('\tCorrectness: {:g}/{:g}'.format(total,self.points),'green')
        for label,points in self.extra_points:
            print utils.output.colorify('\t{}: */{}'.format(label.title(),points),'green')
        print ''
        return collections.Counter(total=total,points=self.points,**dict(self.extra_points))

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
        # From: http://stackoverflow.com/a/6961861/2708328
        exc_type, exc_obj, tb = sys.exc_info()

        # Get the last frame on the error stack
        stack = traceback.extract_tb(tb)
        filename, lineno, func_name, line = stack[-1]

        if not isinstance(line,basestring):
            line = ''

        return '\t  {}.{} at line {} "{}"\n\t  {}: {}'.format(
            filename,func_name,lineno,line.strip(),exc_obj.__class__.__name__, exc_obj
        )

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

        print '\t- assert {}'.format(self.eval_str),
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

    def __init__(self, label, regex_str, *args, **kwargs):
        self.regex_str = regex_str
        self.label = label
        self.consume = kwargs.get('consume', True)
        self.convert = kwargs.get('convert', None)
        self.reg_options = kwargs.get('reg_options', re.I|re.M)
        self.regex_solutions = args



    def check(self,env,output,pos=0):
        match = re.search(self.regex_str,output[pos:],self.reg_options)
        print '\t- %s: Expected %s '%(self.label, self.regex_solutions if len(self.regex_solutions) != 1 else self.regex_solutions[0]),
        if match:
            groups = match.groups()
            print 'Found %s'%(groups if len(groups) != 1 else groups[0],),
            next_pos = pos+match.end() if self.consume else pos
            #First check all groups if they exist
            if len(self.regex_solutions) != 0 and len(groups) != 0:
                #Compare equality on groups
                for idx,value in enumerate(self.regex_solutions):
                    answer = groups[idx]
                    if self.convert is not None:
                        answer = self.convert(answer)
                    if not equals.eq(answer,value):
                        print '  (WRONG VALUE)'
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

        print '\t- assert {}'.format(self.eval_str),
        if check is None:
            print '  (EXCEPTION!)\n{}'.format(err_str)
            return False
        elif not check:
            print self.fail(test_obj,solution_obj)
            return False
        else:
            print '  (OK)'
            return True

class MethodCheck(BaseCheck):

    def __init__(self,method_name,nargs,varargs=None,keywords=None):
        self.method_name = method_name
        self.nargs,self.varargs,self.keywords = nargs,varargs,keywords

    def check(self,env,output):

        print '\t- check method {0.method_name} args: {0.nargs}'.format(self),
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

class OutputFileCheck(BaseCheck):
    def __init__(self,student_file,solution_file):
        self.student_file, self.solution_file = student_file, solution_file

    def check(self,env,output):
        print '\t- check output file', self.student_file,
        if filecmp.cmp(self.student_file, self.solution_file):
            print '  (OK)'
            return True
        else:
            print '  (FAIL!)'
            return False


