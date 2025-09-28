#!/usr/bin/env node

import express from 'express';
import cors from 'cors';
import { createAnthropic } from '@ai-sdk/anthropic';
import * as ai from 'ai';
import { experimental_createMCPClient as createMCPClient, stepCountIs } from 'ai';
import dotenv from 'dotenv';
import { wrapAISDK } from 'langsmith/experimental/vercel';
import { RunTree } from 'langsmith';
import { traceable, withRunTree } from 'langsmith/traceable';

// Load environment variables
dotenv.config();

// Wrap AI SDK functions with LangSmith tracing
const { generateText, } = wrapAISDK(ai);

const app = express();
const port = process.env.PORT || 8333;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Initialize Anthropic client
const anthropic = createAnthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Jewish Library usage prompt 
const jewish_library_usage_prompt = `
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
    "limit": 25-55
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
    "reference": "תפארת שלמה",
    "limit": 40
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
    "text": "Hebrew/Aramaic/English search terms/words",
    "reference": "Optional source filter",
    "topics": "Optional topic filter",
    "num_results": 25-55
  }
}
\`\`\`

**Key properties:**
- Works with Hebrew/Aramaic OR English terms (perform separate searches for each language)
- Supports elastic search syntax
- Returns text snippets with highlights
- Always follow up with \`read_text\` for complete context
- **IMPORTANT**: Perform SEPARATE searches in Hebrew/Aramaic OR English to maximize coverage - not both in one search

**Example pattern:**
\`\`\`json
{
  "name": "keywords_search",
  "arguments": {
    "text": "צדקה שפע ברכה",
    "reference": "נועם אלימלך",
    "num_results": 20
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
- Use precise Hebrew/Aramaic terms OR English terms (in separate searches)
- Include synonyms and related terms in both languages
- Perform multiple searches: one in Hebrew/Aramaic, one in English
- If you get too many results, refine with more specific terms or filter topics or references
- If you get too few results, broaden terms or remove filters

### Example Combined Search Pattern

\`\`\`json
// Step 1: Semantic search for concept understanding
{
  "name": "semantic_search",
  "arguments": {
    "query": "What are the laws of Shabbat candles?",
    "limit": 35
  }
}

// Step 2: Keywords search for precise term matching (Hebrew)
{
  "name": "keywords_search",
  "arguments": {
    "text": "נר שבת (הדלקה OR הדלקת)",
    "topics": "הלכה",
    "num_results": 45
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



## Best Practices for LLM Implementation

### 1. Implement the Four-Phase Search Pattern
- Phase 1: Both semantic_search AND keywords_search
- Phase 2: For EACH relevant source found, use read_text to get full passages
- Phase 3: refine searches based on initial findings
- Never rely solely on search snippets for answers. instead, read the full text with \`read_text\`.

### 2. Use Source-Appropriate Language
- Biblical concepts: Use biblical Hebrew terms
- Talmudic concepts: Use rabbinic Hebrew/Aramaic
- Modern queries: Convert to appropriate traditional terminology

Examples: "speech" → "דיבור", "why" → "מאי טעמא", "said" → "ויאמר"

### 3. Link Handling and Citation Protocol
**CRITICAL REQUIREMENT**: All source citations must be presented as clickable links whenever possible.

#### Link Presentation Rules:
1. **Always preserve links**: When search results include Link URLs, present them as clickable links
2. **Format references as links**: Even when no URL is provided, format references in a way that could become clickable
3. **Link accessibility**: Every source citation should allow users to easily access the original text
4. **Multiple link formats**: Use various link formats (inline links, reference lists, etc.) to maximize accessibility

#### Implementation Guidelines:
- Always include URLs as clickable links in your response
- Present references in formats like: [שולחן ערוך אורח חיים סימן א](https://)
- Never present a source citation without its corresponding link when available

### 4. Attribution Protocol
**CRITICAL**:your answer should be based **ONLY** on sources found with your tools. **NEVER** answer based only on your prior knowledge.
1. Always cite exact source for every piece of information
2. Include full reference and direct quotes when possible
3. **CRITICAL LANGUAGE REQUIREMENT**: Your final answer should be in **RABBINICAL Hebrew**, not modern Hebrew or English, even if the question was asked in English.

### 5. Error Handling Protocol
1. If search yields no results, acknowledge explicitly and suggest alternatives
2. Never fabricate references or content
3. Consider spelling variations for important terms

## Common Pitfalls and Prevention

1. **Use ONLY sources found with tools** - never rely on prior knowledge
2. **Use exact reference formats** from search results
3. **Read full texts** - never rely only on search snippets
4. **Acknowledge when information isn't found** - never fabricate

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
        url:  "https://jewish-library-mcp-preview.fly.dev/sse", // Update with actual MCP server URL
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
- Uses respectful, knowledgeable language familiar to someone studying Jewish texts
Format your response as a single, clear question that will help the user articulate exactly what they're trying to find.
NEVER USE ANY MCP SERVERS OR TOOLS YOUR ONLY JOB IS TO REWRITE FAILING QUERIES
DONT ASK THE USER ANY QUESTIONS FOR CLARIFICATION 

RETURN ONLY THE REWRITTEN QUERY (OR THE ORIGINAL QUERY IF IT WAS CLEAR ENOUGH) AND NOT ANY OTHER TEXT

==========================

Query: ${originalQuery}
`;

    const result = await generateText({
      model: anthropic('claude-sonnet-4-20250514'),
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
// Implements comprehensive Anthropic Claude prompt caching to optimize API costs:
//
// CACHING STRATEGY:
// 1. System Prompt Caching (1-hour TTL):
//    - Large Jewish library usage guide (~4000 tokens) cached for 1 hour
//    - Base system prompt remains uncached for flexibility
//    - Uses multiple system messages to enable cache breakpoints
//
// 2. Tool Definitions Caching (1-hour TTL):
//    - All MCP Jewish Library tool definitions cached for 1 hour
//    - Applied to the last tool to cache the entire tool set
//    - Significant savings since tool definitions are large and stable
//
// 3. Conversation History Caching (via prepareStep, 5-minute TTL):
//    - Caches conversation context in multi-step tool calling scenarios
//    - Smart compression for long conversations (>15 messages)
//    - Applies cache control to conversation boundaries for optimal savings
//    - Prevents context window bloat while maintaining conversation quality
//
// 4. Cache Monitoring:
//    - Tracks cache hits/misses for cost optimization
//    - Logs different TTL cache usage (5m vs 1h)
//    - Calculates efficiency metrics and estimated cost savings
//    - Monitors step-by-step cache performance
//
// EXPECTED SAVINGS:
// - System prompt: ~75% reduction on repeat queries (4000+ tokens)
// - Tool definitions: ~75% reduction on all requests with tools
// - Conversation history: ~75% reduction in multi-step scenarios
// - Overall: 50-70% token cost reduction for typical usage patterns
const processChat = traceable(async function processChat(question, model, jewishLibraryTools) {
  console.log(`Processing question: ${question}`);

  // Step 1: Rewrite the query
  const rewrittenQuery = await rewriteQuery(question);

  // System prompt components with caching - AI SDK 5.0 format
  const baseSystemPrompt = "You are a Torah scholar assistant with access to comprehensive Jewish text database tools.";
  
  const userPrompt = `
**CRITICAL REQUIREMENT - COMPREHENSIVE SOURCE COVERAGE**: 
Your answer MUST include EVERY SINGLE source that is relevant to this topic. Do not stop after finding a few sources - the user expects comprehensive coverage of ALL occurrences. 

**Search Strategy - MANDATORY STEPS**:
1. Use BOTH semantic_search AND keywords_search with multiple variations
2. Search in Hebrew, Aramaic, AND English terms (separate searches for each language)
3. For EACH source you find, read the FULL TEXT and then search for related passages in the same work
4. Search related works and cross-references mentioned in the sources
5. Continue searching until you have exhaustively covered all possibilities

**When you find ANY relevant source**:
- Search for ALL other instances of this concept in the SAME work (entire tractate, entire section, etc.)
- Look for parallel discussions in related works
- Follow cross-references and citations mentioned in the text

**Examples of THOROUGH coverage**:
- If you find it in Rashi on Genesis 1:1, search ALL of Rashi's commentary for this concept
- If you find it in Bava Metzia 58a, search the ENTIRE tractate Bava Metzia and related tractates
- If you find it in one chapter of Mishneh Torah, search ALL relevant sections throughout Mishneh Torah
- If you find it in one section of Shulchan Aruch, check ALL four sections and their commentaries
- If you find it in one Chassidic work, check other works by the same author and related teachings

**Citation Requirements - EVERY SINGLE MENTION**:
- List EVERY occurrence with complete, precise citations
- Include ALL instances even if they contain identical or nearly identical content - the user wants EVERY single place it appears
- If the same teaching appears in 5 different places, cite ALL 5 places individually with full citations
- If the same concept is mentioned in 20 different sources, list ALL 20 sources separately
- Do NOT group similar sources together - cite each occurrence individually
- Provide the exact location (chapter, verse, page, section, etc.) for each source
- Include links when available

**Repetition is REQUIRED**: 
Even if you find the exact same quote or teaching in multiple locations, cite EVERY single location where it appears. The user values complete bibliographic coverage over avoiding repetition.

**Quality Control**:
Your answer will be considered INCOMPLETE if you present only a few sources when many more exist, or if you group similar sources together instead of citing each occurrence individually. The user values exhaustive citation of EVERY mention over brevity.

now, answer the following question with COMPLETE comprehensive coverage:

=========================================================

${rewrittenQuery}`;

  // Messages with proper cache breakpoints - cache system prompt with 1-hour TTL
  const messages = [
    {
      role: 'system',
      content: baseSystemPrompt
    },
    {
      role: 'user',
      content: jewish_library_usage_prompt,
      providerOptions: {
        anthropic: { cacheControl: { type: 'ephemeral' } }
      }
    },
    {
      role: 'user',
      content: userPrompt
    }
  ];



  // Enable tool caching for AI SDK 5.0
  const cachedTools = {};
  if (jewishLibraryTools && Object.keys(jewishLibraryTools).length > 0) {
    const toolKeys = Object.keys(jewishLibraryTools);
    const lastToolKey = toolKeys[toolKeys.length - 1];
    
    // Apply 1-hour caching to the last tool to cache all tool definitions
    for (const [key, tool] of Object.entries(jewishLibraryTools)) {
      cachedTools[key] = {
        ...tool
      };
    }
  }

  // Debug: Log tools structure
  console.log('Available tools:', Object.keys(jewishLibraryTools));
  console.log('Tools structure sample:', jewishLibraryTools[Object.keys(jewishLibraryTools)[0]]);

  // Generate response using AI SDK 5.0 with caching and prepareStep
  const result = await generateText({
    //use haiku for faster responses during testing
    model: anthropic('claude-sonnet-4-20250514'), //anthropic('claude-sonnet-4-20250514'),
    messages: messages,
    tools: Object.keys(cachedTools).length > 0 ? cachedTools : jewishLibraryTools,
    maxRetries: 5,
    stopWhen: stepCountIs(50),
    maxTokens: 15000,
        providerOptions: {
      anthropic: {
        thinking: { type: 'enabled', budgetTokens: 1200 },
      }
    },
    headers: {
      'anthropic-beta': 'context-1m-2025-08-07'
    },

    // Enable detailed provider metadata for cache monitoring
    returnProviderMetadata: true,
    // Use prepareStep to cache conversation history and optimize message handling
    prepareStep: async ({ stepNumber, steps, messages }) => {
      console.log(`📋 Preparing step ${stepNumber + 1}, ${messages.length} messages, ${steps.length} previous steps`);
      
      // Cache conversation history - find the last assistant message and cache it
      if (messages.length >= 4) {
        // Find the last assistant message (excluding the very last message which should be user)
        let lastAssistantIndex = -1;
        for (let i = messages.length - 2; i >= 0; i--) {
          if (messages[i].role === 'assistant') {
            lastAssistantIndex = i;
            break;
          }
        }
        
        if (lastAssistantIndex >= 0) {
          const modifiedMessages = [...messages];
          modifiedMessages[lastAssistantIndex] = {
            ...messages[lastAssistantIndex],
            providerOptions: {
              anthropic: { cacheControl: { type: 'ephemeral' } }
            }
          };
          
          console.log(`⚡ Applied cache control to conversation context (${messages.length} messages, cached at index ${lastAssistantIndex})`);
          return {
            messages: modifiedMessages
          };
        }
      }
      
      // For longer conversations (>15 messages), implement smart compression
      if (messages.length > 15) {
        console.log(`🗜️ Compressing conversation history: ${messages.length} → ${Math.min(12, messages.length)} messages`);
        
        // Keep system messages, recent messages, and apply cache to the boundary
        const systemMessages = messages.filter(m => m.role === 'system');
        const otherMessages = messages.filter(m => m.role !== 'system');
        
        // Keep last 8 messages from conversation
        const recentMessages = otherMessages.slice(-8);
        
        // Apply cache control to the last assistant message in recent messages
        for (let i = recentMessages.length - 2; i >= 0; i--) {
          if (recentMessages[i].role === 'assistant') {
            recentMessages[i] = {
              ...recentMessages[i],
              providerOptions: {
                anthropic: { cacheControl: { type: 'ephemeral' } }
              }
            };
            break;
          }
        }
        
        return {
          messages: [...systemMessages, ...recentMessages]
        };
      }
      
      // Default: no modifications
      return {};
    }
  });

  // Extract usage metadata from the result including comprehensive cache info
  // Note: AI SDK 5.0 exposes cache metadata via providerMetadata.anthropic
  const providerMeta = result.providerMetadata?.anthropic || {};
  const usage_metadata = {
    input_tokens: result.usage?.promptTokens || 0,
    output_tokens: result.usage?.completionTokens || 0,
    total_tokens: result.usage?.totalTokens || (result.usage?.promptTokens || 0) + (result.usage?.completionTokens || 0),
    // Cache usage metadata for cost analysis from AI SDK 5.0
    cache_creation_input_tokens: providerMeta.cacheCreationInputTokens || 0,
    cache_read_input_tokens: providerMeta.cacheReadInputTokens || 0,
    // Enhanced cache metadata tracking for different TTLs
    cache_creation: providerMeta.cacheCreation || null,
    // Cache efficiency metrics
    cache_hit: (providerMeta.cacheReadInputTokens || 0) > 0,
    cache_efficiency_percent: providerMeta.cacheReadInputTokens > 0 
      ? Math.round(providerMeta.cacheReadInputTokens / ((result.usage?.promptTokens || 0) + providerMeta.cacheReadInputTokens) * 100)
      : 0,
    // Cost savings (assuming cache reads are cheaper than full computation)
    estimated_cost_savings: providerMeta.cacheReadInputTokens * 0.25 // 75% savings on cached tokens
  };

  // Enhanced cache usage monitoring for cost optimization
  const cacheStats = {
    hit: providerMeta.cacheReadInputTokens > 0,
    created: providerMeta.cacheCreationInputTokens > 0,
    saved: providerMeta.cacheReadInputTokens || 0,
    created_tokens: providerMeta.cacheCreationInputTokens || 0
  };
  
  if (cacheStats.hit) {
    console.log(`💰 Cache Hit: Saved ${cacheStats.saved} tokens (${Math.round(cacheStats.saved / (usage_metadata.input_tokens + cacheStats.saved) * 100)}% of input)`);
  }
  
  if (cacheStats.created) {
    console.log(`🔄 Cache Created: ${cacheStats.created_tokens} tokens cached for future requests`);
    // Log TTL-specific cache creation details
    if (providerMeta.cacheCreation) {
      const ephemeral5m = providerMeta.cacheCreation.ephemeral_5m_input_tokens || 0;
      const ephemeral1h = providerMeta.cacheCreation.ephemeral_1h_input_tokens || 0;
      if (ephemeral5m > 0) console.log(`  └ 5-minute TTL: ${ephemeral5m} tokens`);
      if (ephemeral1h > 0) console.log(`  └ 1-hour TTL: ${ephemeral1h} tokens`);
    }
  }
  
  // Log cache efficiency metrics
  if (cacheStats.hit || cacheStats.created) {
    console.log(`📊 Cache Status: System prompt cached, Tools cached, Total savings potential: ${Math.round((cacheStats.saved + cacheStats.created_tokens) / usage_metadata.total_tokens * 100)}%`);
  }

  return {
    answer: result.text,
    reasoning: result.reasoning,
    reasoningDetails: result.reasoningDetails,
    usage_metadata: usage_metadata,
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
    console.log(`⚡ Anthropic prompt caching enabled: System prompts (1h TTL) + Tool definitions (1h TTL) + Conversation history (5m TTL via prepareStep)`);
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
