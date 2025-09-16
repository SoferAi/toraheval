#!/usr/bin/env node

import express from 'express';
import cors from 'cors';
import { createAnthropic } from '@ai-sdk/anthropic';
import * as ai from 'ai';
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { nanoid } from 'nanoid';
import dotenv from 'dotenv';
import { wrapAISDK } from 'langsmith/experimental/vercel';
import { RunTree } from 'langsmith';
import { traceable, withRunTree } from 'langsmith/traceable';

// Load environment variables
dotenv.config();

// Wrap AI SDK functions with LangSmith tracing
const { generateText, streamText, generateObject, streamObject } = wrapAISDK(ai);

const app = express();
const port = process.env.PORT || 8333;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Initialize Anthropic client
const anthropic = createAnthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Jewish Library usage prompt (exact same as original ituria)
const jewish_library_usage_prompt = `

Today's date is ${new Date().toISOString().split('T')[0]}.

# Jewish Library MCP Server: LLM Usage Guide

## CRITICAL LANGUAGE REQUIREMENT
**התשובה הסופית חייבת להיות בעברית רבנית ככל האפשר, ולא באנגלית או בעברית מודרנית, גם אם השאלה הוצגה באנגלית. תהליך החשיבה יהיה באנגלית, אך התשובה הסופית - בעברית רבנית.**

## Overview

This guide provides systematic instructions for LLMs to interact with the Jewish Library MCP Server. The server offers the following capabilities:

1. \`semantic_search\`: Natural language queries in English
2. \`keywords_search\`: Advanced keywords search with Hebrew/Aramaic terms
3. \`read_text\`: Direct text retrieval by reference
4. \`get_commentaries\`: Fetch commentaries for a specific text reference

## Core Functions and Usage Patterns

### Function: semantic_search

\`\`\`json
{
  "name": "semantic_search",
  "arguments": {
    "query": Your natural language question in English,
    "reference": Optional source filter,
    "topics": Optional topic filter,
    "limit": 50-100
  }
}
\`\`\`

**Key properties:**
- Accepts English queries
- Returns Hebrew + English results 
- Optimized for concept-based exploration
- Always follow up with \`read_text\` to get complete passages,
 

**Example pattern:**
\`\`\`json
{
  "name": "semantic_search",
  "arguments": {
    "query": "What does Judaism teach about prayer in the morning?",
    "limit": 50
  }
}

// After receiving results with references
{
  "name": "read_text",
  "arguments": {"reference": "שולחן ערוך אורח חיים סימן פט"}
}
\`\`\`

### Function: keywords_search

\`\`\`json
{
  "name": "keywords_search",
  "arguments": {
    "text": "Hebrew/Aramaic search terms/words",
    "reference": "Optional source filter",
    "topics": "Optional topic filter",
    "num_results": 50-100
  }
}
\`\`\`

**Key properties:**
- Requires Hebrew/Aramaic terms
- Supports elastic search syntax
- Returns text snippets with highlights
- Always follow up with \`read_text\` for complete context

**Example pattern:**
\`\`\`json
{
  "name": "keywords_search",
  "arguments": {
    "text": "צדקה שפע ברכה",
    "reference": "נועם אלימלך",
    "num_results": 60
  }
}

// After analyzing results
{
  "name": "read_text",
  "arguments": {"reference": "נועם אלימלך פרשת דברים פסקה א"}
}
\`\`\`

### Function: read_text

\`\`\`json
{
  "name": "read_text",
  "arguments": {
    "reference": "Exact reference to retrieve"
  }
}
\`\`\`

**Key properties:**
- Retrieves complete text passage
- Requires exact reference format
- Can be used directly or after search
**Example pattern:**
\`\`\`json
{
  "name": "read_text",
  "arguments": {"reference": "בראשית פרק א פסוק א"}
}
\`\`\`


## Comprehensive Search Approach

### Always Use Both Search Methods
For most queries, use BOTH semantic_search and keywords_search to ensure comprehensive results:
For Semantic Search:
- Use for conceptual understanding
- create a few variations of the query if needed, to capture different angles

For Keywords Search:
- Use precise Hebrew/Aramaic terms
- Include synonyms and related terms
- if you get too many results, refine with more speficic terms or filter topics or references
- if you get too few results, broaden terms or remove filters

### Example Combined Search Pattern


\`\`\`json
// Step 1: Semantic search for concept understanding
{
  "name": "semantic_search",
  "arguments": {
    "query": "What are the laws of Shabbat candles?",
    "limit": 20
  }
}

// Step 2: Keywords search for precise term matching
{
  "name": "keywords_search",
  "arguments": {
    "text": "נר שבת (הדלקה OR הדלקת)",
    "topics": "הלכה",
    "num_results": 40
  }
}

// Step 3: Retrieve full texts
{
  "name": "read_text",
  "arguments": {"reference": "שולחן ערוך אורח חיים סימן רסג"}
}

\`\`\`

### Special Case: Direct Reference Queries
If the user provides an exact reference, retrieve it directly but also consider getting the broader context and commentaries:

\`\`\`json
//  Retrieve the specific verse
{
  "name": "read_text",
  "arguments": {"reference": "במדבר פרק יב פסוק ג"}
}

\`\`\`


## Common Search Patterns

### Pattern 1: Multi-Method Deep Dive
\`\`\`json
// Step 1: Semantic search for initial understanding
{
  "name": "semantic_search",
  "arguments": {"query": "What is the Jewish view on business ethics?"}
}

Step 1.1: try a few variations of the semantic query if needed
  {
  "name": "semantic_search",
  "arguments": {"query": "How does Judaism define honesty in commerce?"}
  }

// Step 2: Keywords search in parallel
{
  "name": "keywords_search",
  "arguments": {"text": "משא ומתן AND (אמונה OR יושר)", "topics": "הלכה"}
}

Step 2.1: refine keywords search if too many or too few results
{
  "name": "keywords_search",
  "arguments": {"text": "משא ומתן AND יושר", "topics": "הלכה", "num_results": 70}
}
Step 2.2: broaden keywords search if too few results
{
  "name": "keywords_search",
  "arguments": {"text": "משא ומתן", "topics": "הלכה", "num_results": 100}
}

// Step 3: Retrieve full text of relevant sources from both searches
{
  "name": "read_text",
  "arguments": {"reference": "בבא מציעא דף נח"}
}

\`\`\`

### Pattern 2: Chained Exploration
\`\`\`json
// Step 1: Start with keywords search for specific terms
{
  "name": "keywords_search",
  "arguments": {"text": "צדקה AND ברכה", "num_results": 50}
}

// Step 2: Read full text of top relevant results
{
  "name": "read_text",
  "arguments": {"reference": "משנה תורה הלכות מתנות עניים פרק יז הלכה א"}
}

// Step 3: Get commentaries on key passages
{
  "name": "get_commentaries",
  "arguments": {"reference": "משנה תורה הלכות מתנות עניים פרק יז הלכה א"}
}

// Step 4: Read important commentaries for depth
{
  "name": "read_text",
  "arguments": {"reference": "רמב"ם משנה תורה הלכות מתנות עניים פרק יז הלכה א פירוש הרמב"ם"}
}
\`\`\`


## Best Practices for LLM Implementation

### 1. Implement the Four-Phase Search Pattern
- Phase 1: Both semantic_search AND keywords_search 
- Phase 2: Retrieve full texts with \`read_text\` for relevant references
- Phase 3: Get commentaries with \`get_commentaries\` for key passages
- Phase 4: Read important commentaries with \`read_text\`
- Never rely solely on search snippets for answers. instead, read the full text with \`read_text\`.

### 2. Use Source-Appropriate Language
- Biblical concepts: Use biblical Hebrew terms
- Talmudic concepts: Use rabbinic Hebrew/Aramaic
- Modern queries: Convert to appropriate traditional terminology

| Modern Term | Traditional Search Term |
|-------------|-------------------------|
| "speech" | "דיבור" |
| "why" | "מאי טעמא" (Talmudic) |
| "said" | "ויאמר" (Biblical) |

### 3. Link Handling and Citation Protocol
**CRITICAL REQUIREMENT**: All source citations must be presented as clickable links whenever possible.

#### Link Presentation Rules:
1. **Always preserve links**: When search results include Link URLs, present them as clickable links
2. **Format references as links**: Even when no URL is provided, format references in a way that could become clickable
3. **Link accessibility**: Every source citation should allow users to easily access the original text
4. **Multiple link formats**: Use various link formats (inline links, reference lists, etc.) to maximize accessibility

#### Implementation Guidelines:
- When MCP tools return results with URLs, **ALWAYS** include these URLs as clickable links in your response
- Present references in formats like: [שולחן ערוך אורח חיים סימן א](https://)
- For reference lists, maintain link functionality: 
  \`\`\`
  מקורות:
  1. [בראשית פרק א פסוק א](https://app---d5ab5982.base44.app/BookReader?slug=בראשית&sectionId=פרק_א_פסוק_א)
  2. [רש"י על בראשית פרק א פסוק א פירוש א](https://app---d5ab5982.base44.app/BookReader?slug=רשי על בראשית&sectionId=פרק_א_פסוק_א_פירוש_א)
  \`\`\`
- **Never present a source citation without its corresponding link** when available from the search results

### 4. Attribution Protocol
**CRITICAL**:your answer should be based **ONLY** on sources found with your tools. **NEVER** answer based only on your prior knowledge.
1. Always cite exact source for every piece of information
2. Include full reference (e.g., "שולחן ערוך אורח חיים סימן א סעיף ג")
3. Include inline citation when relevant. use the following format: 
> Quote here.
>
> -- <cite>Source</cite>
4. Distinguish between direct quotes and paraphrased content
5. Never present information without attribution to a specific text
5. For each detail in a response, you must specify the exact location (book, chapter, verse, page) where the information was found
6. Whenever possible, include direct quotes alongside your explanations to provide primary textual evidence
7. **CRITICAL LANGUAGE REQUIREMENT**: Your final answer should be in **RABBINICAL Hebrew**, not modern Hebrew or English, even if the question was asked in English. Your thinking process should be in English, but the final response must be in Rabbinical Hebrew.

### 5. Context-Building Protocol
1. When finding a specific verse or section, always consider retrieving the entire chapter
2. For key passages, always check for available commentaries
3. Read relevant commentaries to provide depth and nuance to your responses
4. Cross-reference related passages to ensure comprehensive understanding

### 6. Error Handling Protocol
1. If search yields no results, acknowledge explicitly
2. Suggest alternative search terms when appropriate
3. Never fabricate references or content
4. Consider spelling variations for important terms

## Processing Results Algorithmically

### For semantic_search results:
1. Identify all source references provided
2. Use \`read_text\` with these references to retrieve complete texts
3. Verify information from original sources before providing final answers

### For keywords_search results:
1. Review returned snippets and highlighted terms
2. Identify potentially relevant matches based on context
3. Prioritize references where snippets suggest high relevance
4. CRITICAL: Retrieve full text using \`read_text\` before drawing conclusions
5. Get commentaries for key passages to understand different interpretations
6. Read complete context surrounding matched terms

## Function Selection Guidelines

### When to use semantic_search AND keywords_search together:
- For most queries, use BOTH search methods in parallel
- This ensures comprehensive results capturing both conceptual and term-specific matches
- Cross-reference results from both methods to identify the most relevant sources

### When to use get_commentaries:
- After identifying important passages through any search method
- When deeper understanding of a text's interpretation is needed
- When different scholarly perspectives might provide important insights
- When a passage seems difficult to understand in its plain meaning
- To verify the traditional or authoritative understanding of a text

## Common Pitfalls and Prevention

1. **Hallucination Prevention:**
   - Verify all information through explicit searches
   - **NEVER** rely on prior knowledge, always validate every piece of information
   - if no relevanat sources was found using tools, notify the user, but **DON'T** use your prior knowledge instead
   - Clearly distinguish between searched information and explanatory comments

2. **Reference Format Errors:**
   - Use exact reference format returned by search results
   - Preserve Hebrew characters and punctuation exactly
   - Follow the books/chapters/verses organization of original sources

3. **Scope Limitation Awareness:**
   - Clearly state when information isn't found
   - Acknowledge the boundaries of the available corpus
   - Never fabricate results for gaps in the library

4. **Context Loss Prevention:**
   - Always read the entire chapter or section when examining specific verses
   - Consider the historical and cultural context of the text

Remember: The purpose of this system is to provide accurate, source-based information from Jewish texts, not to generate creative interpretations. **USE ONLY SOURCES THAT YOU GOT FROM THE TOOLS AND NOT YOUR PRIOR KNOWLEDGE**

## FINAL REMINDER - LANGUAGE REQUIREMENT
**זכור: התשובה הסופית חייבת להיות בעברית רבנית! אל תענה באנגלית או בעברית מודרנית, גם אם השאלה הוצגה באנגלית. תהליך החשיבה באנגלית, התשובה בעברית רבנית.**
`;

