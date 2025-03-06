# input_str = 'This is a sample cucumber expression string with {param1}, {param2} and {param3}'
# regex='^ [^{}]* (\{\w\})$'

import re

txt = "There are {xvar} number of flowers in  {yvar} baskets."

#Check if "ain" is present at the beginning of a WORD:

x = re.findall(r"(\{\S+\})", txt)

for group in x:
    print(group)

if x:
  print("Yes, there is at least one match!")
else:
  print("No match")
