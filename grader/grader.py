#!/usr/bin/python

#system imports
import sys, os, shutil, time, re, subprocess, csv, code
#local imports
import utils,config

def grade(args):
    
    #Create grading sandbox if needed
    args.grading_sandbox_path = os.path.abspath(os.path.join(args.grading_folder,'sandbox'))
    if args.refresh_sandbox or not os.path.exists(args.grading_sandbox_path):
        utils.output.PROGRESS_LOG.header("Creating grading sandbox...")
        utils.dirs.ensure_directory_exists(args.grading_sandbox_path)
        utils.dirs.copy_all(args.grading_folder, args.grading_sandbox_path, *args.grade.required_for_grading)
    else:
        utils.output.PROGRESS_LOG.warn("Grading sandbox already exists. Assuming all files required for grading are present.")
    print
    
    cwd = os.getcwd()
    TOTAL_SUBMISSIONS = len(args.submission_folders)
    for i,submission in enumerate(args.submission_folders):
        # Print Header
        progress_msg = 'Preparing to grade student {1}/{2} ({0})...'.format(submission, i, TOTAL_SUBMISSIONS)
        utils.output.PROGRESS_LOG.header(progress_msg)
        
        #get information from gradeit form
        #~ late_days,first_name,last_name,email,gradit_sid = from_gradeit(os.path.join(submission_path,'form.txt'))
        #~ print late_days,first_name,last_name,email,gradit_sid
        
        grade_student(args,submission)

        #Copy code over output and answers to feedback direcotry
        for from_file in args.grade.export_files:
            to_file = os.path.join(os.path.join(cwd,feedback_path),os.path.basename(from_file))
            shutil.copy2(from_file,to_file)
        
        #TODO: Make a delet all _os function
        delete_graded_files(args)
        
        os.chdir(cwd)

def grade_student(args,submission):
    student_name, student_id, submission_path = student_from_submission_dir(submission)
    
    # Do we really want to overwrite this student's feedback?
    rel_submission_dir = os.path.relpath(submission_path,args.submission_dir)
    feedback_path = os.path.join(args.feedback_dir,rel_submission_dir, student_name + '_' + student_id)
    if os.path.exists(feedback_path):
        if not args.quite:
            utils.output.verify("Are you sure you want to overwrite existing feedback for this student?")
    else:
        utils.dirs.ensure_directory_exists(feedback_path)
        
    utils.output.PROGRESS_LOG.warn(student_name,student_id,feedback_path)

    # Copy in the solution files to grading sandbox
    utils.dirs.copy_all(submission_path, args.grading_sandbox_path, *args.grade.solution_files)
    
    #change working directory to grading sandbox
    os.chdir(args.grading_sandbox_path)
    
    #Run run_hw() from grade
    args.grade.run_hw(args)
    
    if not args.no_pause:
        # Pause in case the grader needs to review this student's files
        response = raw_input("\nThe student's output files are currently in the grading sandbox for review.\n" \
                  "Type 'regrade' to rerun the scripts, or anything else to continue: ").lower()
        if response in ['regrade']:
            grade_student(args,submission) #recusive call
            
def student_from_submission_dir(path):
    '''
    Given the path to a student submission on the form: folder1/folder2/LASTNAME_UWID
    Return tuple(lastname,uwid)
    '''
    head,tail = os.path.split(path)
    if tail is '': #path ends with a slash
        tail = os.path.basename(head)
        
    return tuple(tail.split('_')+[os.path.abspath(path)])

        
def from_gradeit(form_txt):
    '''
    Return:  late_days,first_name,last_name,email,gradit_sid
    '''
    with open(form_txt,'r') as form:
        lines = form.readlines()
        late_days = lines[1].split('=')[1].strip()
        first_name = lines[2].split('=')[1].strip()
        last_name = lines[4].split('=')[1].strip()
        email = lines[5].split('=')[1].strip()
        gradit_sid = lines[6].split('=')[1].strip()
        return late_days,first_name,last_name,email,gradit_sid

def delete_graded_files(args):
    """ Remove all solution files and generated files from the grading sandbox. """
    remove_files = args.grade.solution_files + args.grade.generated_files
    remove_paths = map(lambda fn: utils.dirs.to_path(args.grading_sandbox_path, fn), remove_files)

    for path in remove_paths: 
        utils.output.DEBUG_LOG('Removing {0}'.format(path))
        utils.dirs.remove(path)
        
########################
# HW survey row methods: assume the survey.csv file is in this same directory
########################

def process_survey_row(header,row):
    for i in range(12):
        if i<7:
            print '%s: %s'%(header[i],row[i])
        elif i==7:
            print '\n'
        elif i>7:
            print '%s:\n\t%s\n'%(header[i],row[i])
            

def process_survey(csv_file='survey.csv'):
    with open(csv_file) as fp:
        csv_file = csv.reader(fp)

        csv_file.next() #skip Intro header
        header = csv_file.next()[8:]
        header = csv_file.next()[:7] + [''] + header
        
        #Process each survey answer
        for row in csv_file:
            student = config.student_netid_map[row[0]]
            folder = '%s_%s'%(student.last_name,student.number)
            filename = 'surveys/%s/survey.txt'%folder
            
            #create survey file and make it stdout
            os.makedirs(os.path.dirname(filename))
            sys.stdout = open(filename,'w')
            process_survey_row(header,row)
            sys.stdout = sys.__stdout__
