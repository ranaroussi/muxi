# AI Agent Framework Dashboard

A modern web dashboard for interacting with the AI Agent Framework.

## Features

- **Agent Management**: Create, delete, and view details of your AI agents
- **Real-time Chat**: Chat with agents in real-time using WebSockets
- **Memory Search**: Search through an agent's memories
- **Tool Exploration**: See which tools are available to each agent
- **Responsive Design**: Works on desktop and mobile devices

## Technologies Used

- **React**: UI library
- **Chakra UI**: Component library for consistent design
- **React Router**: For navigation
- **Axios**: For API requests
- **WebSocket API**: For real-time communication

## Getting Started

### Prerequisites

- Node.js 14+ and npm
- AI Agent Framework API server running

### Installation

1. Navigate to the web dashboard directory:
   ```bash
   cd src/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (optional):
   ```
   # Replace with your API server's address (IP or FQDN) including the port
   REACT_APP_API_URL=http://localhost:5050

   # Examples:
   # REACT_APP_API_URL=http://192.168.1.100:5050
   # REACT_APP_API_URL=http://api.yourdomain.com:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

The dashboard will be available at http://localhost:3000.

## Building for Production

To build the dashboard for production:

```bash
npm run build
```

This will create a `build` directory with optimized production files.

## Configuration

You can configure the dashboard using the following environment variables:

- `REACT_APP_API_URL`: URL of the AI Agent Framework API (defaults to the same host as the dashboard)

## Deployment

### With the AI Agent Framework

The dashboard can be served by the AI Agent Framework API server. To do this:

1. Build the dashboard:
   ```bash
   npm run build
   ```

2. Copy the contents of the `build` directory to the appropriate location in the API server.

### Standalone Deployment

The dashboard can also be deployed separately using services like:

- Netlify
- Vercel
- GitHub Pages
- Any static file server

## Screenshots

- Dashboard View: A quick overview of your agents and stats
- Chat Interface: Real-time communication with your agents
- Agent Details: View and manage specific agent details and memory

## Development

### Project Structure

```
src/
├── components/    # Reusable UI components
├── hooks/         # Custom React hooks
├── pages/         # Main application pages
├── services/      # API and WebSocket services
├── styles/        # CSS and theme files
└── utils/         # Utility functions
```

### Adding New Features

1. **New Pages**: Add new pages in the `pages` directory and update the routing in `App.js`
2. **API Endpoints**: Add new API endpoints in `services/api.js`
3. **WebSocket Events**: Handle new WebSocket events in `hooks/useWebSocket.js`

## License

This project is part of the AI Agent Framework and is licensed under the same terms.
