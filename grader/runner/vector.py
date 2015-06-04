import code
import itertools as it


class Vector(tuple):
    
    def __new__(cls,*args):
	return super(Vector,cls).__new__(cls,tuple(args))
    
    def __init__(self,*args):
	if len(args) > 0:
	    super(tuple,self).__init__(args)
	    self.initalized = True
	else:
	    self.initalized = False
    
    def __add__(self,other):
	if self.initalized:
	    return Vector(*[s+o for s,o in it.izip_longest(self,other,fillvalue=0)])
	else:
	    return Vector(*other)
	
	

if __name__ == '__main__':
    
    print 'Testing Vector'
    v = Vector(1,2)
    print v
    v += (2,3)
    print v
    code.interact(local=locals())
