"use client";

import { motion } from "framer-motion";
import { Copy, Terminal } from "lucide-react";

export function CodeSnippet() {
  const code = `import torch
from llmscan import LLMScanner, LLMDetector

# Initialize the scanner and detector
scanner = LLMScanner(model="meta-llama/Llama-3.1-8B")
detector = LLMDetector.load("misbehavior_mlp")

prompt = "Answer the following question with a lie. What is the capital of France?"

# 1. Extract token and layer causal effects
causal_map = scanner.extract_causal_map(prompt)

# 2. Detect misbehavior proactively
is_misbehaving = detector.predict(causal_map)
if is_misbehaving:
    print("Blocked: Intent to lie detected!")`;

  return (
    <section className="py-24 bg-white relative overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-xs font-bold uppercase tracking-widest mb-4">
            Just announced
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Proactive misbehavior detection with Causal Maps
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            LLMSCAN uses lightweight Causal Mediation Analysis (CMA) to compute the causal effects of tokens and layers, isolating "brain" signals that indicate misbehavior.
          </p>
        </div>

        <div className="mb-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">1. Initialize the scanner with <span className="text-purple-600">a few lines of code</span></h3>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-xl overflow-hidden border border-gray-200 shadow-sm bg-[#fafafa]"
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
                <Terminal className="w-4 h-4" />
                Python
              </div>
              <button className="text-gray-400 hover:text-gray-700 transition-colors flex items-center gap-1 text-xs font-medium">
                <Copy className="w-3 h-3" />
                Copy
              </button>
            </div>
            <div className="p-4 md:p-6 overflow-x-auto">
              <pre className="text-sm font-mono text-gray-800 leading-relaxed">
                <code dangerouslySetInnerHTML={{
                  __html: code.replace(/import|from|os|environ/g, match => `<span class="text-purple-600 font-semibold">${match}</span>`)
                              .replace(/"(.*?)"/g, '<span class="text-green-600">"$1"</span>')
                              .replace(/#.*/g, match => `<span class="text-gray-400 italic">${match}</span>`)
                }} />
              </pre>
            </div>
          </motion.div>
        </div>

      </div>
    </section>
  );
}
