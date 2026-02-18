using Microsoft.AspNetCore.Mvc;
using RagDemo.Models;
using RagDemo.Services;

namespace RagDemo.Controllers;

[ApiController]
[Route("api")]
public class QueryController(RagService ragService, RateLimiterService rateLimiter) : ControllerBase
{
    [HttpPost("query")]
    public async Task<IActionResult> Query([FromBody] QueryRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Question))
            return BadRequest("Question is required");

        if (request.Source != "pdf" && request.Source != "postgres")
            return BadRequest("Source must be 'pdf' or 'postgres'");

        var clientIp = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown";
        var (allowed, remaining) = rateLimiter.Check(clientIp);

        Response.Headers["X-RateLimit-Remaining"] = remaining.ToString();

        if (!allowed)
            return StatusCode(429, new { error = "Has alcanzado el límite de 7 consultas por hora. Vuelve más tarde." });

        var response = await ragService.QueryAsync(request);
        return Ok(response);
    }
}
