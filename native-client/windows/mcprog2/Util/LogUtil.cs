using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.IO;
using Microsoft.VisualBasic.Logging;

namespace mcprog2.Util
{
    class LogUtil
    {
        public static TraceListener getAppLogTraceListener()
        {
            string logDir = Path.GetDirectoryName(Process.GetCurrentProcess().MainModule.FileName) + "\\logs";
            FileLogTraceListener fileLogListener = new FileLogTraceListener();
            fileLogListener.BaseFileName = "AppLog";
            fileLogListener.Append = true;
            fileLogListener.IncludeHostName = false;
            fileLogListener.Delimiter = ", ";
            fileLogListener.AutoFlush = true;
            fileLogListener.TraceOutputOptions = TraceOptions.DateTime;

            fileLogListener.Location = LogFileLocation.Custom;
            fileLogListener.CustomLocation = logDir;
            fileLogListener.LogFileCreationSchedule = LogFileCreationScheduleOption.Daily;
            fileLogListener.MaxFileSize = 10 * 1024 * 1024;// 10M
            fileLogListener.DiskSpaceExhaustedBehavior = DiskSpaceExhaustedOption.ThrowException;

            return fileLogListener;
        }
    }
}
