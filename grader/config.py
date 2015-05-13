import collections,csv,os

TeachingAssistant = collections.namedtuple('TA',['name','short_name','email','section'])

ta_map = {}
with open('ta.csv','r') as fp:
    reader = csv.reader(fp)
    reader.next() #skip header

    for row in reader:
	ta = TeachingAssistant(*row)
	ta_map[ta.short_name] = ta

Student = collections.namedtuple('Student',['username','last_name','first_name','number','status'])
student_id_map = {}  #Maps number:student nameedtuple
with open('students.csv','rU') as fp:
    reader = csv.reader(fp)
    reader.next() #skip header

    #Loop through students and add active ones to student map
    for row in reader:
	student = Student(*row)
	if student.status == 'Active':
	    student_id_map[student.number] = student

student_netid_map = {s.username:s for s in student_id_map.values()}