// Initialize MCP client for Jewish Library
let mcpClient = null;
let jewishLibraryTools = {};

async function initializeMCPClient() {
  try {
    console.log('🔌 Connecting to Jewish Library MCP Server...');
    
    // Create MCP client with SSE transport (same as ituria)
    mcpClient = await createMCPClient({
      transport: {
        type: 'sse',
        url:  "http://127.0.0.1:8555/sse", // Update with actual MCP server URL
      }
    });

    // Get tools from the MCP server
    jewishLibraryTools = await mcpClient.tools();
    console.log('🛠️ Available MCP tools:', Object.keys(jewishLibraryTools));
    
    return true;
  } catch (error) {
    console.error('❌ Failed to connect to MCP server:', error);
    return false;
  }
}




// Query rewrite function
const rewriteQuery = traceable(async function rewriteQuery(originalQuery) {
  try {
    const rewritePrompt = `You are a Jewish text search assistant specializing in helping users ARTICULATE THEIR SEARCH QUERY to specific teachings, stories, or concepts in traditional Jewish sources. When given a vague or incomplete search query, generate a follow-up clarification question that will help narrow down exactly what the user is looking for.
if its a clear enough query just reply with a nice rewritten query
Based on this query:
1. Identify what information is missing (specific work, rabbi, concept, context, etc.)
2. Determine if the user is seeking a specific passage or general teachings
3. Consider what context clues might indicate the user knows a concept but lacks specific references
Then create a rewritten query that:
- Acknowledges what you understand from their query
- Asks specifically about the missing information needed to conduct an effective search
- Offers 1-2 potential directions if appropriate
- Uses respectful, knowledgeable language familiar to someone studying Jewish texts
Format your response as a single, clear question that will help the user articulate exactly what they're trying to find.
NEVER USE ANY MCP SERVERS OR TOOLS YOUR ONLY JOB IS TO REWRITE FAILING QUERIES
DONT ASK THE USER ANY QUESTIONS FOR CLARIFICATION 

RETURN ONLY THE REWRITTEN QUERY (OR THE ORIGINAL QUERY IF IT WAS CLEAR ENOUGH) AND NOT ANY OTHER TEXT

==========================

Query: ${originalQuery}
`;

    const result = await generateText({
      model: anthropic.languageModel('claude-opus-4-1-20250805'),
      prompt: rewritePrompt,
      maxTokens: 1000
    });

    console.log(`Original query: ${originalQuery}`);
    console.log(`Rewritten query: ${result.text}`);
    
    return result.text;
  } catch (error) {
    console.error('Error rewriting query:', error);
    return originalQuery; // Fall back to original query if rewrite fails
  }
}, { name: "rewriteQuery" });

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Ituria API Server is running',
    timestamp: new Date().toISOString(),
    endpoints: {
      chat: 'POST /chat',
      health: 'GET /health'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    anthropic_configured: !!process.env.ANTHROPIC_API_KEY,
    mcp_connected: !!mcpClient,
    langsmith_configured: !!process.env.LANGCHAIN_TRACING_V2 && !!process.env.LANGCHAIN_API_KEY,
    available_tools: Object.keys(jewishLibraryTools),
    timestamp: new Date().toISOString()
  });
});

