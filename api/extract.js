export default async function handler(req, res) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: { message: 'Method not allowed' } });
  }

  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  if (!GROQ_API_KEY) {
    return res.status(503).json({ error: { message: 'Server API key not configured.' } });
  }

  const { mimeType, data64, prompt } = req.body;
  if (!data64) {
    return res.status(400).json({ error: { message: 'No image data provided.' } });
  }

  const dataUri = `data:${mimeType || 'image/jpeg'};base64,${data64}`;
  const defaultPrompt = 'Extract all fields from this identity document as JSON.';

  const payload = {
    model: 'meta-llama/llama-4-scout-17b-16e-instruct',
    messages: [{
      role: 'user',
      content: [
        { type: 'text', text: prompt || defaultPrompt },
        { type: 'image_url', image_url: { url: dataUri } }
      ]
    }],
    temperature: 0,
    max_completion_tokens: 1024,
    response_format: { type: 'json_object' }
  };

  try {
    const groqRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
      },
      body: JSON.stringify(payload)
    });

    const data = await groqRes.json();

    if (!groqRes.ok) {
      const msg = data?.error?.message || `Groq API error ${groqRes.status}`;
      return res.status(groqRes.status).json({ error: { message: msg } });
    }

    let text = (data.choices?.[0]?.message?.content || '').trim();

    // Strip markdown fences if present
    if (text.includes('```')) {
      const parts = text.split('```');
      text = parts[1] || text;
      if (text.startsWith('json')) text = text.slice(4);
    }
    text = text.trim();

    const parsed = JSON.parse(text);
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json({ content: [{ type: 'text', text: JSON.stringify(parsed) }] });

  } catch (e) {
    return res.status(500).json({ error: { message: e.message || 'Unexpected error' } });
  }
}

// Copyright (c) 2026 Pratyush Chaudhari. All Rights Reserved.
