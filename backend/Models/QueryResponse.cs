namespace RagDemo.Models;

public record QueryResponse(
    string Answer,
    string Source,
    List<string> SourceChunks,
    int TokensUsed
);
