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

		dict d = extract<dict>(main_module.attr("__dict__"));
		object fptr1 = d["pyFunc"];
		//std::function<bool()> fptr2(fptr1);
		std::cout << bool(fptr1()) << " " << std::endl;

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