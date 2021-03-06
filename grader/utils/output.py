#!/usr/bin/python

import sys,re

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
    ''' Class that logs to a given output stream (default sys.stdout) '''

    def __init__(self,enable=False,stream=sys.stdout,end='\n',sep=' '):
        self.enable = enable
        self.stream = stream
        #TODO: make this a string buffer. Is that faster?
        self.output = []
        self.end = end
        self.sep = sep

    def log(self,*messages,**kwargs):
        message = self.join_messages(*messages,**kwargs)
        self.write(message,**kwargs)

    def warn(self,*messages,**kwargs):
        self.log(*messages,color='warning',**kwargs)

    def error(self,*messages,**kwargs):
        self.log(*messages,color='error',**kwargs)

    def header(self,*messages,**kwargs):
        self.log(*messages,color='header',**kwargs)

    def join_messages(self,*messages,**kwargs):
        sep = kwargs.get('sep',self.sep)
        end = kwargs.get('end',self.end)
        return sep.join([m for m in messages])+end

    def write(self,str,**kwargs):
        str = colorify(str,kwargs.get('color',''))
        self.output.append(str)
        self._write(str,**kwargs)

    def prepend(self,str,**kwargs):
        self.output[0:0] = [str]
        self._write(str,**kwargs)

    def _write(self,str,**kwargs):
        enable = kwargs.get('enable',False)
        if enable or (not enable and self.enable):
            self.stream.write(str)

    def write_file(self,file_name):
        with open(file_name,'w') as fp:
            for line in self.output:
                fp.write(remove_color(line))

    def splitlines(self):
        return str(self).splitlines()

    def clear(self):
        self.output = []

    def __str__(self):
        return ''.join(remove_color(line) for line in self.output)

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

color_remover_regex = re.compile(r'\033\[\d+m')
def remove_color(string):
    return color_remover_regex.sub('',string)

DEBUG_LOG = PrintLogger(False)
PROGRESS_LOG = PrintLogger(True)
