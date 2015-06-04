
def eq(student, answer):
    # == is stricter than eq, so if == is true,
    # then eq would be true as well.  
    if student == answer:
        return True

    # Compare ints as float instead
    if type(student) == int:
        student = float(student)
    if type(answer) == int:
        answer = float(answer)

    # Arguments must be of the same type.
    if type(student) != type(answer):
        return False

    # Delegate to a more specific comparator. Only the types
    # for this assignment are implemented.
    if type(student) == dict:
        return eq_dict(student, answer)
    elif type(student) == float:
        return eq_float(student, answer)
    elif type(student) == str:
        return eq_str(student, answer)
    elif type(student) == list:
        return eq_list(student,answer)
    elif type(student) == set:
        return eq(list(student),list(answer))
    
    # Return equality as default - this should be False
    return student == answer

def eq_dict(student, answer):
    if not eq(student.keys(),answer.keys()):
        return False

    for key in student:
      if not eq(student[key], answer[key]):
          return False

    return True

def eq_float(student, answer):
    epsilon = 0.00001
    return abs(student - answer) < epsilon

def eq_str(student, answer):
    return student == answer
    
def eq_list(student,answer):
    
    if len(student) != len(answer):
        return False
    
    # Loop through all elemets and compare equality
    for s,a in zip(student,answer):
        if not eq(s,a):
            break # Exit for loop and do not run else
    else:
        # Return true if for loop does not break
        return True
        
    return False
