using System.Collections.Concurrent;

namespace RagDemo.Services;

public class RateLimiterService
{
    private const int MAX_REQUESTS = 7;
    private static readonly TimeSpan WINDOW = TimeSpan.FromHours(1);

    private readonly ConcurrentDictionary<string, ClientBucket> _buckets = new();

    public (bool Allowed, int Remaining) Check(string clientIp)
    {
        var bucket = _buckets.GetOrAdd(clientIp, _ => new ClientBucket());

        lock (bucket)
        {
            bucket.Requests.RemoveAll(t => DateTime.UtcNow - t > WINDOW);

            if (bucket.Requests.Count >= MAX_REQUESTS)
                return (false, 0);

            bucket.Requests.Add(DateTime.UtcNow);
            return (true, MAX_REQUESTS - bucket.Requests.Count);
        }
    }

    private class ClientBucket
    {
        public List<DateTime> Requests { get; } = [];
    }
}
