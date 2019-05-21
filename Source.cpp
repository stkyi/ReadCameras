#define BOOST_PYTHON_STATIC_LIB
#include <string>
#include <chrono>
#include <thread>
#include <iostream>
#include <boost/python.hpp>
#include <string>
#include <list>
#include <boost/ref.hpp>
using namespace boost::python;

int main() {
	try {
		Py_Initialize();
		object main_module = import("__main__");
		object main_namespace = main_module.attr("__dict__");
		//std::list<int> l = {};
		// Load the QApplication module.
		//exec("from PyQt5.QtWidgets import QApplication", main_namespace);
		//object sys = import("sys");
		//object app = eval("QApplication([])", main_namespace);
		//object app = main_module.attr("QApplication")(boost::ref(sys.attr("argv"));
		
		object pyScript = exec_file("VidManagerEken.py", main_namespace);

		object window0 = main_module.attr("App")("Test", 0, "F", 850, 50);
		object window1 = main_module.attr("App")("Test", 1, "L", 200, 50);
		object window2 = main_module.attr("App")("Test", 2, "R", 525, 50);
		object button_close = main_module.attr("add_button_close")(850, 50);
		window0.attr("sh")();
		window1.attr("sh")();
		window2.attr("sh")();
		button_close.attr("sh")();

		object run_app = main_module.attr("run_app");
		run_app();

		//read global variable in file
		//std::string s = extract<std::string>(main_namespace["strA"]);
		// можно так: s = extract<std::string>(main_module.attr("strA"));
		//std::cout << "strA in C++ space: " << s << std::endl;
		
		/*// read function return result
		object func = main_module.attr("pyFunc");
		func();
		//std::cout << extract<int>(rand2) << std::endl;

		// class inheritance
		/* object cl_peter = main_module.attr("Dog")("Peter");
		object cl_jhon = main_module.attr("Dog")("Jhon");
		cl_peter.attr("bark")();
		cl_jhon.attr("bark")(); */
		std::cout << "stopping";
		std::cin.ignore(1000, '/n');
	}
	catch(...) {

	}
/*	catch (error_already_set &) {

		PyObject *ptype, *pvalue, *ptraceback;
		PyErr_Fetch(&ptype, &pvalue, &ptraceback);

		//Extract error message
		std::string strErrorMessage = extract<std::string>(pvalue);
		std::cout << strErrorMessage;
		std::cin.ignore(1000, '/n');
	}	*/
}