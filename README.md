# RAG Demo — Inteligencia Documental Financiera

Demo de **Retrieval-Augmented Generation (RAG)** con dos fuentes de conocimiento: documentos PDF y una base de datos PostgreSQL. Permite hacer preguntas en lenguaje natural sobre datos financieros de una empresa ficticia (Grupo Altamira S.A.).

**[Ver demo en vivo](https://calm-tenderness-production.up.railway.app)**

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | .NET 8, ASP.NET Core Web API |
| RAG | Microsoft Semantic Kernel, InMemory Vector Store |
| LLM | OpenAI gpt-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| PDF Parsing | PdfPig |
| Base de datos | PostgreSQL (Npgsql) |
| Frontend | HTML/CSS/JS puro (servido como static files) |
| Deploy | Railway (Dockerfile) |

## Cómo funciona

1. **Ingesta** — Al iniciar, el backend procesa 3 PDFs financieros y consulta las tablas de PostgreSQL. El texto se divide en chunks.
2. **Embeddings** — Cada chunk se convierte en un vector de 1536 dimensiones usando `text-embedding-3-small` y se almacena en un vector store en memoria.
3. **Consulta** — Cuando el usuario hace una pregunta, se vectoriza, se buscan los chunks más similares, y se envían como contexto a `gpt-4o-mini` para generar la respuesta.

## Fuentes de datos

### PDFs (Grupo Altamira S.A.)
- **Reporte Anual 2023** — Ingresos $4.2M, EBITDA $890K, expansión regional
- **Estados Financieros Q3** — Balance general, P&L, ratios financieros
- **Contratos Proveedores** — TechSupply ($240K/año), LogiPanama ($85K/año), OficinaMax ($12K/año)

### PostgreSQL
- 15 clientes ficticios (Panamá, Colombia, Costa Rica)
- 20 facturas con estados variados (pagadas, pendientes, vencidas)
- 10 productos con márgenes del 20% al 80%
- 25 registros de ventas

## Desarrollo local

### Requisitos
- .NET 8 SDK
- PostgreSQL (o connection string a una instancia remota)
- API key de OpenAI

### Setup

```bash
# Clonar
git clone https://github.com/EpenalbaDev/rag-demo.git
cd rag-demo

# Configurar variables
cd backend
cp appsettings.json appsettings.Development.json
# Editar appsettings.Development.json con tu OpenAI key y connection string

# Ejecutar seed SQL en tu PostgreSQL
psql $DATABASE_URL -f Data/seed.sql

# Correr
dotnet run
```

La app estará en `http://localhost:8080`.

### Preguntas de ejemplo

**PDF:**
- "¿Cuál fue el EBITDA en 2023?"
- "¿Qué dice el contrato con TechSupply sobre penalidades?"
- "¿En qué países opera la empresa?"

**PostgreSQL:**
- "¿Clientes con más deuda vencida?"
- "¿Qué producto tiene mejor margen pero menos ventas?"
- "¿Facturas vencidas más de 60 días?"

## Deploy en Railway

1. Push a GitHub
2. En Railway: New Project > Deploy from GitHub
3. Agregar PostgreSQL add-on
4. Configurar variables de entorno:
   - `OPENAI__APIKEY`
   - `ConnectionStrings__PostgreSQL`
   - `PORT=8080`
5. Ejecutar `Data/seed.sql` en la instancia PostgreSQL

## Estructura del proyecto

```
rag-demo/
├── backend/
│   ├── Controllers/        # API endpoints
│   ├── Services/           # RAG, PDF ingestion, PostgreSQL ingestion
│   ├── Models/             # TextChunk, QueryRequest, QueryResponse
│   ├── Data/
│   │   ├── pdfs/           # 3 PDFs demo
│   │   └── seed.sql        # Datos SQL
│   └── Program.cs          # Entry point + DI + startup ingestion
├── frontend/
│   └── index.html          # SPA completa
├── Dockerfile
└── railway.toml
```

## API

### `POST /api/query`
```json
{
  "question": "¿Cuál fue el EBITDA en 2023?",
  "source": "pdf"
}
```
`source`: `"pdf"` o `"postgres"`

### `GET /api/status`
Health check.

## Autor

**Edwin Peñalba** — [epenalba.tech](https://www.epenalba.tech)

## Licencia

MIT
