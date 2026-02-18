using Microsoft.Extensions.VectorData;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Embeddings;
using RagDemo.Models;

namespace RagDemo.Services;

public class RagService(Kernel kernel, IVectorStore vectorStore)
{
    private const string PDF_COLLECTION = "pdf-knowledge";
    private const string PG_COLLECTION = "postgres-knowledge";

    public async Task<QueryResponse> QueryAsync(QueryRequest request)
    {
        var collectionName = request.Source == "pdf" ? PDF_COLLECTION : PG_COLLECTION;

        var embeddingService = kernel.GetRequiredService<ITextEmbeddingGenerationService>();
        var questionEmbedding = await embeddingService.GenerateEmbeddingAsync(request.Question);

        var collection = vectorStore.GetCollection<string, TextChunk>(collectionName);
        var searchResults = await collection.VectorizedSearchAsync(questionEmbedding, new() { Top = 4 });

        var chunks = new List<string>();
        await foreach (var result in searchResults.Results)
            chunks.Add(result.Record.Content);

        var context = string.Join("\n\n---\n\n", chunks);
        var systemPrompt = request.Source == "pdf"
            ? "Eres un analista financiero experto. Responde SOLO basándote en los documentos proporcionados. Si la información no está en los documentos, dilo claramente. Responde en español, de forma concisa y profesional."
            : "Eres un analista de datos experto. Responde SOLO basándote en los datos de la base de datos proporcionados. Incluye números específicos cuando estén disponibles. Responde en español, de forma concisa y profesional.";

        var prompt = $"""
            {systemPrompt}

            CONTEXTO DISPONIBLE:
            {context}

            PREGUNTA: {request.Question}

            RESPUESTA:
            """;

        var chatService = kernel.GetRequiredService<IChatCompletionService>();
        var response = await chatService.GetChatMessageContentAsync(prompt);

        return new QueryResponse(
            Answer: response.Content ?? "No se pudo generar respuesta.",
            Source: request.Source,
            SourceChunks: chunks,
            TokensUsed: 0
        );
    }
}
