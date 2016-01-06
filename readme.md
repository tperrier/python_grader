# Usage
    usage: __main__.py [-h] [-g FOLDER] [-t [FOLDER [FOLDER ...]]]
                       [-s SUBMISSIONS_FOLDER] [-d SUBMISSIONS_DIR]
                       [--grade-modual GRADE_FILE] [--feedback_dir FEEDBACK_DIR]
                       [-q] [-f] [--refresh-sandbox] [--survey] [-c CSV_FILE]
                       [--errors]

    optional arguments:
      -h, --help            show this help message and exit
      -g FOLDER, --grading-folder FOLDER
                            Directory containing GRADE_FILE and SUBMISSIONS.
                            Defaults to current
      -t [FOLDER [FOLDER ...]], --target [FOLDER [FOLDER ...]]
                            Single submission FOLDER to run
      -s SUBMISSIONS_FOLDER, --submissions-folder SUBMISSIONS_FOLDER
                            Folder inside SUBMISSION_DIR to process. Defaults to
                            all folders
      -d SUBMISSIONS_DIR, --submission-dir SUBMISSIONS_DIR
                            Directory to find SUBMISSION_FOLDERS in. Default
                            GRADING_FOLDER/submissions
      --grade-modual GRADE_FILE
                            Python script to run grades. Default
                            GRADING_FOLDER/grade.py
      --feedback_dir FEEDBACK_DIR
                            Directory to place feedback. Default
                            GRADING_FOLDER/feedback
      -q, --quite           Say yes to everything. Default is True
      -f, --show-feedback
      --refresh-sandbox     Refresh all config scripts in Grading Sandbox
      --survey              Parse survey results into folder
      -c CSV_FILE, --survey-file CSV_FILE
                            Location of csv file of survey results. Default
                            GRADING_FOLDER/survey.csv
      --errors              Run in error mode

This grading script assumes the following file structure

* students.csv (Catalyst Gradebook export: Username,Last Name,First Name M.,Student Number,Status)
* grader/ (Folder with grading library core - invoke with python -m grader)
  * grader.py
  * config.py
* homework_folder/ (Folder with gradit submissions and main grading script)
  * survey.csv (Catalyst Homework Survey csv export)
  * submissions/  (gradeit zip download)
    * ta_1
    * ta_2
    * ta_3
    * grade.py
      - required_for_grading (list)
      - solution_files (list)
      - generated_files (list)
      - export_files (list)
      - get_problems (function that returns list of problems)

To grade all submissions for ta_1:

    python grader.py ta_1 submissions/ta_1/*

To grade all submission for ta_1 who's last name starts with C

    python grader.py ta_1 submissions/ta_1/C*
