# CodeSys
1. Usage:
    Run the script from within the CODESYS IDE (its embedded Python scripting engine) -- either the IDE's own script console, or `CODESYS.exe --runscript=export.py` from the command line.
2. Script description:

Export.py:
  Backs up the ST-language text (declaration + implementation) of every POU,
  along with Global_var (GVL), Textlist, TaskConfiguration, and library
  objects, into the Save_Folder directory. If a `.git` folder already exists
  inside Save_Folder, commits the updated folder to HEAD.

Load.py:
  Imports the contents of the folder above back into a new CODESYS project.

3. Known issues:
  a. Only ST-language text is exported -- Visualizations (Visu), the
     ImagePool, VisuConfiguration, Project Settings, and Project Information
     are NOT exported.
  b. GlobalTextList loses its ID column data on export.
