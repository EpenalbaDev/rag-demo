# RAG Demo — Inteligencia Documental Financiera
## Guía completa para Claude Code

---

## CONTEXTO DEL PROYECTO

Demo pública de RAG (Retrieval-Augmented Generation) con dos fuentes de conocimiento:
1. **PDFs** — Documentos financieros de empresa ficticia "Grupo Altamira S.A."
2. **PostgreSQL** — Base de datos operacional con clientes, facturas, productos, ventas

**Objetivo**: Página demo de una sola pantalla con dos chats side-by-side que demuestre a empresas el poder de RAG. Será parte del portafolio de Edwin + base para un blog post.

**Deploy**: Railway (backend .NET + frontend estático servido por el mismo backend)

---

## STACK TÉCNICO

### Backend
- .NET 8 ASP.NET Core Web API
- Microsoft.SemanticKernel (RAG orquestación)
- Microsoft.SemanticKernel.Connectors.InMemory (vector store para demo)
- PdfPig (extracción texto PDF)
- Npgsql (conexión PostgreSQL)
- OpenAI API (embeddings: text-embedding-3-small, LLM: gpt-4o-mini)

### Frontend
- HTML/CSS/JS puro (sin framework) — servido como static files desde el backend
- Una sola página (index.html)
- Diseño: oscuro, elegante, financiero — NO genérico

### Base de Datos
- PostgreSQL (Railway add-on)
- Datos ficticios pero realistas de empresa panameña

---

## ESTRUCTURA DE CARPETAS

```
rag-demo/
├── CLAUDE.md                    ← Este archivo
├── README.md
├── .gitignore
├── railway.toml                 ← Config deploy Railway
├── backend/
│   ├── RagDemo.csproj
│   ├── Program.cs
│   ├── Dockerfile
│   ├── appsettings.json
│   ├── appsettings.Development.json
│   ├── Controllers/
│   │   ├── QueryController.cs   ← POST /api/query
│   │   └── StatusController.cs  ← GET /api/status
│   ├── Services/
│   │   ├── RagService.cs        ← Orquestación principal
│   │   ├── PdfIngestionService.cs
│   │   ├── PostgresIngestionService.cs
│   │   └── EmbeddingService.cs
│   ├── Models/
│   │   ├── QueryRequest.cs
│   │   ├── QueryResponse.cs
│   │   └── TextChunk.cs
│   └── Data/
│       ├── pdfs/                ← 3 PDFs ficticios pre-generados
│       │   ├── reporte_anual_2023.pdf
│       │   ├── estados_financieros_Q3.pdf
│       │   └── contratos_proveedores.pdf
│       └── seed.sql             ← Script SQL datos demo
└── frontend/
    ├── index.html               ← Todo el frontend en un archivo
    └── assets/
        └── pdf-previews/        ← Imágenes preview de los PDFs
```

---

## FASE 1 — BACKEND CORE

### 1.1 Setup del proyecto

```bash
cd backend
dotnet new webapi -n RagDemo --no-https
dotnet add package Microsoft.SemanticKernel --version 1.21.0
dotnet add package Microsoft.SemanticKernel.Connectors.InMemory --version 1.21.0
dotnet add package PdfPig --version 0.1.9
dotnet add package Npgsql --version 8.0.3
```

### 1.2 Program.cs — configuración mínima funcional

```csharp
var builder = WebApplication.CreateBuilder(args);

// CORS para desarrollo local
builder.Services.AddCors(opt => opt.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

// Semantic Kernel
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("gpt-4o-mini", builder.Configuration["OpenAI:ApiKey"]!)
    .AddOpenAITextEmbeddingGeneration("text-embedding-3-small", builder.Configuration["OpenAI:ApiKey"]!)
    .Build();

builder.Services.AddSingleton(kernel);
builder.Services.AddSingleton<IVectorStore, InMemoryVectorStore>();
builder.Services.AddScoped<RagService>();
builder.Services.AddScoped<PdfIngestionService>();
builder.Services.AddScoped<PostgresIngestionService>();
builder.Services.AddControllers();

// Servir frontend estático
builder.Services.AddSpaStaticFiles(config => config.RootPath = "../frontend");

var app = builder.Build();

app.UseCors();
app.UseStaticFiles();
app.UseSpaStaticFiles();
app.MapControllers();
app.UseSpa(spa => spa.Options.SourcePath = "../frontend");

// Puerto Railway
var port = Environment.GetEnvironmentVariable("PORT") ?? "8080";
app.Run($"http://0.0.0.0:{port}");
```

