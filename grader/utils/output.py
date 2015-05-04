#!/usr/bin/python

import sys

def underline(msg):
    return msg + '\n' + '=' * len(msg)

def verify(query):
    while True:
        response = raw_input(query + ' [y/N]: ').lower()
        if response in ['y']:
            return
        elif response in ['n', '']:
            exit()
        else:
            print 'Please enter a valid response.'
	    
class PrintLogger:
    def __init__(self,enable=False,stream=sys.stdout,end='\n',sep=' '):
        self.enable = enable
	self.stream = stream
	#TODO: make this a string buffer. Is that faster?
	self.output = []
	self.color_output = []
	self.end = end
	self.sep = sep

    def log(self,*messages,**kwargs):
	message = self.join_messages(*messages,**kwargs)
	self.write(message,**kwargs)
	    
    def warn(self,*messages,**kwargs):
	self.log(*messages,color='warning',**kwargs)
	
    def header(self,*messages,**kwargs):
	self.log(*messages,color='header',**kwargs)
    
    def join_messages(self,*messages,**kwargs):
	sep = kwargs.get('sep',self.sep)
	end = kwargs.get('end',self.end)
	return sep.join([m for m in messages])+end
    
    def write(self,str,**kwargs):
	self.output.append(str)
	
	str = colorify(str,kwargs.get('color',''))
	self.color_output.append(str)
	
	enable = kwargs.get('enable',False)
	if enable or (not enable and self.enable):
	    self.stream.write(str)
	    
    def write_file(self,file_name):
	with open(file_name,'w') as fp:
	    fp.writelines(self.output)
	    
    def splitlines(self):
	return str(self).splitlines()
	
    def __str__(self):
	return ''.join(self.output)

    def __call__(self,*messages,**kwargs):
	self.log(*messages,**kwargs)
	
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def colorify(str,*modifiers):
    return ''.join([getattr(colors,m.upper(),'') for m in modifiers]) + ''.join([str,colors.END])

def warn(str):
    return colorify(str,'warning')
    
def header(str):
    return colorify(str,'header')
    
def error(str):
    return colorify(str,'error')
	
DEBUG_LOG = PrintLogger(False)
PROGRESS_LOG = PrintLogger(True)
