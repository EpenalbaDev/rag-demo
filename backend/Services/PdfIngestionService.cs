using Microsoft.Extensions.VectorData;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Embeddings;
using RagDemo.Models;
using UglyToad.PdfPig;

namespace RagDemo.Services;

public class PdfIngestionService(Kernel kernel, IVectorStore vectorStore)
{
    private const string COLLECTION = "pdf-knowledge";

    public async Task IngestAllPdfsAsync(string pdfFolderPath)
    {
        var collection = vectorStore.GetCollection<string, TextChunk>(COLLECTION);
        await collection.CreateCollectionIfNotExistsAsync();

        var embeddingService = kernel.GetRequiredService<ITextEmbeddingGenerationService>();

        foreach (var pdfPath in Directory.GetFiles(pdfFolderPath, "*.pdf"))
        {
            var fileName = Path.GetFileName(pdfPath);
            using var pdf = PdfDocument.Open(pdfPath);

            var fullText = string.Join(" ", pdf.GetPages().Select(p => p.Text));
            var chunks = ChunkText(fullText, 600);

            foreach (var (chunk, index) in chunks.Select((c, i) => (c, i)))
            {
                var embedding = await embeddingService.GenerateEmbeddingAsync(chunk);
                await collection.UpsertAsync(new TextChunk
                {
                    Id = $"{fileName}-chunk-{index}",
                    Content = chunk,
                    Source = "pdf",
                    SourceName = fileName,
                    Embedding = embedding
                });
            }

            Console.WriteLine($"[PDF] Indexado: {fileName} ({chunks.Count} chunks)");
        }
    }

    private static List<string> ChunkText(string text, int chunkSize)
    {
        var words = text.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        var chunks = new List<string>();

        for (int i = 0; i < words.Length; i += chunkSize)
            chunks.Add(string.Join(" ", words.Skip(i).Take(chunkSize)));

        return chunks;
    }
}