### 1.3 Modelos

```csharp
// Models/TextChunk.cs
public class TextChunk
{
    [VectorStoreRecordKey]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [VectorStoreRecordData]
    public string Content { get; set; } = string.Empty;
    
    [VectorStoreRecordData]
    public string Source { get; set; } = string.Empty; // "pdf" | "postgres"
    
    [VectorStoreRecordData]
    public string SourceName { get; set; } = string.Empty; // nombre del archivo o tabla
    
    [VectorStoreRecordVector(1536)] // dimensiones text-embedding-3-small
    public ReadOnlyMemory<float> Embedding { get; set; }
}

// Models/QueryRequest.cs
public record QueryRequest(string Question, string Source); // Source: "pdf" | "postgres"

// Models/QueryResponse.cs
public record QueryResponse(
    string Answer,
    string Source,
    List<string> SourceChunks, // para mostrar en UI qué fragmentos usó
    int TokensUsed
);
```

### 1.4 RagService — lógica principal

```csharp
public class RagService(Kernel kernel, IVectorStore vectorStore)
{
    private const string PDF_COLLECTION = "pdf-knowledge";
    private const string PG_COLLECTION  = "postgres-knowledge";

    public async Task<QueryResponse> QueryAsync(QueryRequest request)
    {
        var collectionName = request.Source == "pdf" ? PDF_COLLECTION : PG_COLLECTION;
        
        // 1. Generar embedding de la pregunta
        var embeddingService = kernel.GetRequiredService<ITextEmbeddingGenerationService>();
        var questionEmbedding = await embeddingService.GenerateEmbeddingAsync(request.Question);
        
        // 2. Buscar chunks relevantes
        var collection = vectorStore.GetCollection<string, TextChunk>(collectionName);
        var searchResults = await collection.VectorizedSearchAsync(questionEmbedding, new() { Top = 4 });
        
        var chunks = new List<string>();
        await foreach (var result in searchResults.Results)
            chunks.Add(result.Record.Content);
        
        // 3. Construir prompt con contexto
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
        
        // 4. Generar respuesta
        var chatService = kernel.GetRequiredService<IChatCompletionService>();
        var response = await chatService.GetChatMessageContentAsync(prompt);
        
        return new QueryResponse(
            Answer: response.Content ?? "No se pudo generar respuesta.",
            Source: request.Source,
            SourceChunks: chunks,
            TokensUsed: 0 // opcional: implementar conteo
        );
    }
    
    public async Task<(int PdfChunks, int PostgresChunks)> GetStatusAsync()
    {
        // Retorna cuántos chunks hay en cada colección
        // Implementar según necesidad
        return (0, 0);
    }
}
```

### 1.5 PdfIngestionService

```csharp
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
            var chunks = ChunkText(fullText, 600); // ~600 palabras por chunk
            
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
```

### 1.6 PostgresIngestionService

```csharp
public class PostgresIngestionService(Kernel kernel, IVectorStore vectorStore, IConfiguration config)
{
    private const string COLLECTION = "postgres-knowledge";
    
    public async Task IngestAsync()
    {
        var collection = vectorStore.GetCollection<string, TextChunk>(COLLECTION);
        await collection.CreateCollectionIfNotExistsAsync();
        
        var embeddingService = kernel.GetRequiredService<ITextEmbeddingGenerationService>();
        var connString = config.GetConnectionString("PostgreSQL");
        
        await using var conn = new NpgsqlConnection(connString);
        await conn.OpenAsync();
        
        // Ingestar cada tabla como chunks de texto
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
        
        // Agrupar filas en chunks de ~20 filas cada uno
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
```

### 1.7 Controllers

```csharp
// Controllers/QueryController.cs
[ApiController]
[Route("api")]
public class QueryController(RagService ragService) : ControllerBase
{
    [HttpPost("query")]
    public async Task<IActionResult> Query([FromBody] QueryRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Question))
            return BadRequest("Question is required");
            
        if (request.Source != "pdf" && request.Source != "postgres")
            return BadRequest("Source must be 'pdf' or 'postgres'");
        
        var response = await ragService.QueryAsync(request);
        return Ok(response);
    }
}

// Controllers/StatusController.cs
[ApiController]
[Route("api")]
public class StatusController : ControllerBase
{
    [HttpGet("status")]
    public IActionResult Status() => Ok(new { status = "ok", timestamp = DateTime.UtcNow });
}
```

