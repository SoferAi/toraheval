"""
Ituria-like Torah Q&A target using MCP server and comprehensive search.
"""
import os
import json
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()


class JewishLibraryMCPClient:
    """Client for connecting to the Jewish Library MCP server using proper MCP SDK."""
    
    def __init__(self, server_command: str = "ituria-mcp-server"):
        self.server_command = server_command
        self.session = None
        self.read = None
        self.write = None
        
    async def connect(self):
        """Connect to the MCP server using stdio transport."""
        try:
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command=self.server_command,  # The MCP server executable
                args=[],  # Optional command line arguments
                env=None,  # Optional environment variables
            )
            
            # Connect using stdio client
            self.read, self.write = await stdio_client(server_params).__aenter__()
            
            # Create session
            self.session = await ClientSession(self.read, self.write).__aenter__()
            
            # Initialize the connection
            await self.session.initialize()
            
            return True
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return False
    
    async def semantic_search(self, query: str, reference: str = "", topics: str = "", limit: int = 30) -> Dict[str, Any]:
        """Perform semantic search using the MCP server."""
        try:
            if not self.session:
                return {"error": "Not connected to MCP server"}
                
            result = await self.session.call_tool(
                "semantic_search",
                arguments={
                    "query": query,
                    "reference": reference,
                    "topics": topics,
                    "limit": limit
                }
            )
            return {"result": result}
        except Exception as e:
            return {"error": f"Semantic search failed: {str(e)}"}
    
    async def keywords_search(self, text: str, reference: str = "", topics: str = "", num_results: int = 50) -> Dict[str, Any]:
        """Perform keywords search using the MCP server."""
        try:
            if not self.session:
                return {"error": "Not connected to MCP server"}
                
            result = await self.session.call_tool(
                "keywords_search",
                arguments={
                    "text": text,
                    "reference": reference,
                    "topics": topics,
                    "num_results": num_results
                }
            )
            return {"result": result}
        except Exception as e:
            return {"error": f"Keywords search failed: {str(e)}"}
    
    async def read_text(self, reference: str) -> Dict[str, Any]:
        """Read text by reference using the MCP server."""
        try:
            if not self.session:
                return {"error": "Not connected to MCP server"}
                
            result = await self.session.call_tool(
                "read_text",
                arguments={"reference": reference}
            )
            return {"result": result}
        except Exception as e:
            return {"error": f"Read text failed: {str(e)}"}
    
    async def get_commentaries(self, reference: str) -> Dict[str, Any]:
        """Get commentaries for a reference using the MCP server."""
        try:
            if not self.session:
                return {"error": "Not connected to MCP server"}
                
            result = await self.session.call_tool(
                "get_commentaries",
                arguments={"reference": reference}
            )
            return {"result": result}
        except Exception as e:
            return {"error": f"Get commentaries failed: {str(e)}"}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        try:
            if not self.session:
                return {"error": "Not connected to MCP server"}
                
            tools = await self.session.list_tools()
            return {"tools": tools}
        except Exception as e:
            return {"error": f"List tools failed: {str(e)}"}
    
    async def close(self):
        """Close the connection."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.read and self.write:
                # Close the stdio client context
                pass  # The context manager should handle cleanup
        except Exception as e:
            print(f"Error closing MCP client: {e}")


async def ituria_agent_search(query: str) -> str:
    """
    Perform comprehensive Jewish text search using the same methodology as the Ituria agent.
    
    This function implements the four-phase search pattern from the Ituria system:
    1. Both semantic_search AND keywords_search
    2. Retrieve full texts with read_text for relevant references  
    3. Get commentaries with get_commentaries for key passages
    4. Read important commentaries with read_text
    """
    
    client = JewishLibraryMCPClient()
    
    if not await client.connect():
        return "Failed to connect to Jewish Library MCP server"
    
    try:
        search_results = []
        references_to_read = []
        commentaries_to_read = []
        
        # Phase 1: Both semantic and keywords search
        # Semantic search for conceptual understanding
        semantic_result = await client.semantic_search(query, limit=20)
        if "error" not in semantic_result:
            search_results.append(f"Semantic search results: {json.dumps(semantic_result, ensure_ascii=False)}")
            
            # Extract references for full text reading
            if "result" in semantic_result and "content" in semantic_result["result"]:
                # Parse references from results (this would need to be adjusted based on actual API response format)
                content = semantic_result["result"]["content"]
                if isinstance(content, list):
                    for item in content[:5]:  # Limit to top 5 results
                        if "reference" in item:
                            references_to_read.append(item["reference"])
        
        # Keywords search with Hebrew terms (convert English query to Hebrew concepts)
        hebrew_keywords = convert_to_hebrew_keywords(query)
        if hebrew_keywords:
            keywords_result = await client.keywords_search(hebrew_keywords, topics="הלכה", num_results=40)
            if "error" not in keywords_result:
                search_results.append(f"Keywords search results: {json.dumps(keywords_result, ensure_ascii=False)}")
                
                # Extract references for full text reading
                if "result" in keywords_result and "content" in keywords_result["result"]:
                    content = keywords_result["result"]["content"]
                    if isinstance(content, list):
                        for item in content[:5]:  # Limit to top 5 results
                            if "reference" in item:
                                references_to_read.append(item["reference"])
        
        # Phase 2: Retrieve full texts for relevant references
        full_texts = []
        for ref in references_to_read[:8]:  # Limit to prevent too many requests
            text_result = await client.read_text(ref)
            if "error" not in text_result:
                full_texts.append(f"Full text of {ref}: {json.dumps(text_result, ensure_ascii=False)}")
                
                # Add this reference for commentary search
                commentaries_to_read.append(ref)
        
        # Phase 3: Get commentaries for key passages
        commentaries_list = []
        for ref in commentaries_to_read[:5]:  # Limit commentary searches
            commentaries_result = await client.get_commentaries(ref)
            if "error" not in commentaries_result:
                commentaries_list.append(f"Commentaries for {ref}: {json.dumps(commentaries_result, ensure_ascii=False)}")
                
                # Extract specific commentary references to read
                if "result" in commentaries_result and "content" in commentaries_result["result"]:
                    content = commentaries_result["result"]["content"]
                    if isinstance(content, list):
                        for commentary in content[:2]:  # Top 2 commentaries per reference
                            if "reference" in commentary:
                                commentary_ref = commentary["reference"]
                                
                                # Phase 4: Read important commentaries
                                commentary_text = await client.read_text(commentary_ref)
                                if "error" not in commentary_text:
                                    commentaries_list.append(f"Commentary text {commentary_ref}: {json.dumps(commentary_text, ensure_ascii=False)}")
        
        # Compile all results
        all_results = {
            "search_results": search_results,
            "full_texts": full_texts, 
            "commentaries": commentaries_list
        }
        
        return json.dumps(all_results, ensure_ascii=False, indent=2)
        
    finally:
        await client.close()


def convert_to_hebrew_keywords(english_query: str) -> str:
    """Convert English concepts to Hebrew keywords for search."""
    # Basic mapping of common English terms to Hebrew equivalents
    keyword_mapping = {
        "prayer": "תפילה",
        "shabbat": "שבת",
        "sabbath": "שבת", 
        "kasher": "כשר",
        "kosher": "כשר",
        "study": "לימוד",
        "torah": "תורה",
        "talmud": "תלמוד",
        "rabbi": "רב",
        "synagogue": "בית כנסת",
        "moses": "משה",
        "law": "הלכה",
        "ethics": "מוסר",
        "business": "משא ומתן",
        "charity": "צדקה",
        "blessing": "ברכה",
        "holiday": "חג",
        "fast": "צום",
        "marriage": "נישואין",
        "divorce": "גירושין"
    }
    
    query_lower = english_query.lower()
    hebrew_terms = []
    
    for english, hebrew in keyword_mapping.items():
        if english in query_lower:
            hebrew_terms.append(hebrew)
    
    if hebrew_terms:
        return " AND ".join(hebrew_terms)
    else:
        # If no direct mapping, return a general search term
        return "הלכה OR מוסר OR תורה"


def ituria_like_target(inputs: dict) -> dict:
    """
    Torah Q&A system that mimics the Ituria site agent behavior.
    
    This function:
    1. Connects to the Jewish Library MCP server
    2. Performs comprehensive search using semantic and keywords search
    3. Retrieves full texts and commentaries
    4. Uses LangChain with Anthropic to generate responses based on found sources
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    question = inputs["question"]
    
    # System prompt similar to Ituria's approach
    system_prompt = """You are a Torah scholar assistant with access to a comprehensive Jewish text database. 

Your role is to:
1. Analyze search results from Jewish texts comprehensively
2. Provide accurate answers based ONLY on the sources provided
3. Include proper citations for all information
4. Respond in scholarly Hebrew when appropriate, or clear English with Hebrew terms
5. Never rely on prior knowledge - only use the provided search results

When analyzing search results:
- Distinguish between direct quotes and paraphrased content
- Provide exact source references (book, chapter, verse/page)
- Consider multiple perspectives from different commentaries
- Explain the context of each source

Format your response with:
- Clear answer to the question
- Supporting quotes with proper attribution
- Source list at the end"""

    try:
        # Perform the comprehensive search
        search_results = asyncio.run(ituria_agent_search(question))
        
        # Initialize LangChain client
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.1,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create the full prompt with search results
        full_prompt = f"""
Question: {question}

Search Results and Sources:
{search_results}

Based on the above search results from Jewish texts, provide a comprehensive answer to the question. 
Remember to:
1. Only use information found in the search results
2. Provide exact citations for all sources
3. Include direct quotes when relevant
4. If the search results don't contain sufficient information, say so clearly
"""
        
        # Generate response using LangChain
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_prompt)
        ]
        
        response = llm.invoke(messages)
        
        return {"answer": response.content.strip()}
        
    except Exception as e:
        return {"answer": f"Error processing question: {str(e)}. The MCP server connection may be unavailable."}
