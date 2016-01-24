#standard lib from standard lib
import os,sys,argparse

#local imports
import utils,grader

''' Main invokation of grading scripts '''

def make_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--grading-folder',default='current',help='Directory containing GRADE_FILE and SUBMISSIONS. Defaults to current',metavar='FOLDER')

    # for grading a subset of a submission directory
    parser.add_argument('-t','--target',nargs='*',help='Single submission FOLDER to run',metavar='FOLDER')
    parser.add_argument('-s','--submissions-folder',help='Folder inside SUBMISSION_DIR to process. Defaults to all folders',metavar='SUBMISSIONS_FOLDER')

    parser.add_argument('-d','--submission-dir',default=None,help='Directory to find SUBMISSION_FOLDERS in. Default GRADING_FOLDER/submissions',metavar='SUBMISSIONS_DIR')
    parser.add_argument('--grade-modual',default='grade',help='Python script to run grades. Default GRADING_FOLDER/grade.py ',metavar='GRADE_FILE')
    parser.add_argument('--feedback_dir',default=None,help='Directory to place feedback. Default GRADING_FOLDER/feedback')

    parser.add_argument('-q','--quiet',action='store_false',default=True,help='Say yes to everything. Default is True')
    parser.add_argument('-f','--show-feedback',action='store_true',default=False)
    parser.add_argument('--refresh-sandbox',action='store_true',default=False,help='Refresh all config scripts in Grading Sandbox')

    parser.add_argument('--survey',action='store_true',default=False,help='Parse survey results into folder')
    parser.add_argument('-c','--survey-file',default=None,help='Location of csv file of survey results. Default GRADING_FOLDER/survey.csv',metavar='CSV_FILE')
    parser.add_argument('--errors',action='store_true',default=False,help='Run in error mode')

    return parser

if __name__ == '__main__':

    #Parse Args
    parser = make_argument_parser()
    args = parser.parse_args()

    #Set default SUBMISSIONS and FEEDBACK folders if not set.
    if args.submission_dir is None:
        args.submission_dir = os.path.join(args.grading_folder,'submissions')
    if args.feedback_dir is None:
        args.feedback_dir = os.path.join(args.grading_folder,'feedback')
    if args.survey_file is None:
        args.survey_file = os.path.join(args.grading_folder,'survey.csv')
    #Set sandbox folder
    args.grading_sandbox = os.path.join(args.grading_folder,'sandbox')

    # Check that grading folder and submission folder exisit
    if not os.path.exists(args.grading_folder):
        print utils.output.warn('Grading folder "%s" Not Found'%args.grading_folder)
        sys.exit()
    if not os.path.exists(args.submission_dir):
        print utils.output.warn('Submission folder "%s" Not Found'%args.submission_dir)
        sys.exit()

    # Process survey and exit if --survey flag set
    if args.survey:
        print "Processing HW survey...."
        grader.process_survey(args)
        print "Done"
        sys.exit()

    #Import grad.py file - will rise error if not found
    sys.path.append(args.grading_folder)
    grade_modual = __import__(args.grade_modual)
    args.grade = grade_modual.GradeRunner

    #Grade in either error mode or submissions mode
    if args.errors:
        grader.grade_errors(args)
    else: #default grade all submissions
        grader.grade_submissions(args)
