import os,sys,argparse
import utils,grader,config


def make_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--grading-folder',default='current',help='Directory contaning GRADE_FILE and SUBMISSIONS. Defaults to current',metavar='FOLDER')
    
    parser.add_argument('-t','--target',nargs='*',help='Single submission FOLDER to run',metavar='FOLDER')
    parser.add_argument('-s','--submissions-folder',help='Folder inside SUBMISSION_DIR to process. Defaults to first folder',metavar='SUBMISSIONS_FOLDER')
    
    parser.add_argument('-d','--submission-dir',default=None,help='Directory to find SUBMISSION_FOLDERS in. Default GRADING_FOLDER/submissions',metavar='SUBMISSIONS_DIR') 
    parser.add_argument('--grade-modual',default='grade',help='Python script to run grades',metavar='GRADE_FILE')
    parser.add_argument('--feedback_dir',default=None,help='Directory to place feedback. Default GRADING_FOLDER/feedback')
    
    parser.add_argument('-q','--quite',action='store_true',default=False) #Yes to everything
    parser.add_argument('-f','--show-feedback',action='store_true',default=False)
    parser.add_argument('--refresh-sandbox',action='store_true',default=False,help='Refresh all config scripts in Grading Sandbox')
    parser.add_argument('--no-pause',action='store_true',default=False)
    parser.add_argument('--survey',action='store_true',default=False,help='Parse survey results into folder')
    
    return parser

if __name__ == '__main__':
    
    #Parse Args 
    parser = make_argument_parser()
    args = parser.parse_args()
    print args
    
    # Process survey and exit if --survey flag set
    if args.survey:
        print "Processing HW survey...."
        grader.process_survey()
        print "Done"
        sys.exit()

    #Import grad.py file - will rise error if not found
    sys.path.append(args.grading_folder)
    args.grade = __import__(args.grade_modual)
    
    #Set ta based on grading_folder or chose a default ta
    try:
        args.ta = config.ta_map[args.grading_folder]
    except KeyError as e:
        args.ta = next(config.ta_map.itervalues())
        print utils.output.colorify('Grader {} not found using {}'.format(args.grading_folder,args.ta.short_name),'warning')
    
    if args.submission_dir is None:
	args.submission_dir = os.path.join(args.grading_folder,'submissions')
    if args.feedback_dir is None:
	args.feedback_dir = os.path.join(args.grading_folder,'feedback')
    #Get submission folders
    if args.target:
	args.submission_folders = args.target[:]
    elif args.submissions_folder:
        args.submission_folders = utils.dirs.get_sub_directories(os.path.join(args.submission_dir,args.submissions_folder))
    else: #default to first folder inside SUBMISSIONS_DIR
	section_folders = utils.dirs.get_sub_directories(args.submission_dir)
	print section_folders
	args.submission_folders = utils.dirs.get_sub_directories(section_folders[0])

    #Run grader
    grader.grade(args)
    
