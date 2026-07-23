import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { spawn } from 'child_process';
import axios from 'axios';

// --- Custom Middleware Plugin for Local AI Services ---
const localApiPlugin = () => ({
  name: 'local-api-plugin',
  configureServer(server) {
    // Middleware for Text-to-Speech
    server.middlewares.use('/api/speak', (req, res, next) => {
      if (req.method !== 'POST') return next();
      let body = '';
      req.on('data', chunk => { body += chunk.toString(); });
      req.on('end', () => {
        try {
          const { text } = JSON.parse(body);
          if (!text) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: 'No text provided.' }));
          }
          console.log(`[Speak API] Received text: "${text}"`);
          const pythonProcess = spawn(
            path.resolve(__dirname, '../../venv/bin/python3'),
            [path.resolve(__dirname, '../../tools/speak.py'), text],
            { env: { ...process.env, COQUI_TOS_AGREED: "1" } }
          );
          pythonProcess.stdout.on('data', (data) => console.log(`[Speak Script Out]: ${data}`));
          pythonProcess.stderr.on('data', (data) => console.error(`[Speak Script Err]: ${data}`));
          pythonProcess.on('close', (code) => console.log(`[Speak Script] exited with code ${code}`));
          res.statusCode = 200;
          res.end(JSON.stringify({ status: 'ok' }));
        } catch (e) {
          console.error('[Speak API] Error:', e);
          res.statusCode = 500;
          res.end(JSON.stringify({ error: 'Internal server error.' }));
        }
      });
    });

    // Middleware for Ollama Chat
    server.middlewares.use('/api/chat', async (req, res, next) => {
      if (req.method !== 'POST') return next();
      let body = '';
      req.on('data', chunk => { body += chunk.toString(); });
      req.on('end', async () => {
        try {
          const { prompt } = JSON.parse(body);
           if (!prompt) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ error: 'No prompt provided.' }));
          }
          console.log(`[Chat API] Received prompt for Ollama: "${prompt}"`);
          
          const ollamaRes = await axios.post('http://localhost:11434/api/generate', {
            model: 'nemotron-3-super:cloud',
            prompt: prompt,
            stream: false
          });

          res.setHeader('Content-Type', 'application/json');
          res.statusCode = 200;
          res.end(JSON.stringify({ response: ollamaRes.data.response }));

        } catch (e) {
          console.error('[Chat API] Error:', e.message);
          res.statusCode = 500;
          res.end(JSON.stringify({ error: 'Failed to connect to Ollama.' }));
        }
      });
    });
  }
});


export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react(), localApiPlugin()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});