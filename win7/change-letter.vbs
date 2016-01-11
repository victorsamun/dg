if WScript.Arguments.Count <> 2 then
   WScript.StdErr.WriteLine("Usage: " & WScript.ScriptName & " " & _
                            "<label> <new letter>")
   WScript.Quit(1)
end if

label = WScript.Arguments(0)
letter = WScript.Arguments(1)

set wmi = GetObject("winmgmts:{impersonationLevel=Impersonate}!//.")
set volumes = wmi.ExecQuery(_
    "SELECT * from Win32_Volume WHERE Label = '" & label & "'")

if volumes.Count = 0 then
    WScript.StdErr.WriteLine(label & ": no volumes found")
    WScript.Quit(1)
end if

for each volume in volumes
    volume.DriveLetter = letter
    volume.Put_
next
