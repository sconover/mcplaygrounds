using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Diagnostics;

namespace mcprog2.Util
{
    class InMemoryTraceListener : TraceListener
    {
        private ConcurrentQueue<string> lines;

        public InMemoryTraceListener()
        {
            lines = new ConcurrentQueue<string>();
        }

        public override void Write(string message)
        {
            lines.Enqueue(message);
        }

        public override void WriteLine(string message)
        {
            lines.Enqueue(message + "\n");
        }

        public string[] dequeueAll()
        {
            List<string> lineList = new List<string>();
            string line = null;
            while (lines.TryDequeue(out line))
            {
                if (line != null)
                {
                    lineList.Add(line);
                }
            };
            return lineList.ToArray();
        }
    }
}
