from fastmcp import FastMCP

mcp = FastMCP(
    "Admin backend",
    instructions="""
    This server provides functionality for the admin backend.
    """
)

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Retrieves a user's profile by ID."""
    # TODO: Implement this
    return {}

@mcp.resource("users://{user_id}/orders")
def get_user_orders(user_id: int) -> dict:
    """Retrieves a user's orders by ID."""
    # TODO: Implement this
    return {}

@mcp.tool()
def search_users(query: str) -> dict:
    """Searches for users by name or email."""
    # TODO: Implement this
    return []

@mcp.tool()
async def send_password_reset_email(email: str) -> str:
    """Send a password reset email"""
    # TODO: Implement this
    return "Password reset email sent"

if __name__ == "__main__":
    mcp.run()
