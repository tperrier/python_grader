#!/usr/bin/python

import os,shutil
import output

def get_sub_directories(*paths):
    '''
    
    '''
    sub_dirs = []
    for path in paths:
        if not os.path.isdir(path):
            continue #short circuit if not a directory 
        for sub in next(os.walk(path))[1]:
            sub_dirs.append(os.path.join(path,sub))
    return sub_dirs

def ensure_directory_exists(path):
    '''
    
    '''
    if not os.path.exists(path):
        output.DEBUG_LOG("Creating {0}...".format(path))
        os.makedirs(path)

def copy_all(src_parent_path, dst_parent_path, *paths):
    '''
    
    '''
    ensure_directory_exists(dst_parent_path)
    #If there are no paths then use files in src_parents_path
    if len(paths) > 0 and paths[0] == None:
        paths = os.listdir(src_parent_path)
    for path in paths:
        src_path = os.path.join(src_parent_path, path)
        if not os.path.exists(src_path):
            raise IOError('Could not copy. File or folder DNE: {0}'.format(src_path))
        elif os.path.isfile(src_path):
            shutil.copy2(src_path, dst_parent_path)
        elif os.path.isdir(src_path):
            if os.path.exists(dst_parent_path):
                shutil.rmtree(dst_parent_path)
            dst_path = os.path.join(dst_parent_path,os.path.basename(src_path))
            print src_path,dst_path
            shutil.copytree(src_path, dst_path)

def remove_all(parent_path,*paths):
    '''
    
    '''
    if len(paths) == 0:
        shutil.rmtree(parent_path)
    for path in paths:
        path = os.path.join(parent_path,path)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
