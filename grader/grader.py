#!/usr/bin/python

#system imports
import sys, os, shutil, time, re, subprocess, csv, code, traceback,StringIO
#local imports
import utils,config
from runner import GraderException

def grade_errors(args):

    #Get submission folders:
    #Get submission folders
    if args.target:
        errors_dirs = args.target[:]
    elif args.submissions_folder:
        errors_dirs = [os.path.join(args.feedback_dir,args.submissions_folder,'errors')]
    else:
        feedback_dirs = utils.dirs.get_sub_directories(args.feedback_dir)
        errors_dirs = []
        for fd in feedback_dirs:
            error_dir = os.path.join(fd,'errors')
            if os.path.isdir(error_dir):
                errors_dirs.append(error_dir)

    submission_folders = []

    for ed in errors_dirs:
        submission_folders.extend(utils.dirs.get_sub_directories(ed))

    create_sandbox(args)

    args.errors = True #We are in error mode

    #Make sure that notes.txt and errors.txt are copied to and from feedback
    args.grade.export_files.update(['notes.txt','errors.txt'])
    args.grade.solution_files.update(['notes.txt','errors.txt'])

    for i,submission_path in enumerate(submission_folders):

        # Print Header
        progress_msg = 'Preparing to grade student {1}/{2} ({0})...'.format(submission_path, i+1, len(submission_folders))
        utils.output.PROGRESS_LOG.header(progress_msg)

        errors = grade_student(args,submission_path)

        #Get path for feedback
        if errors: #There are still errors so place inside feedback/submission_path/errors/lastname_uwid
            # Get relative path between submission_dir and submission_path and duplicate dir structure for feedback
            feedback_path = submission_path
        else: #Move copy to feedback/submission_path/lastname_uwid_FIXED
            dir_split = submission_path.split(os.sep)
            del dir_split[-2]
            dir_split[-1] += '_FIXED'
            feedback_path = os.sep.join(dir_split)

            #also copy original error folder into feedback_path/original
            original_path = os.path.join(feedback_path,'original')
            utils.dirs.copy_all(submission_path,original_path,None)

            #Remove original
            utils.dirs.remove_all(submission_path)

        copy_feedback_and_remove(args,feedback_path)


        progress_msg = 'Correct! Feedback in {0}'.format(feedback_path)
        utils.output.PROGRESS_LOG.header(progress_msg)

    progress_msg = 'All Done!\n'
    for fd in errors_dirs:
        num_errors = len(os.listdir(fd))
        progress_msg = '{} ({}) errors {}'.format(fd,num_errors,'DELETED' if num_errors == 0 else '')
        if num_errors == 0:
            utils.dirs.remove_all(fd)
    utils.output.PROGRESS_LOG(progress_msg,color='blue')

def grade_submissions(args):

    #Get submission folders
    if args.target:
        submission_folders = args.target[:]
    elif args.submissions_folder:
        section_folder = os.path.join(args.submission_dir,args.submissions_folder)
        submission_folders = utils.dirs.get_sub_directories(section_folder,filter=filter_skipped)
    else: #default to all folders inside SUBMISSIONS_DIR
        #Get all subdirectories of SUBMISSION_DIR
        section_folders = utils.dirs.get_sub_directories(args.submission_dir)
        submission_folders = utils.dirs.get_sub_directories(*section_folders,filter=filter_skipped)

    create_sandbox(args)

    for i,submission_path in enumerate(submission_folders):

        # Print Header
        progress_msg = 'Preparing to grade student {1}/{2} ({0})...'.format(submission_path, i+1, len(submission_folders))
        utils.output.PROGRESS_LOG.header(progress_msg)

        errors = grade_student(args,submission_path)

        #Get Feedback path
        errors_dir = 'errors' if errors else ''
        # Get relative path between submission_dir and submission_path and duplicate dir structure for feedback
        feedback_dir,submission_folder = os.path.split(os.path.relpath(submission_path,args.submission_dir))
        feedback_path = os.path.join(args.feedback_dir,feedback_dir,errors_dir,submission_folder)

        #Add notes.txt and errors.txt from export files
        if errors:
            args.grade.export_files.update(['notes.txt','errors.txt'])

        copy_feedback_and_remove(args,feedback_path)

         #Remove notes.txt and errors.txt from export files
        if errors:
            args.grade.export_files.difference_update(['notes.txt','errors.txt'])

        progress_msg = 'Done. Feedback in {0}'.format(feedback_path)
        utils.output.PROGRESS_LOG.header(progress_msg)

