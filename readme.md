This grading script assumes the following file structure

hw2/
    students.csv (Catalyst Gradebook export: Username,Last Name,First Name M.,Student Number,Status)
    survey.csv (Catalyst Homework Survey csv export)
    grader.py
    config.py
    submissions/  (gradeit zip download)
	ta_1 
	ta_2
	ta_3
    grading_scripts/
	grade.py
	    - required_for_grading (list)
	    - solution_files (list)
	    - generated_files (list)
	    - export_files (list)
	    - run_hw (func)
	    - grade_hw (func)
	    
To grade all submissions for ta_1: 

    python grader.py ta_1 submissions/ta_1/* 
    
To grade all submission for ta_1 who's last name starts with C

    python grader.py ta_1 submissions/ta_1/C*
