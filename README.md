# ADIF TOOL

Command line program to manipulate ADIF files.  Basically, some of my adif log files are getting out of hand and I needed some way of chopping them up.  This program has very limited functionality right now.

# Installation under Linux:

1) Uses python3 
2) Clone gitub adif_tool, libs and data repositories
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/adif_tool
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data
3) Install packages needed for adif_tool:
   - cd ~/Python/adif_tool
   - pip3 install -r requirements.txt
4) Make sure its executable:
   - chmod +x adif_tool.py start start_cw
5) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"
6) To run adif_tool, take a look at "score" to see how to set the various args.

# Installation under Mini-conda:

0) Good video:  https://www.youtube.com/watch?v=23aQdrS58e0&t=552s

1) Point browser to https://docs.conda.io/en/latest/miniconda.html
2) Download and install latest & greatest Mini-conda for your particular OS:
   - I used the bash installer for linux
   - As of July 2023: Conda 23.5.2 Python 3.11.3 released July 13, 2023
   - cd ~/Downloads
   - bash Miniconda3-latest-Linux-x86_64.sh
   - Follow the prompts

   - If you'd prefer that conda's base environment not be activated on startup, 
      set the auto_activate_base parameter to false: 

      conda config --set auto_activate_base false

   - To get it to work under tcsh:
       - bash
       - conda init tcsh
       - This creates ~/.tcshrc - move its contents to .cshrc if need be
       - relaunch tcsh and all should be fine!
       - Test with:
           - conda list

3) Create a working enviroment for ham radio stuff:
   - !!! THERE IS A BUG IN re in python 3.11 - need to use 3.10 !!!
   - conda create --name aa2il python=3.10

   - To activate this environment, use:
       - conda activate aa2il
   - To deactivate an active environment, use:
       - conda deactivate

   - conda env list
   - conda activate aa2il

4) Clone gitub adif_tool, libs and data repositories:
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/adif_tool
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data

5) Install packages needed by adif_tool:
   - cd ~/Python/adif_tool
   - pip3 install -r requirements.txt

6) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"

7) To run adif_tool, we need to specify python interpreter so it doesn't run in
   the default system environment:
   - cd ~/Python/adif_tool
   - conda activate aa2il
   - python adif_tool.py

8) Known issues using this (as of July 2023):
   - None

# Installation for Windoz:

1) Best bet is to use mini-conda and follow the instructions above.
2) If you want/need a binary, email me.
