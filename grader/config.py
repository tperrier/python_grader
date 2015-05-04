import collections,csv,os

TeachingAssistant = collections.namedtuple('TA',['name','short_name','email','section'])

ta_map = {
    'nick':TeachingAssistant('Nick Shahan','nick','nshahan@cs.washington.edu','AB'),
    'lee':TeachingAssistant('Lee Organick','lee','leeorg@cs.washington.edu','AA'),
    'trevor':TeachingAssistant('Trevor Perrier','trevor','tperrier@cs.washington.edu','AC'),
}


Student = collections.namedtuple('Student',['username','last_name','first_name','number','status'])

student_id_map = {}  #Maps number:student nameedtuple 
with open('students.csv','r') as fp:
    reader = csv.reader(fp)
    reader.next() #skip header
    
    #Loop through students and add active ones to student map
    for row in reader:
	student = Student(*row)
	if student.status == 'Active':
	    student_id_map[student.number] = student

student_netid_map = {s.username:s for s in student_id_map.values()}
