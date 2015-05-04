#!/usr/bin/python

import os,shutil
import output

def get_sub_directories(path):
    '''
    
    '''
    sub_directories = next(os.walk(path))[1]
    return [os.path.join(path,sub) for sub in sub_directories]

def to_path_and_create(*elements):
    '''
    
    '''
    path = to_path(*elements)
    ensure_directory_exists(path)
    return path

def to_path(*paths):
    '''
    
    '''
    return os.path.abspath(os.path.join(*paths))

def ensure_directory_exists(path):
    '''
    
    '''
    if not os.path.exists(path):
        output.DEBUG_LOG("Creating {0}...".format(path))
        os.makedirs(path)

def copy_all(src_parent_path, dst_parent_path, *names):
    '''
    
    '''
    def _copy_file(src_path, dst_parent):
        output.DEBUG_LOG("Copying file {0} into {1}...".format(src_path, dst_parent))
        shutil.copy(src_path, dst_parent)

    def _copy_tree(src_path, dst_path):
        output.DEBUG_LOG("Copying folder {0} to {1}...".format(src_path, dst_path))
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)

    for name in names:
        src_path = to_path(src_parent_path, name)

        if not os.path.exists(src_path):
            raise Exception('File or folder does not exist: {0}'.format(src_path))
        ensure_directory_exists(dst_parent_path)

        if os.path.isfile(src_path):
            _copy_file(src_path, dst_parent_path)
        else:
	    shutil.rmtree(path)

def remove(path):
    '''
    
    '''
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
