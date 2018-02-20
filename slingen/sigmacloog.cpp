#include <stdio.h>
#include <string>

#define CLOOG_INT_GMP

#include <cloog/cloog.h>
#include <osl/scop.h>

#include <boost/python.hpp>

using namespace boost::python;

void tosigma(const char * filein, const char * fileout)
{

  CloogState *state;
  CloogInput *input;
  CloogOptions * options ;
  struct clast_stmt *root;
  
  state = cloog_state_malloc();
  options = cloog_options_malloc(state);
  options->openscop = 1;
  options->strides = 1;

  FILE * fin = fopen(filein, "r");
  FILE * fout = fopen(fileout, "w");
  osl_scop_p scop = osl_scop_read(fin);

	input = cloog_input_from_osl_scop(state, scop);
	cloog_options_copy_from_osl_scop(scop, options);

  root = cloog_clast_create_from_input(input, options);
  clast_pprint(fout, root, 0, options);
  
  fclose(fin);
  fclose(fout);
  cloog_clast_free(root);
  cloog_options_free(options) ;
  cloog_state_free(state);
  
}

object tosigma_str(const char * filein)
{

  CloogState *state;
  CloogInput *input;
  CloogOptions * options ;
  struct clast_stmt *root;
  
  state = cloog_state_malloc();
  options = cloog_options_malloc(state);
  options->openscop = 1;
  options->strides = 1;

  FILE * fin = fopen(filein, "r");
  osl_scop_p scop = osl_scop_read(fin);

	input = cloog_input_from_osl_scop(state, scop);
	cloog_options_copy_from_osl_scop(scop, options);

  root = cloog_clast_create_from_input(input, options);
  std::string sigma = sll_pprint("", root, 0, options);
  
  fclose(fin);
  cloog_clast_free(root);
  cloog_options_free(options) ;
  cloog_state_free(state);
  
  return object(sigma);
}


BOOST_PYTHON_MODULE(sigmacloog)
{
    def("tosigma", tosigma);
    def("tosigma_str", tosigma_str);
}

