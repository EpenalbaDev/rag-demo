#pragma warning disable SKEXP0001, SKEXP0010, SKEXP0020, SKEXP0050

using Microsoft.Extensions.VectorData;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.InMemory;
using RagDemo.Services;

var builder = WebApplication.CreateBuilder(args);

// CORS
builder.Services.AddCors(opt => opt.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

// Semantic Kernel
var openAiKey = builder.Configuration["OpenAI:ApiKey"]
    ?? Environment.GetEnvironmentVariable("OPENAI__APIKEY")
    ?? throw new InvalidOperationException("OpenAI:ApiKey no configurado");

var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("gpt-4o-mini", openAiKey)
    .AddOpenAITextEmbeddingGeneration("text-embedding-3-small", openAiKey)
    .Build();

builder.Services.AddSingleton(kernel);
builder.Services.AddSingleton<IVectorStore, InMemoryVectorStore>();
builder.Services.AddScoped<RagService>();
builder.Services.AddScoped<PdfIngestionService>();
builder.Services.AddScoped<PostgresIngestionService>();
builder.Services.AddControllers();

// Servir frontend estático
builder.Services.AddSpaStaticFiles(config => config.RootPath = "frontend");

var app = builder.Build();

app.UseCors();
app.UseStaticFiles();
app.UseSpaStaticFiles();
app.MapControllers();
app.UseSpa(spa => spa.Options.SourcePath = "frontend");

// Auto-ingestar al iniciar
using (var scope = app.Services.CreateScope())
{
    try
    {
        var pdfService = scope.ServiceProvider.GetRequiredService<PdfIngestionService>();
        var pgService  = scope.ServiceProvider.GetRequiredService<PostgresIngestionService>();

        var pdfPath = Path.Combine(AppContext.BaseDirectory, "Data", "pdfs");
        if (Directory.Exists(pdfPath))
            await pdfService.IngestAllPdfsAsync(pdfPath);
        else
            Console.WriteLine($"[WARN] Carpeta PDFs no encontrada: {pdfPath}");

        await pgService.IngestAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"[ERROR] Ingesta inicial falló: {ex.Message}");
    }
}

// Puerto Railway
var port = Environment.GetEnvironmentVariable("PORT") ?? "8080";
app.Run($"http://0.0.0.0:{port}");
