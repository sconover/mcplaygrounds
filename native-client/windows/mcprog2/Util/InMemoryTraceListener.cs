using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
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
            // cheating with Write implementation, but fine for now I think.
            lines.Enqueue(message);
        }

        public override void WriteLine(string message)
        {
            Write(message);
        }

        public string[] dequeueAll()
        {
            List<string> lineList = new List<string>();
            string line = null;
            if (lines.TryDequeue(out line))
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
