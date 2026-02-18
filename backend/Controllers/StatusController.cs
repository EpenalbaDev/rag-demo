using Microsoft.AspNetCore.Mvc;

namespace RagDemo.Controllers;

[ApiController]
[Route("api")]
public class StatusController : ControllerBase
{
    [HttpGet("status")]
    public IActionResult Status() => Ok(new { status = "ok", timestamp = DateTime.UtcNow });
}
