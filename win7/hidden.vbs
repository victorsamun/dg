cmdline = WScript.Arguments(0)
for i = 1 to WScript.Arguments.Count - 1
    cmdline = cmdline & " " & WScript.Arguments(i)
next

CreateObject("WScript.Shell").Run cmdline, 0, False
