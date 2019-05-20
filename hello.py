import sys, os
sys.path.append(os.getcwd())
strA = "python string"
def pyFunc():
    print('python: pyFunc()')
    return 123
class Dog():
    def bark(self):
        print('python:  Dog.bark')
        return 111