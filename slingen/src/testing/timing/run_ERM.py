import os.path
import subprocess
import shutil
import sys
import shlex
import random
from datetime import date

contech_path = "/local/contech/compile"
middle_path = "/home/caparrov/contech/middle"

output_file = "erm.out"
log_file = "erm.log"



# _______________Instrument bitcode _______________
bitcode_file_name = 'main.bc'
instrumented_bitcode_file_name = 'main_ct.bc'

if not os.path.isfile(bitcode_file_name):
	sys.exit("Bitcode file does not exist")
	
# Copy bitecode file to contech dir
shutil.copyfile(os.path.expanduser(bitcode_file_name), os.path.expanduser(contech_path + "/" + os.path.basename(bitcode_file_name))) 

cmd = "python " + contech_path + "/contech_wrapper.py " + contech_path + "/" + os.path.basename(bitcode_file_name)
p = subprocess.Popen(cmd, shell=True, universal_newlines=True)
p.wait()

# Copy back the instrumented bitecode dile
shutil.copyfile(os.path.expanduser(contech_path + "/" + os.path.basename(instrumented_bitcode_file_name)), os.path.expanduser(instrumented_bitcode_file_name)) 


	

# _______________ Run app _______________
# shutil.move(os.getcwd()+"/a.out", os.path.expanduser(path)+"/a.out")
# cmd = os.path.expanduser(path)+"/a.out" 
cmd = "./a.out" 
p = subprocess.Popen(cmd, shell=True, universal_newlines=True)
p.wait() 

# _______________ Generate taskgraph _______________
cmd = middle_path + "/middle /tmp/contech_fe main.taskgraph"
p = subprocess.Popen(cmd, shell=True, universal_newlines=True)
p.wait() 


# _______________Create arguments to ERM from congif _______________
# with open('config.json') as f:
# 	config = json.load(f)
# 	
# config_params=""
# for key in config:
# 	config_params+="-"+key+"="+config[key]+" "


# _______________RUN ERM _______________
out = open(os.path.expanduser(output_file), "w")
out_dir = os.getcwd();
cmd = "/usr/local/bin/opt -load=/local/llvm-3.4-build/Release+Asserts/lib/LLVMDynAnalysisDev.so -EnginePass main_ct.bc -taskgraph-file main.taskgraph -function kernel -uarch SB -warm-cache -vector-code -output-dir="+out_dir+" 2> " + output_file
print cmd
p = subprocess.Popen(cmd, shell=True, universal_newlines=True, stderr=out)
p.communicate()
with open(output_file) as f:
	str_f = f.read()
	if 'LLVM ERROR' in str_f:
		stamp = '.%s.%s' % (date.today().isoformat(), str(random.randint(0,2**32)))
		args = shlex.split("cp -r /home/caparrov/tmp/cpu0 /home/caparrov/caparrov/BENCHMARKS/err_pool/tmp0"+stamp)
		subprocess.call(args)

out.close()