---

## FASE 2 — DATOS DEMO

### 2.1 Contenido de los 3 PDFs (generar con script)

Crear `Data/generate_pdfs.py` (o hacerlo manualmente con Word/LibreOffice):

**PDF 1: reporte_anual_2023.pdf**
- Resumen ejecutivo Grupo Altamira S.A.
- Ingresos: $4.2M (+18% vs 2022)
- EBITDA: $890K (margen 21.2%)
- Segmentos: Retail 60%, Corporativo 40%
- Expansión a Colombia en Q4

**PDF 2: estados_financieros_Q3.pdf**  
- Balance General al 30-Sep-2023
- Activos: $8.1M, Pasivos: $3.2M, Patrimonio: $4.9M
- P&L Q3: Ingresos $1.1M, COGS $650K, Utilidad Neta $180K
- Ratio deuda/equity: 0.65

**PDF 3: contratos_proveedores.pdf**
- Contrato Proveedor TechSupply Corp: $240K/año, vigente hasta Dic 2024, penalidad 15% por incumplimiento
- Contrato LogiPanama S.A.: $85K/año, exclusividad zona Pacífico
- Contrato OficinaMax: $12K/año, renovación automática

### 2.2 Script SQL seed

Ver archivo `Data/seed.sql` — incluye:
- 15 clientes ficticios panameños
- 80 facturas con estados variados
- 10 productos con márgenes diferentes
- 150 registros de ventas

---

## FASE 3 — FRONTEND

### 3.1 Diseño

**Estética**: Financiero premium, tema oscuro
- Background: `#0a0e1a` (azul marino muy oscuro)
- Accent: `#00d4aa` (verde-cyan para datos/success)
- Accent2: `#f59e0b` (ámbar para PDF/documentos)
- Font display: "DM Serif Display" (Google Fonts)
- Font body: "DM Mono" (monoespaciado para datos)

**Secciones de la página** (scroll vertical):

1. **Hero** — Título + subtítulo animado
2. **Demo Split** — Dos chats side-by-side (SECCIÓN PRINCIPAL)
3. **Fuentes** — PDFs preview (izquierda) + Tabla preview (derecha)
4. **CTA** — "¿Quieres esto para tu empresa?" → link contacto

### 3.2 Funcionalidad JS del chat

```javascript
async function sendQuery(question, source) {
    const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, source })
    });
    const data = await response.json();
    return data.answer;
}
```

### 3.3 Suggested questions (chips clicables)

**Para PDF:**
- "¿Cuál fue el EBITDA del año 2023?"
- "¿Qué dice el contrato con TechSupply sobre penalidades?"
- "¿En qué países está operando la empresa?"

**Para PostgreSQL:**
- "¿Cuáles son los 3 clientes con más deuda vencida?"
- "¿Qué producto tiene el mejor margen pero menos ventas?"
- "¿Cuántas facturas están vencidas más de 30 días?"

---

## FASE 4 — DATOS SEED SQL

