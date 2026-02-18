using Microsoft.AspNetCore.Mvc;
using RagDemo.Models;
using RagDemo.Services;

namespace RagDemo.Controllers;

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
