Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Build the command to run
pythonScript = scriptDir & "\score_blocker.py"

' Run the close_all command without showing a window
objShell.Run "python """ & pythonScript & """ --close_all", 0, True
