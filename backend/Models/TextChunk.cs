using Microsoft.Extensions.VectorData;

namespace RagDemo.Models;

public class TextChunk
{
    [VectorStoreRecordKey]
    public string Id { get; set; } = Guid.NewGuid().ToString();

    [VectorStoreRecordData]
    public string Content { get; set; } = string.Empty;

    [VectorStoreRecordData]
    public string Source { get; set; } = string.Empty;

    [VectorStoreRecordData]
    public string SourceName { get; set; } = string.Empty;

    [VectorStoreRecordVector(1536)]
    public ReadOnlyMemory<float> Embedding { get; set; }
}
