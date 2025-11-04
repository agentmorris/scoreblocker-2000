Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Build the command to run
pythonScript = scriptDir & "\launch_monitor.py"
configFile = "configs\monitor2.json"

' Run the Python script without showing a window
objShell.Run "python """ & pythonScript & """ """ & configFile & """", 0, False