```sql
-- seed.sql
-- Ejecutar en Railway PostgreSQL

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    segmento VARCHAR(50), -- 'Corporativo', 'PYME', 'Retail'
    pais VARCHAR(50) DEFAULT 'Panamá',
    limite_credito DECIMAL(12,2),
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    precio DECIMAL(10,2),
    costo DECIMAL(10,2),
    margen DECIMAL(5,2) -- porcentaje
);

CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(id),
    monto DECIMAL(12,2),
    fecha DATE,
    fecha_vencimiento DATE,
    estado VARCHAR(20), -- 'pagada', 'pendiente', 'vencida'
    dias_vencida INT DEFAULT 0
);

CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    cliente_id INT REFERENCES clientes(id),
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    fecha DATE
);

-- CLIENTES
INSERT INTO clientes (nombre, segmento, pais, limite_credito) VALUES
('Grupo Torre Alta S.A.', 'Corporativo', 'Panamá', 500000),
('Constructora Pacífico', 'Corporativo', 'Panamá', 350000),
('Farmacia San Judas', 'PYME', 'Panamá', 50000),
('Distribuidora El Volcán', 'PYME', 'Panamá', 80000),
('Hotel Miramar', 'Corporativo', 'Panamá', 200000),
('Supermercados Riba Smith', 'Corporativo', 'Panamá', 450000),
('Clínica Santa Fe', 'PYME', 'Panamá', 120000),
('Tecnología Avanzada S.A.', 'Corporativo', 'Panamá', 300000),
('Importadora Los Andes', 'PYME', 'Colombia', 90000),
('Servicios Globales CR', 'PYME', 'Costa Rica', 70000),
('Banco Regional S.A.', 'Corporativo', 'Panamá', 800000),
('Seguros del Istmo', 'Corporativo', 'Panamá', 600000),
('Restaurantes La Plaza', 'PYME', 'Panamá', 40000),
('Logística Ágil S.A.', 'PYME', 'Panamá', 110000),
('Editorial Centroamérica', 'PYME', 'Panamá', 30000);

-- PRODUCTOS
INSERT INTO productos (nombre, categoria, precio, costo, margen) VALUES
('Software ERP Básico', 'Software', 4500.00, 900.00, 80.00),
('Software ERP Empresarial', 'Software', 12000.00, 2400.00, 80.00),
('Consultoría Implementación', 'Servicios', 8000.00, 3200.00, 60.00),
('Soporte Anual Premium', 'Servicios', 3600.00, 720.00, 80.00),
('Soporte Anual Básico', 'Servicios', 1200.00, 360.00, 70.00),
('Hardware Servidor Dell', 'Hardware', 6500.00, 5200.00, 20.00),
('Licencias Microsoft 365', 'Software', 180.00, 120.00, 33.00),
('Capacitación Usuarios', 'Servicios', 2500.00, 800.00, 68.00),
('Módulo RRHH Add-on', 'Software', 2200.00, 440.00, 80.00),
('Módulo Inventario Add-on', 'Software', 1800.00, 360.00, 80.00);

-- FACTURAS (mezcla de estados)
INSERT INTO facturas (cliente_id, monto, fecha, fecha_vencimiento, estado, dias_vencida) VALUES
(1, 12000.00, '2023-10-01', '2023-11-01', 'pagada', 0),
(1, 3600.00, '2023-11-15', '2023-12-15', 'vencida', 62),
(2, 8000.00, '2023-09-01', '2023-10-01', 'pagada', 0),
(2, 6500.00, '2023-12-01', '2024-01-01', 'vencida', 46),
(3, 1200.00, '2023-11-01', '2023-12-01', 'pendiente', 0),
(4, 4500.00, '2023-10-15', '2023-11-15', 'vencida', 62),
(4, 2200.00, '2023-12-15', '2024-01-15', 'pendiente', 0),
(5, 12000.00, '2023-08-01', '2023-09-01', 'pagada', 0),
(5, 3600.00, '2023-12-01', '2024-01-01', 'vencida', 46),
(6, 8000.00, '2023-11-01', '2023-12-01', 'pagada', 0),
(6, 1800.00, '2024-01-05', '2024-02-05', 'pendiente', 0),
(7, 4500.00, '2023-10-01', '2023-11-01', 'vencida', 92),
(8, 12000.00, '2023-12-01', '2024-01-01', 'pendiente', 0),
(9, 2500.00, '2023-11-15', '2023-12-15', 'vencida', 47),
(10, 1200.00, '2024-01-10', '2024-02-10', 'pendiente', 0),
(11, 12000.00, '2023-09-01', '2023-10-01', 'pagada', 0),
(11, 8000.00, '2023-12-01', '2024-01-01', 'pagada', 0),
(12, 3600.00, '2023-11-01', '2023-12-01', 'vencida', 77),
(13, 1200.00, '2023-10-01', '2023-11-01', 'vencida', 91),
(14, 4500.00, '2024-01-01', '2024-02-01', 'pendiente', 0);

-- VENTAS
INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, fecha) VALUES
(2, 1, 1, 12000.00, '2023-10-01'),
(4, 1, 1, 3600.00, '2023-11-15'),
(3, 2, 1, 8000.00, '2023-09-01'),
(6, 2, 1, 6500.00, '2023-12-01'),
(5, 3, 1, 1200.00, '2023-11-01'),
(1, 4, 1, 4500.00, '2023-10-15'),
(9, 4, 1, 2200.00, '2023-12-15'),
(2, 5, 1, 12000.00, '2023-08-01'),
(4, 5, 1, 3600.00, '2023-12-01'),
(3, 6, 1, 8000.00, '2023-11-01'),
(10, 6, 1, 1800.00, '2024-01-05'),
(1, 7, 1, 4500.00, '2023-10-01'),
(2, 8, 1, 12000.00, '2023-12-01'),
(8, 9, 1, 2500.00, '2023-11-15'),
(5, 10, 1, 1200.00, '2024-01-10'),
(2, 11, 1, 12000.00, '2023-09-01'),
(3, 11, 1, 8000.00, '2023-12-01'),
(4, 12, 1, 3600.00, '2023-11-01'),
(5, 13, 1, 1200.00, '2023-10-01'),
(1, 14, 1, 4500.00, '2024-01-01'),
(7, 1, 25, 180.00, '2023-10-01'),
(7, 5, 50, 180.00, '2023-08-01'),
(7, 11, 100, 180.00, '2023-09-01'),
(8, 2, 1, 2500.00, '2023-09-15'),
(8, 6, 1, 2500.00, '2023-11-20');
```

