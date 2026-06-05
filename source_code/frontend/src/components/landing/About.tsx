"use client";

import { motion } from "framer-motion";
import { HelpCircle, Target, Users, Brain } from "lucide-react";

export function About() {
  const points = [
    {
      icon: <Brain className="w-6 h-6 text-purple-600" />,
      title: "What We Did",
      description: "We built LLMSCAN, a runtime causal diagnostic engine for large language models. It uses HuggingFace activation hooks to intercept internal activations (from mid-to-high transformer layers) and processes them through an ensemble classification model (MLP, Random Forest, and SVC) to score model integrity.",
      gradient: "from-purple-500/10 to-indigo-500/10",
      border: "border-purple-100",
    },
    {
      icon: <HelpCircle className="w-6 h-6 text-indigo-600" />,
      title: "Why We Did It",
      description: "Modern LLM safety relies heavily on prompt-filtering and output-checking, which are easily bypassed by jailbreaks or backdoor attacks. By analyzing the model's inner activations using causal interventions (skipping layer blocks and masking tokens), we expose the direct reasons behind LLM misbehavior.",
      gradient: "from-indigo-500/10 to-pink-500/10",
      border: "border-indigo-100",
    },
    {
      icon: <Users className="w-6 h-6 text-pink-600" />,
      title: "Who We Serve",
      description: "We support AI safety engineers, red-teaming units, enterprise developers, and researchers deploying large language models. Anyone who needs a transparent, real-time safety layer that guarantees secure and truthful LLM usage.",
      gradient: "from-pink-500/10 to-purple-500/10",
      border: "border-pink-100",
    },
    {
      icon: <Target className="w-6 h-6 text-teal-600" />,
      title: "Problem We Solve",
      description: "We solve the problem of LLM vulnerability to lies, jailbreaks, toxicity, and backdoor attacks. LLMSCAN detects these safety violations from causal activation states before the model starts generating harmful text, preventing damage before it occurs.",
      gradient: "from-teal-500/10 to-emerald-500/10",
      border: "border-teal-100",
    },
  ];

  return (
    <section id="about" className="py-24 bg-gray-50/50 border-t border-gray-100 scroll-mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-xs font-bold uppercase tracking-widest mb-4">
            Mission & Overview
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            About LLMSCAN
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A research-driven, causality-based audit engine designed to bring transparency and safety to LLM deployments.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {points.map((point, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5, scale: 1.01 }}
              className={`bg-white p-8 rounded-2xl border ${point.border} shadow-xl shadow-purple-900/5 relative overflow-hidden transition-all duration-300 flex flex-col justify-between`}
            >
              {/* Subtle background gradient splash */}
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${point.gradient} rounded-bl-full opacity-30 pointer-events-none`}></div>
              
              <div className="relative z-10 flex flex-col gap-4">
                <div className="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center border border-gray-100 shadow-sm">
                  {point.icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{point.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{point.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
