Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Build the command to run
pythonScript = scriptDir & "\launch_monitor.py"
configFile = "configs\monitor1.json"

' Run the Python script WITH a visible window for debugging (window style = 1)
objShell.Run "python """ & pythonScript & """ """ & configFile & """", 1, True