def create_sandbox(args):
     #Create grading sandbox if needed
    if args.refresh_sandbox or not os.path.exists(args.grading_sandbox):
        utils.output.PROGRESS_LOG.header("Creating grading sandbox...")
        utils.dirs.ensure_directory_exists(args.grading_sandbox)
        utils.dirs.copy_all(args.grading_folder, args.grading_sandbox, *args.grade.required_for_grading)
    else:
        utils.output.PROGRESS_LOG.warn("Grading sandbox exists. Assuming files required for grading are present.")
    print

def grade_student(args,submission_path):

    # Copy in the solution files to grading sandbox
    utils.dirs.copy_all(submission_path, args.grading_sandbox, *args.grade.solution_files)

    #change working directory to grading sandbox
    cwd = os.getcwd()
    os.chdir(args.grading_sandbox)

    first_time = True
    errors = False
    while first_time or (args.errors and errors):

        errors = False #Reset errors
        try:
            #Run grade() from grade
            feedback,output = args.grade(args.show_feedback).grade()
        except GraderException as e:
            errors = True
            err_msg = str(e)
            #Write output and feedback if they exist
            e.feedback.write_file('feedback.txt') if e.feedback else False
            e.output.write_file('output.txt') if e.output else False
            
            #Write errors.txt
            with(open('errors.txt','w')) as errors_fp:
                errors_fp.writelines(err_msg)
            
            if not os.path.isfile('notes.txt'):
                with open('notes.txt','a') as notes_fp:
                    notes_fp.write('{}\n'.format(submission_path))
        else:
            #Write output
            feedback.write_file('feedback.txt')
            output.write_file('output.txt')

        if args.errors and errors:
            # Pause in case the grader needs to review this student's files
            pause_message = utils.output.colorify('\nThere was an error with the students code\n','error')
            pause_message += err_msg
            pause_message += "\nThe student's output files are currently in the grading sandbox for review.\n"
            pause_message += "Type 'r' to rerun the scripts, or anything else to continue: "
            response = raw_input(pause_message).lower()

            err_msg

            if not response.startswith('r'):
                break #No regrade so exit while loop

        first_time = False #Exit while loop if args.errors is false

    #Change back to cwd
    os.chdir(cwd)

    return errors

def copy_feedback_and_remove(args,feedback_path):
    if os.path.exists(feedback_path):
        if not args.quite:
            utils.output.verify("Are you sure you want to overwrite existing feedback for this student?")
    else:
        utils.dirs.ensure_directory_exists(feedback_path)

    #Copy export_files to feedback_path
    utils.dirs.copy_all(args.grading_sandbox,feedback_path,*args.grade.export_files)

    #Delete generated files
    files_to_delete = args.grade.solution_files | args.grade.generated_files | args.grade.export_files
    utils.dirs.remove_all(args.grading_sandbox,*files_to_delete)


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
    
def filter_skipped(folder):
    return not folder.endswith('_skip')


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


def process_survey(args):
    #Get all subdirectories of FEEDBACK_DIR
    feedback_folders = []
    for path,dirs,files in os.walk(args.feedback_dir):
        feedback_folders.extend([os.path.join(path,f) for f in dirs if not f.endswith('errors')])

    def get_submission_folder(folder_name):
        for submission_path in feedback_folders:
            if folder_name in submission_path:
                print submission_path
                return submission_path

        raise KeyError('Folder {} not found'.format(folder_name))

    with open(args.survey_file, 'rU') as fp:
        csv_file = csv.reader(fp)

        csv_file.next() #skip Intro header
        header = csv_file.next()[8:]
        header = csv_file.next()[:7] + [''] + header

        #Process each survey answer
        for row in csv_file:
            student = config.student_netid_map[row[0]]
            folder_name = '%s_%s'%(student.last_name,student.number)

            try:
                submission_folder = get_submission_folder(folder_name)
            except KeyError as e:
                print utils.output.colorify(str(e),'warning')
            filename = os.path.join(submission_folder,'survery.txt')

            #create survey file and make it stdout
            sys.stdout = open(filename,'w')
            process_survey_row(header,row)
            sys.stdout = sys.__stdout__