---

## FASE 5 — DEPLOY RAILWAY

### 5.1 Dockerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY backend/ .
RUN dotnet publish RagDemo.csproj -c Release -o /app/publish

FROM base AS final
COPY --from=build /app/publish .
COPY frontend/ ./frontend/
ENTRYPOINT ["dotnet", "RagDemo.dll"]
```

### 5.2 railway.toml

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "on_failure"
```

### 5.3 Variables de entorno en Railway

```
OPENAI__APIKEY=sk-...
ConnectionStrings__PostgreSQL=Host=...;Database=...;Username=...;Password=...
PORT=8080
```

### 5.4 Proceso de deploy

1. `git init && git add . && git commit -m "initial"`
2. Push a GitHub
3. En Railway: New Project → Deploy from GitHub
4. Add PostgreSQL add-on
5. Configurar variables de entorno
6. Deploy automático

---

## FASE 6 — INICIALIZACIÓN EN STARTUP

En `Program.cs`, después de `app.Build()`:

```csharp
// Auto-ingestar al iniciar
using (var scope = app.Services.CreateScope())
{
    var pdfService = scope.ServiceProvider.GetRequiredService<PdfIngestionService>();
    var pgService = scope.ServiceProvider.GetRequiredService<PostgresIngestionService>();
    
    var pdfPath = Path.Combine(AppContext.BaseDirectory, "Data", "pdfs");
    await pdfService.IngestAllPdfsAsync(pdfPath);
    await pgService.IngestAsync();
}
```

---

## CHECKLIST FINAL

### Backend
- [ ] `dotnet build` sin errores
- [ ] PDF ingesta correcta (ver logs "Indexado: X chunks")
- [ ] PostgreSQL ingesta correcta
- [ ] `POST /api/query` con source "pdf" responde correctamente
- [ ] `POST /api/query` con source "postgres" responde correctamente
- [ ] Frontend se sirve en `/`

### Frontend
- [ ] Dos chats funcionales
- [ ] Chips de preguntas sugeridas funcionan
- [ ] Previews de PDFs visibles
- [ ] Preview tabla de datos visible
- [ ] Responsive en mobile

### Deploy
- [ ] Dockerfile construye sin errores
- [ ] Variables de entorno configuradas en Railway
- [ ] URL pública accesible
- [ ] Ingesta automática al iniciar (ver logs Railway)

---

## NOTAS IMPORTANTES

1. **InMemoryVectorStore** se resetea en cada deploy — es intencional para demo, por eso la ingesta automática en startup
2. Los PDFs deben estar en `backend/Data/pdfs/` y se incluyen en el build via `.csproj`
3. El frontend se sirve como SPA estática desde el backend — no necesitas servidor separado
4. Para el blog: captura screenshots de las respuestas a las preguntas "wow" antes de publicar

---

## COMANDOS ÚTILES

```bash
# Desarrollo local
cd backend && dotnet run

# Ver logs Railway
railway logs

# Conectar a PostgreSQL Railway local
railway connect PostgreSQL

# Ejecutar seed
railway run psql $DATABASE_URL -f Data/seed.sql
```