import sys, os
sys.path.append(os.getcwd())
strA = "python string"
def pyFunc():
    print('python: pyFunc()')
    return 123
class Dog():
    def __init__(self,name):
        self.n = name
    def bark(self):
        print('python:  Dog.bark'+ str(self.n))
        #return 111