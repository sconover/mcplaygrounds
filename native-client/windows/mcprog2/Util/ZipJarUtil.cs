using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.IO.Compression;
using System.IO;

namespace mcprog2.Util
{
    class ZipJarUtil
    {
        public static void unzipArchivesToDir(string[] zipArchivePaths, string extractDir)
        {
            extractDir = GlobalSettings.substitute(extractDir);
            System.IO.Directory.CreateDirectory(extractDir);
            foreach (string zipArchivePath in zipArchivePaths)
            {
                string fullZipArchivePath = GlobalSettings.substitute(zipArchivePath);
                Console.WriteLine("extract zip archive: " + fullZipArchivePath);
                Contract.Requires(File.Exists(fullZipArchivePath), "file not found: " + fullZipArchivePath);
                unzip(fullZipArchivePath, extractDir);
            }
        }

        private static void unzip(string zipFilePath, string extractDir)
        {
            ZipStorer zip = ZipStorer.Open(zipFilePath, FileAccess.Read);
            List<ZipStorer.ZipFileEntry> entries = zip.ReadCentralDir();
            foreach (ZipStorer.ZipFileEntry entry in entries)
            {
                string destPath = extractDir + "\\" + entry.FilenameInZip;
                Console.WriteLine("unzip from archive '" + zipFilePath + "' to '" + destPath + "'");
                zip.ExtractFile(entry, destPath);
            }
            zip.Close();
        }
    }
}
