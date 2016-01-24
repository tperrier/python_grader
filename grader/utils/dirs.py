#!/usr/bin/python

import os,shutil,glob,sys
import output

def get_sub_directories(*paths,**kwargs):
    '''

    '''
    filter = kwargs.get('filter',None)
    sub_dirs = []
    for path in paths:
        if not os.path.isdir(path):
            continue #short circuit if not a directory
        for sub in next(os.walk(path))[1]:
            if filter is None or filter(sub):
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
    print paths
    for glob_path in paths:
        src_path = os.path.join(src_parent_path, glob_path)
        glob_files = glob.glob(src_path)
        print >> sys.stderr , src_parent_path, glob_path
        for path in glob_files:
            copy_one(path, dst_parent_path)

def copy_one(src_path,dst_parent_path):
    '''

    '''
    if not os.path.exists(src_path):
            print output.colorify('Could not copy. File or folder DNE: {0}'.format(src_path),'warning')
    elif os.path.isfile(src_path):
        ensure_directory_exists(dst_parent_path)
        shutil.copy2(src_path,dst_parent_path)
    elif os.path.isdir(src_path):
        dst_path = os.path.join(dst_parent_path,os.path.basename(src_path))
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)

def remove_all(parent_path,*paths):
    '''

    '''
    if len(paths) == 0:
        shutil.rmtree(parent_path)
    for glob_path in paths:
        glob_path = os.path.join(parent_path,glob_path)
        for path in glob.glob(glob_path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
