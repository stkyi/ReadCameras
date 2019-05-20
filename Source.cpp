#define BOOST_PYTHON_STATIC_LIB
#include <string>
#include <iostream>
#include <boost/python.hpp>
using namespace boost::python;

int main() {
	try {
		Py_Initialize();
		object main_module = import("__main__");
		object main_namespace = main_module.attr("__dict__");

		object pyScript = exec_file("hello.py", main_namespace);

		/* Тут хотелось бы получить ссылку на python строку, а не копировать ее в C++ строку s: */
		std::string s = extract<std::string>(main_namespace["strA"]);
		
		/* можно так: s = extract<std::string>(main_module.attr("strA")); */

		std::cout << "strA in C++ space: " << s << std::endl;
		
		object func = main_module.attr("pyFunc");
		object rand2 = func();
		std::cout << extract<int>(rand2) << std::endl;

		object cl_peter = main_module.attr("Dog")("Peter");
		
		//std::cout << extract<int>(cl.attr("bark")()) << std::endl;
		object cl_jhon = main_module.attr("Dog")("jhon");
		cl_peter.attr("bark")();
		cl_jhon.attr("bark")();

		std::cin.ignore(1000, '/n');
	}
	catch (error_already_set const &) {
		if (PyErr_ExceptionMatches(PyExc_ZeroDivisionError)) {
			/* handle ZeroDivisionError specially */
		}
		else {
			/* print all other errors to stderr */
			PyErr_Print();
		}
	}
}