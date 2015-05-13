
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

def eq_dict(student, answer):
    # In this assignment, keys will never be float, so this 
    # comparison is okay.
    if set(student.keys()) != set(answer.keys()):
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
