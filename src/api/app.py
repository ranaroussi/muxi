"""
API server for the AI Agent Framework.

This module provides a FastAPI-based API server for interacting with
agents created with the AI Agent Framework.
"""

import logging
import os
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.llm import OpenAILLM
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase
from src.core.orchestrator import Orchestrator
from src.tools.web_search import WebSearch
from src.tools.calculator import Calculator
from src.config import config
from src.api.websocket import register_websocket_routes
from src.utils import get_version


# Load environment variables
load_dotenv()

# Create orchestrator as a global variable
orchestrator = Orchestrator()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")


# Define API models
class AgentRequest(BaseModel):
    """Model for creating an agent."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    llm_model: str = Field(
        config.llm.default_model,
        description="LLM model to use (e.g., gpt-4o)"
    )
    system_message: Optional[str] = Field(
        None,
        description="System message to customize agent behavior"
    )
    enable_web_search: bool = Field(
        config.tools.enable_web_search,
        description="Whether to enable web search"
    )
    enable_calculator: bool = Field(
        config.tools.enable_calculator,
        description="Whether to enable calculator"
    )
    use_long_term_memory: bool = Field(
        config.memory.use_long_term,
        description="Whether to use long-term memory"
    )
    multi_user_support: bool = Field(
        False,
        description="Whether to enable multi-user support via Memobase"
    )


class MessageRequest(BaseModel):
    """Model for sending a message to an agent."""
    message: str = Field(..., description="Message to send to the agent")
    agent_id: Optional[str] = Field(
        None,
        description="Agent ID to send the message to (uses default if None)"
    )
    user_id: Optional[int] = Field(
        0,
        description="User ID for multi-user support (0 for single-user mode)"
    )


class MessageResponse(BaseModel):
    """Model for agent responses."""
    message: str = Field(..., description="Response from the agent")
    agent_id: str = Field(..., description="ID of the agent that responded")
    user_id: Optional[int] = Field(
        0,
        description="User ID of the requester"
    )
    tools_used: List[str] = Field(
        default_factory=list,
        description="Tools used in generating the response"
    )


class MemorySearchRequest(BaseModel):
    """Model for searching agent memory."""
    query: str = Field(..., description="Search query")
    agent_id: Optional[str] = Field(
        None,
        description="Agent ID to search memories of (uses default if None)"
    )
    user_id: Optional[int] = Field(
        0,
        description="User ID for multi-user support (0 for single-user mode)"
    )
    limit: int = Field(5, description="Maximum number of results to return")
    use_long_term: bool = Field(
        True,
        description="Whether to include long-term memory in search"
    )


class MemoryItem(BaseModel):
    """Model for a memory item."""
    text: str = Field(..., description="Text content of the memory")
    source: str = Field(
        ...,
        description="Source of the memory (buffer/long_term)"
    )
    distance: float = Field(..., description="Semantic distance from query")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the memory"
    )


class MemorySearchResponse(BaseModel):
    """Model for memory search results."""
    query: str = Field(..., description="Original search query")
    agent_id: str = Field(..., description="ID of the agent searched")
    user_id: Optional[int] = Field(
        0,
        description="User ID of the requester"
    )
    results: List[MemoryItem] = Field(
        default_factory=list,
        description="Search results"
    )


class AgentListResponse(BaseModel):
    """Model for listing agents."""
    agents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of agents"
    )


class ToolListResponse(BaseModel):
    """Model for listing tools."""
    tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of available tools"
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Agent Framework API",
        description="API for interacting with AI agents",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up static file serving for the React app
    web_build_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../web/build"))

    if os.path.exists(web_build_dir):
        # Mount static files
        app.mount(
            "/static",
            StaticFiles(directory=f"{web_build_dir}/static"),
            name="static"
        )

        # Also mount any other static assets at the root level
        if os.path.exists(os.path.join(web_build_dir, "assets")):
            app.mount(
                "/assets",
                StaticFiles(directory=f"{web_build_dir}/assets"),
                name="assets"
            )
    else:
        logging.warning(
            f"React build directory not found at {web_build_dir}. "
            "Web UI will not be served. "
            "Run 'npm run build' in the web directory."
        )

    # Define API routes
    @app.get("/api", tags=["Health"])
    async def api_root():
        """Health check endpoint."""
        return {"status": "healthy", "message": "AI Agent Framework API"}

    @app.get("/version", tags=["Health"])
    async def version():
        """Get the current version of the AI Agent Framework."""
        return {"version": get_version()}

    # Original root route now at /api
    @app.get("/", tags=["Health"])
    async def root():
        """Redirect to the React app or API health check."""
        # When we have a build directory, serve index.html
        if os.path.exists(web_build_dir):
            index_path = os.path.join(web_build_dir, "index.html")
            return FileResponse(index_path)
        # Otherwise return API status
        return {"status": "healthy", "message": "AI Agent Framework API"}

    @app.post(
        "/agents",
        response_model=Dict[str, str],
        tags=["Agents"]
    )
    async def create_agent(request: AgentRequest):
        """
        Create a new agent with specified parameters.
        """
        try:
            # Check if agent already exists
            if orchestrator.get_agent(request.agent_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Agent with ID '{request.agent_id}' already exists"
                )

            # Create LLM
            llm = OpenAILLM(model=request.llm_model)

            # Create memory systems
            buffer_memory = BufferMemory()
            long_term_memory = None
            memobase = None

            if request.use_long_term_memory:
                try:
                    long_term_memory = LongTermMemory(
                        default_collection=f"agent_{request.agent_id}"
                    )
                    # Create a Memobase instance if multi-user support is enabled
                    if request.multi_user_support:
                        memobase = Memobase(long_term_memory=long_term_memory)
                except Exception as e:
                    logger.error(f"Error creating long-term memory: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error creating long-term memory: {str(e)}"
                    )

            # Create tools
            tools = []

            if request.enable_web_search:
                tools.append(WebSearch())

            if request.enable_calculator:
                tools.append(Calculator())

            # Create agent
            agent = orchestrator.create_agent(
                agent_id=request.agent_id,
                llm=llm,
                buffer_memory=buffer_memory,
                long_term_memory=long_term_memory,
                memobase=memobase,
                tools=tools,
                system_message=request.system_message
            )

            return {"message": f"Agent '{request.agent_id}' created successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating agent: {str(e)}"
            )

    @app.get(
        "/agents",
        response_model=AgentListResponse,
        tags=["Agents"]
    )
    async def list_agents():
        """List all agents."""
        try:
            agents_info = []
            for agent_id, agent in orchestrator.agents.items():
                tools = agent.get_available_tools()
                tool_names = [tool["name"] for tool in tools]

                agents_info.append({
                    "agent_id": agent_id,
                    "tools": tool_names,
                    "is_default": orchestrator.default_agent_id == agent_id,
                })

            return AgentListResponse(agents=agents_info)

        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error listing agents: {str(e)}"
            )

    @app.delete(
        "/agents/{agent_id}",
        response_model=Dict[str, str],
        tags=["Agents"]
    )
    async def delete_agent(agent_id: str):
        """Delete an agent."""
        try:
            # Check if agent exists
            if not orchestrator.get_agent(agent_id):
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Agent with ID '{agent_id}' not found"
                    )
                )

            # Delete agent
            orchestrator.remove_agent(agent_id)

            return {
                "status": "success",
                "message": f"Agent '{agent_id}' deleted successfully"
            }

        except HTTPException:
            raise

        except Exception as e:
            logger.error(f"Error deleting agent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting agent: {str(e)}"
            )

    @app.post(
        "/agents/chat",
        response_model=MessageResponse,
        tags=["Chat"]
    )
    async def chat_with_agent(request: MessageRequest):
        """
        Send a message to an agent and get a response.
        """
        try:
            agent_id = request.agent_id or config.agent.default_agent_id
            agent = orchestrator.get_agent(agent_id)

            if not agent:
                raise HTTPException(
                    status_code=404,
                    detail=f"Agent with ID '{agent_id}' not found"
                )

            # Get a response from the agent
            response = await agent.chat(message=request.message, user_id=request.user_id)

            return {
                "message": response,
                "agent_id": agent_id,
                "user_id": request.user_id,
                "tools_used": getattr(agent, "last_used_tools", [])
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting response from agent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting response from agent: {str(e)}"
            )

    @app.post(
        "/agents/memory/search",
        response_model=MemorySearchResponse,
        tags=["Memory"]
    )
    async def search_memory(request: MemorySearchRequest):
        """
        Search an agent's memory for relevant information.
        """
        try:
            agent_id = request.agent_id or config.agent.default_agent_id
            agent = orchestrator.get_agent(agent_id)

            if not agent:
                raise HTTPException(
                    status_code=404,
                    detail=f"Agent with ID '{agent_id}' not found"
                )

            # Search memory
            results = await agent.search_memory(
                query=request.query,
                k=request.limit,
                use_long_term=request.use_long_term,
                user_id=request.user_id
            )

            # Format results
            formatted_results = []
            for r in results:
                # Handle different formats from different memory sources
                if "content" in r:
                    text = r["content"]
                elif "text" in r:
                    text = r["text"]
                else:
                    text = str(r)

                # Get metadata
                metadata = r.get("metadata", {})

                # Get distance if available
                distance = r.get("distance", 0.0)

                # Get source
                source = r.get("source", "unknown")

                formatted_results.append({
                    "text": text,
                    "source": source,
                    "distance": distance,
                    "metadata": metadata
                })

            return {
                "query": request.query,
                "agent_id": agent_id,
                "user_id": request.user_id,
                "results": formatted_results
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error searching memory: {str(e)}"
            )

    @app.get(
        "/tools",
        response_model=ToolListResponse,
        tags=["Tools"]
    )
    async def list_tools():
        """List all available tools."""
        try:
            # Create a temporary agent to get the tool list
            if not orchestrator.agents:
                llm = OpenAILLM(
                    api_key=config.llm.openai_api_key,
                    model=config.llm.default_model,
                )

                tools = [Calculator(), WebSearch()]

                orchestrator.create_agent(
                    agent_id="_temp",
                    llm=llm,
                    tools=tools,
                )

                tool_list = (orchestrator.get_agent("_temp")
                             .get_available_tools())
                orchestrator.remove_agent("_temp")
            else:
                # Use existing agent to get tool list
                agent_id = list(orchestrator.agents.keys())[0]
                tool_list = (orchestrator.get_agent(agent_id)
                             .get_available_tools())

            return ToolListResponse(tools=tool_list)

        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error listing tools: {str(e)}"
            )

    # Register WebSocket routes
    register_websocket_routes(app, orchestrator)

    # Serve index.html for all non-API routes (SPA client-side routing)
    # This must be the last route to catch all unhandled paths
    if os.path.exists(web_build_dir):
        @app.get("/{full_path:path}")
        async def serve_react_app(request: Request, full_path: str):
            # Skip API routes
            if full_path.startswith("api/") or \
               full_path.startswith("agents/") or \
               full_path.startswith("tools/") or \
               full_path == "ws":
                raise HTTPException(status_code=404, detail="Not found")

            index_path = os.path.join(web_build_dir, "index.html")
            return FileResponse(index_path)

    return app


def start_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the API server.

    Args:
        host: Host to bind to.
        port: Port to bind to.
        reload: Whether to enable auto-reload.
    """
    uvicorn.run(
        "src.api.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )
