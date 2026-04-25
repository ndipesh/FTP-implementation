import sys

if(len(sys.argv) <3):
    print('usage: python copy.py <source> <destination>')
    sys.exit()

# open both files
with open(sys.argv[1],"r") as firstfile, open(sys.argv[2],"w") as secondfile:
      
    # read content from first file
    for line in firstfile:
               
             # append content to second file
             secondfile.write(line)
