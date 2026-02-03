' Запуск Pomodoro без окна CMD (через pythonw)
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = scriptDir
shell.Environment("Process")("PYTHONPATH") = scriptDir & "\src"
shell.Run "pythonw -m pomodoro", 1, False
