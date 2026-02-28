#!/usr/bin/env python3
"""
Simple Embedding API Service
Provides sentence-transformers embeddings via HTTP API for n8n workflows
"""

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Load model once at startup
print("Loading sentence-transformers model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print(f"Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")


@app.route('/embed', methods=['POST'])
def embed():
    """Generate embedding for input text"""
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field in request'}), 400

        text = data['text']

        if not text or not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400

        # Generate embedding
        embedding = model.encode(text)

        # Convert to list for JSON serialization
        embedding_list = embedding.tolist()

        return jsonify({
            'embedding': embedding_list,
            'dimension': len(embedding_list),
            'model': 'sentence-transformers/all-MiniLM-L6-v2'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'sentence-transformers/all-MiniLM-L6-v2',
        'dimension': model.get_sentence_embedding_dimension()
    })


if __name__ == '__main__':
    # Run on port 5000, accessible from network
    app.run(host='0.0.0.0', port=5000, debug=False)
