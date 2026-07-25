# Smart Home MCP Server

A Model Context Protocol (MCP) server for controlling Tuya-compatible smart home devices locally using Python's `tinytuya` library.

## Setup

1. Install Node.js dependencies (this will automatically configure the Python environment and install `tinytuya` and the `mcp` SDK using `uv`):
   ```bash
   npm install
   ```

2. Copy the example environment file and fill in your Tuya credentials:
   ```bash
   cp .env.example .env
   ```

3. Run the server:
   ```bash
   npm start
   ```

4. Run tests:
   ```bash
   npm test
   ```
