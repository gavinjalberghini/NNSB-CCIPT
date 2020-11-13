## Script Information
* __PYTHON__

  * _gather.py_: Hit noaa_coop API for Sewells Point to gather Sea Level and Tide data. Information is pushed to CSV format in __Code/Data__ folder.

  * _push.py_: Take information stored in __Code/Data__ directory and push it into SQL schema as defined in __System_Documentation/Diagrams/NNSB_RELATIONAL_SCHEMA.pdf__.

  * _process.py_: Generate polynomial regression lines for sea and tide data. Calculate waight average of land subsidence for Newprot News area. 

  * _gui.py_: Collect user input and deliver it to other scripts.
  
* __BATCH (Windows)__

* __SHELL (Unix)__
