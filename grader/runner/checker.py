import grader.utils as utils


class Problem(object):
    
    def __init__(self,name,checks,points=None):
	self.name = name
	self.checks = checks
	points = points if points is not None else len(self.checks)
	self.points = float(points)
    
    def check(self,env):
	print utils.output.colorify(self.name,'blue')
	correct = 0
	for test,result in self.checks:
	    out = eval(test,None,env)
	    check = out == result #ToDo: Change this to a better equality
	    
	    print '\tassert {}'.format(test),
	    if not check:
		print '  FAIL!\n\t  {} != {}'.format(out,result)
	    else:
		print '  OK'
		correct +=1
	total = correct*points/len(checks)
	
	print utils.output.colorify('\tCorrectness: {}/{}\n'.format(total,points),'green')
	return total,points
    
