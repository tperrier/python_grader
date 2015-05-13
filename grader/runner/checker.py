import sys,traceback,copy
import grader.utils as utils
import equals, vector, runner

class EqualsProblem(object):

    def __init__(self,name,checks,points=None,env=None):
        self.name = name
        self.checks = checks
        points = points if points is not None else len(self.checks)
        self.points = float(points)
        self.env = env if env is not None else {}

    def check(self,env):
        print utils.output.colorify(self.name,'blue')

        #No tests to run so 0 points
        if len(self.checks) == 0:
            print '\tNO Tests'
            return 0,self.points

        correct = 0
        #Update environment
        env.update(copy.deepcopy(self.env))
        for test,result in self.checks:
            out = eval(test,None,env)
            check = equals.eq(out,result)

            print '\tassert {}'.format(test),
            if not check:
                print '  FAIL!\n\t  {} != {}'.format(out,result)
            else:
                print '  OK'
            correct +=1
        total = correct*self.points/len(self.checks)

        print utils.output.colorify('\tCorrectness: {}/{}\n'.format(total,self.points),'green')
        return total,self.points


def check_problems(problem_list,env):

    total = vector.Vector(0,0)

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


