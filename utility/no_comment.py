# Remove Comments on Micropython Programs

# MP programs running on PICO W have limited space.
# This program removes text in the comment line but retains the comment.
# That means when an error occurs, the line number reported
# still matches the original source
# Note: This does remove comments at the end of a line

__program__="no_comment.py"
__version__="1.0"

import sys

# It is assumed that this program will run on the host computer for
# the PICO W. Prevent it accidentally running on the PICO by checking
# the platform.

if sys.platform == "rp2":
    print("You are running this program on the PICO W")
    print("Change and run on the host computer")
    sys.exit(1)

src_dir = "."

if len(sys.argv) == 1:
    print("No file name provided")
    sys.exit(1)
    
# Filename is entered without .PY
fname=sys.argv[1]
src=src_dir+"/"+fname+".py"
# The target file is the source file name with _NC added (No Comment)
trg=src_dir+"/"+fname+"_NC.py"
print("Uncommenting "+src+" >> "+trg)

# reading the file
with open(src) as fp:
    contents=fp.readlines()

c_removed=0
saved=0

for number in range(len(contents)):
    # Look for # after the first 5 lines. Keep brief description
    # of the first 5 lines
    if (contents[number].strip()[:1] == "#") and (number > 5):
        c_removed +=1
        saved +=len(contents[number])-1 # Subtract retained #
        contents[number]="#\n"

# writing into a new file
with open(trg,"w") as fp:
    fp.writelines(contents)
    
print(c_removed,"comment lines removed.",saved, "characters removed")