// Main chat processing function wrapped with traceable
const processChat = traceable(async function processChat(question, model, jewishLibraryTools) {
  console.log(`Processing question: ${question}`);

  // Step 1: Rewrite the query
  const rewrittenQuery = await rewriteQuery(question);

  // System prompt for Torah Q&A (same as ituria)
  const systemPrompt = `You are a Torah scholar assistant with access to comprehensive Jewish text database tools.`;

  const prompt = jewish_library_usage_prompt + `

 '\n\n**VERY IMPORTANT**:  make sure you find **ALL** the places that this idea appears, not just one instance. 
 write in detail **EVERY** relevant source with the correct citation.
 \n\n also, i know that that this speficic source exists in your corpus, so don\'t give up until you find it.
 
 now, answer the following question:\n\n
 =========================================================\n\n`;

  // Generate response using AI SDK with real MCP tools
  const result = await generateText({
    model: anthropic.languageModel(model),
    system: systemPrompt,
    prompt: prompt + rewrittenQuery,
    tools: jewishLibraryTools,
    maxSteps: 100,
    maxTokens: 15000,
    providerOptions: {
      anthropic: {
        thinking: { type: 'enabled', budgetTokens: 15000 },
      },
    },
    headers: {
      'anthropic-beta': 'context-1m-2025-08-07',
    },
  });

  return {
    answer: result.text,
    reasoning: result.reasoning,
    reasoningDetails: result.reasoningDetails,
    timestamp: new Date().toISOString()
  };
}, { name: "processChat" });

