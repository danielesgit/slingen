'''
Created on Jun 13, 2014

@author: danieles
'''

import sys
import os
import shlex
import subprocess
from datetime import datetime

if __name__ == "__main__":
    parsername = sys.argv[1]
    grammar = sys.argv[2]
    args = shlex.split('grako -o %s.py %s' % (parsername, grammar) )
    
    print "Generating " + parsername + " from " + grammar + "..."
    if "/usr/local/bin" not in os.environ['PATH']:
        os.environ['PATH'] += ":/usr/local/bin"
    subprocess.call(args)

    #Prepend time info
    t = datetime.now()
    with open(parsername + ".py", 'r+') as f:
        content = f.read()
        f.seek(0)
        f.write("# " + str(t) + "\n" + content)
    
    print "...done."  
