#!/usr/bin/env node

import express from 'express';
import cors from 'cors';
import Anthropic from '@anthropic-ai/sdk';
import dotenv from 'dotenv';
import { RunTree } from 'langsmith';
import { traceable, withRunTree } from 'langsmith/traceable';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 8334;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const TORAH_SYSTEM_PROMPT = `
You are a Torah scholar assistant.
Answer questions about Torah texts and sources accurately, providing specific citations
when possible.
If asked about Divrei Yoel or other Hasidic texts, try to provide relevant teachings
and sources.
`;

// Main chat processing function with tracing
const processChat = traceable(async function processChat(question, model = 'claude-3-5-sonnet-20241022') {
  console.log(`Processing question: ${question}`);
  console.log(`Using model: ${model}`);

  try {
    const response = await anthropic.messages.create({
      model: model,
      max_tokens: 1000,
      system: TORAH_SYSTEM_PROMPT,
      messages: [
        {
          role: 'user',
          content: question
        }
      ]
    });

    // Extract the text content from the response
    const content = response.content[0];
    const answer = content.type === 'text' ? content.text : String(content);

    // Extract usage metadata
    const usage_metadata = {
      input_tokens: response.usage?.input_tokens || 0,
      output_tokens: response.usage?.output_tokens || 0,
      total_tokens: (response.usage?.input_tokens || 0) + (response.usage?.output_tokens || 0)
    };

    console.log(`Response generated: ${answer.substring(0, 100)}...`);
    console.log(`Usage: ${usage_metadata.input_tokens} input, ${usage_metadata.output_tokens} output tokens`);

    return {
      answer: answer.strip ? answer.strip() : answer.trim(),
      usage_metadata: usage_metadata,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error calling Anthropic API:', error);
    throw error;
  }
}, { name: "processChat" });

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Anthropic JS Target API Server is running',
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
    langsmith_configured: !!process.env.LANGSMITH_TRACING && !!process.env.LANGSMITH_API_KEY,
    timestamp: new Date().toISOString()
  });
});

app.post('/chat', async (req, res) => {
  try {
    const { question, model = 'claude-3-5-sonnet-20241022' } = req.body;
    
    if (!question || !question.trim()) {
      return res.status(400).json({ error: 'Question cannot be empty' });
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(500).json({ error: 'Anthropic API key not configured' });
    }

    // Extract tracing headers and create/continue trace for distributed tracing
    const runTree = RunTree.fromHeaders(req.headers);
    
    // Process the chat request with distributed tracing
    const result = await withRunTree(runTree, () => 
      processChat(question, model)
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

// Start the server
app.listen(port, () => {
  console.log(`🚀 Anthropic JS Target API Server running on http://localhost:${port}`);
  console.log(`📚 Anthropic API configured: ${!!process.env.ANTHROPIC_API_KEY}`);
  console.log(`📊 LangSmith tracing configured: ${!!process.env.LANGSMITH_TRACING && !!process.env.LANGSMITH_API_KEY}`);
  console.log(`📅 Started at: ${new Date().toISOString()}`);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down server...');
  process.exit(0);
});