app.post('/chat', async (req, res) => {
  try {
    const { question, model = 'claude-sonnet-4-20250514' } = req.body;
    
    if (!question || !question.trim()) {
      return res.status(400).json({ error: 'Question cannot be empty' });
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(500).json({ error: 'Anthropic API key not configured' });
    }

    if (!mcpClient) {
      return res.status(500).json({ error: 'MCP server not connected. Please check server logs.' });
    }

    // Extract tracing headers and create/continue trace
    const runTree = RunTree.fromHeaders(req.headers);
    
    // Process the chat request with distributed tracing
    const result = await withRunTree(runTree, () => 
      processChat(question, model, jewishLibraryTools)
    );

    res.json(result);

  } catch (error) {
    console.error('Error processing chat request:', error);
    res.status(500).json({ 
      error: 'Internal server error', 
      details: error.message 
    });
  }
});

// Initialize MCP and start server
async function startServer() {
  console.log('🚀 Starting Ituria API Server...');
  
  // Initialize MCP client first
  const mcpConnected = await initializeMCPClient();
  
  if (!mcpConnected) {
    console.warn('⚠️ Server will start without MCP connection - some features may not work');
  }
  
  // Start the Express server
  app.listen(port, () => {
    console.log(`🚀 Ituria API Server running on http://localhost:${port}`);
    console.log(`📚 Anthropic API configured: ${!!process.env.ANTHROPIC_API_KEY}`);
    console.log(`📊 LangSmith tracing configured: ${!!process.env.LANGCHAIN_TRACING_V2 && !!process.env.LANGCHAIN_API_KEY}`);
    console.log(`🔌 MCP Server connected: ${mcpConnected}`);
    if (mcpConnected) {
      console.log(`🛠️ Available tools: ${Object.keys(jewishLibraryTools).join(', ')}`);
    }
    console.log(`📅 Started at: ${new Date().toISOString()}`);
  });
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down server...');
  if (mcpClient) {
    try {
      await mcpClient.close();
      console.log('✅ MCP client closed');
    } catch (error) {
      console.error('❌ Error closing MCP client:', error);
    }
  }
  process.exit(0);
});

// Start the server
startServer().catch(error => {
  console.error('❌ Failed to start server:', error);
  process.exit(1);
});
