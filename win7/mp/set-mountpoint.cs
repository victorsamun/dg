using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

class VolumeAPI {
    public const Int32 MAX_LENGTH = 1024;

    [DllImport("kernel32", EntryPoint="FindFirstVolume", SetLastError=true)]
    public static extern int FindFirstVolume(
        StringBuilder name, int nameLength);

    [DllImport("kernel32", EntryPoint="FindNextVolume", SetLastError=true)]
    public static extern bool FindNextVolume(
        int handle, StringBuilder name, int nameLength);

    [DllImport("kernel32", EntryPoint="GetVolumePathNamesForVolumeName",
     SetLastError=true)]
    unsafe public static extern bool GetVolumePathNamesForVolumeName(
        string volume, byte* paths, int pathsLength, out int pathsActualLength);

    [DllImport("kernel32", EntryPoint="GetVolumeInformation",
     SetLastError=true)]
    public static extern bool GetVolumeInformation(
        string path, StringBuilder name, int nameLength,
        out int serial, out int maxComponentLength, out int fileSystemFlags,
        StringBuilder fileSystemName, int fileSystemNameLength);

    [DllImport("kernel32", EntryPoint="DeleteVolumeMountPoint",
     SetLastError=true)]
    public static extern bool DeleteVolumeMountPoint(string mountPoint);

    [DllImport("kernel32", EntryPoint="SetVolumeMountPoint", SetLastError=true)]
    public static extern bool SetVolumeMountPoint(
        string mountPoint, string volume);
}

class VolumeUtils {
    public static List<string> GetVolumeNames() {
        StringBuilder name = new StringBuilder(VolumeAPI.MAX_LENGTH);
        List<string> names = new List<string>();
        int handle = VolumeAPI.FindFirstVolume(name, VolumeAPI.MAX_LENGTH);
        do {
            names.Add(name.ToString());
        } while (VolumeAPI.FindNextVolume(handle, name, VolumeAPI.MAX_LENGTH));
        return names;
    }

    static List<string> ParseRawPaths(byte[] raw_paths, int length) {
        List<string> paths = new List<string>();
        for (int ptr = 0, len; raw_paths[ptr] != 0; ptr += len + 1) {
            len = 0;
            while (raw_paths[ptr+len] != 0)
                ++len;
            paths.Add(Encoding.Default.GetString(
                raw_paths.Skip(ptr).Take(len).ToArray()));
        }
        return paths;
    }

    public static List<string> GetVolumePaths(string volume) {
        byte[] raw_paths = new byte[VolumeAPI.MAX_LENGTH];
        int actualLength;
        bool rv = false;
        unsafe {
            fixed (byte* paths_ptr = raw_paths) {
                rv = VolumeAPI.GetVolumePathNamesForVolumeName(
                    volume, paths_ptr, raw_paths.Length, out actualLength);
            }
        }
        return rv ? ParseRawPaths(raw_paths, actualLength) : null;
    }

    public static string GetVolumeLabel(string volume) {
        int unused;
        StringBuilder label = new StringBuilder(VolumeAPI.MAX_LENGTH);
        bool rv = VolumeAPI.GetVolumeInformation(
            volume, label, VolumeAPI.MAX_LENGTH,
            out unused, out unused, out unused, null, 0);
        return rv ? label.ToString() : null;
    }

    public static bool DeleteAllVolumePaths(string volume) {
        List<string> paths = GetVolumePaths(volume);
        if (paths == null)
            return false;

        foreach (string path in paths)
            if (!VolumeAPI.DeleteVolumeMountPoint(path))
                return false;
        return true;
    }
}

class Program {
    public static int Main(string[] args) {
        if (args.Length != 2) {
            Console.Error.WriteLine("Usage: {0} <label> <mount point>",
                                    Process.GetCurrentProcess().ProcessName);
            return 1;
        }
        string label = args[0], point = args[1];

        List<string> volumes = VolumeUtils.GetVolumeNames();
        List<string> matchingVolumes = volumes.Where(
            volume => VolumeUtils.GetVolumeLabel(volume) == label).ToList();
        if (matchingVolumes.Count == 1) {
            string volume = matchingVolumes[0];
            return VolumeUtils.DeleteAllVolumePaths(volume) &&
                   VolumeAPI.SetVolumeMountPoint(point, volume) ? 0 : 3;
        } else {
            Console.Error.WriteLine(
                "Should be exactly one volume with label '{0}', got {1}",
                label, matchingVolumes.Count);
            return 2;
        }
    }
}
