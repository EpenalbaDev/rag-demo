using Microsoft.Extensions.VectorData;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Embeddings;
using Npgsql;
using RagDemo.Models;

namespace RagDemo.Services;

public class PostgresIngestionService(Kernel kernel, IVectorStore vectorStore, IConfiguration config)
{
    private const string COLLECTION = "postgres-knowledge";

    public async Task IngestAsync()
    {
        var connString = config.GetConnectionString("PostgreSQL");
        if (string.IsNullOrEmpty(connString))
        {
            Console.WriteLine("[PostgreSQL] Connection string no configurada, saltando ingesta.");
            return;
        }

        var collection = vectorStore.GetCollection<string, TextChunk>(COLLECTION);
        await collection.CreateCollectionIfNotExistsAsync();

        var embeddingService = kernel.GetRequiredService<ITextEmbeddingGenerationService>();

        await using var conn = new NpgsqlConnection(connString);
        await conn.OpenAsync();

        await IngestTableAsync(conn, embeddingService, collection, "clientes",
            "SELECT id, nombre, segmento, pais, limite_credito FROM clientes");

        await IngestTableAsync(conn, embeddingService, collection, "facturas",
            """
            SELECT f.id, c.nombre as cliente, f.monto, f.fecha, f.estado, f.dias_vencida
            FROM facturas f JOIN clientes c ON f.cliente_id = c.id
            """);

        await IngestTableAsync(conn, embeddingService, collection, "ventas_resumen",
            """
            SELECT p.nombre as producto, p.categoria, p.margen,
                   SUM(v.cantidad) as total_vendido,
                   SUM(v.cantidad * p.precio) as revenue
            FROM ventas v JOIN productos p ON v.producto_id = p.id
            GROUP BY p.id, p.nombre, p.categoria, p.margen
            ORDER BY revenue DESC
            """);

        Console.WriteLine("[PostgreSQL] Ingesta completada");
    }

    private static async Task IngestTableAsync(
        NpgsqlConnection conn,
        ITextEmbeddingGenerationService embeddings,
        IVectorStoreRecordCollection<string, TextChunk> collection,
        string tableName,
        string query)
    {
        await using var cmd = new NpgsqlCommand(query, conn);
        await using var reader = await cmd.ExecuteReaderAsync();

        var rows = new List<string>();
        while (await reader.ReadAsync())
        {
            var parts = new List<string>();
            for (int i = 0; i < reader.FieldCount; i++)
                parts.Add($"{reader.GetName(i)}: {reader.GetValue(i)}");
            rows.Add(string.Join(", ", parts));
        }

        const int rowsPerChunk = 20;
        for (int i = 0; i < rows.Count; i += rowsPerChunk)
        {
            var chunkRows = rows.Skip(i).Take(rowsPerChunk).ToList();
            var chunkText = $"Tabla {tableName}:\n" + string.Join("\n", chunkRows);
            var embedding = await embeddings.GenerateEmbeddingAsync(chunkText);

            await collection.UpsertAsync(new TextChunk
            {
                Id = $"{tableName}-chunk-{i / rowsPerChunk}",
                Content = chunkText,
                Source = "postgres",
                SourceName = tableName,
                Embedding = embedding
            });
        }
    }
}
