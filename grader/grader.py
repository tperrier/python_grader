#!/usr/bin/python

#system imports
import sys, os, shutil, time, re, subprocess, csv, code
#local imports
import utils,config

def grade(args):
    
    #Create grading sandbox if needed
    if args.refresh_sandbox or not os.path.exists(args.grading_sandbox):
        utils.output.PROGRESS_LOG.header("Creating grading sandbox...")
        utils.dirs.ensure_directory_exists(args.grading_sandbox)
        utils.dirs.copy_all(args.grading_folder, args.grading_sandbox, *args.grade.required_for_grading)
    else:
        utils.output.PROGRESS_LOG.warn("Grading sandbox exists. Assuming files required for grading are present.")
    print
    
    TOTAL_SUBMISSIONS = len(args.submission_folders)
    for i,submission_path in enumerate(args.submission_folders):
        # Print Header
        progress_msg = 'Preparing to grade student {1}/{2} ({0})...'.format(submission_path, i, TOTAL_SUBMISSIONS)
        utils.output.PROGRESS_LOG.header(progress_msg)
        
        # Copy in the solution files to grading sandbox
        utils.dirs.copy_all(submission_path, args.grading_sandbox, *args.grade.solution_files)
        

        #change working directory to grading sandbox
        cwd = os.getcwd()
        os.chdir(args.grading_sandbox)
        
        try:
            grade_student(args,submission_path)
            error_dir = ''
        except Exception as e:
            print e
            error_dir = 'errors'
            
                
        #Change back to cwd
        os.chdir(cwd)
        
        #Get Feedback path 
        # Get relative path between submission_dir and submission_path and duplicate dir structure for feedback
        feedback_dir,submission_file = os.path.split(os.path.relpath(submission_path,args.submission_dir))
        feedback_path = os.path.join(args.feedback_dir,feedback_dir,error_dir,submission_file)
        if os.path.exists(feedback_path):
            if not args.quite:
                utils.output.verify("Are you sure you want to overwrite existing feedback for this student?")
                utils.dirs.ensure_directory_exists(feedback_path)
        else:
            utils.dirs.ensure_directory_exists(feedback_path)
        
        #Copy export_files to feedback_path
        try:
            utils.dirs.copy_all(args.grading_sandbox,feedback_path,*args.grade.export_files)
        except IOError as e:
            utils.output.PROGRESS_LOG.warn(str(e))
        
        #Delete generated files
        files_to_delete = args.grade.solution_files | args.grade.generated_files | args.grade.export_files
        utils.dirs.remove_all(*files_to_delete,parent_path=args.grading_sandbox)
        
        progress_msg = 'Done. Feedback in {0}'.format(feedback_path)
        utils.output.PROGRESS_LOG.header(progress_msg)

def grade_student(args,submission):
    first_time = True
    while first_time or args.pause:
        #Run run_hw() from grade
        args.grade.run_hw()
        print 'After'
        first_time = False #Exit while loop if args.pause is false 
        if args.pause:
            # Pause in case the grader needs to review this student's files
            response = raw_input("\nThe student's output files are currently in the grading sandbox for review.\n" \
                      "Type 'regrade' to rerun the scripts, or anything else to continue: ").lower()
            if response in ['regrade']:
                continue #Repeat while loop
            else:
                #No regrade so exit while loop
                break

            
def student_from_submission_dir(path):
    '''
    Given the path to a student submission on the form: folder1/folder2/LASTNAME_UWID
    Return tuple(lastname,uwid)
    '''
    head,tail = os.path.split(path)
    if tail is '': #path ends with a slash
        tail = os.path.basename(head)
        
    dir_split = tail.split('_')
    return (dir_split[0],dir_split[1]+os.path.abspath(path))

        
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
