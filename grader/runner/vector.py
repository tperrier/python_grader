import code


class Vector(tuple):
    
    def __new__(cls,*args):
	return super(Vector,cls).__new__(cls,tuple(args))
    
    def __init__(self,*args):
	super(tuple,self).__init__(args)
    
    def __iadd__(self,other):
	return Vector(*[sum(t) for t in zip(self,other)])
	
	

if __name__ == '__main__':
    
    print 'Testing Vector'
    v = Vector(1,2)
    print v
    v += (2,3)
    print v
    code.interact(local=locals())
