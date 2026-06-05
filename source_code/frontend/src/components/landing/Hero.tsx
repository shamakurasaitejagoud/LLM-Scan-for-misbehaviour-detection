"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Play } from "lucide-react";
import { SplineSceneBasic } from "./SplineSceneBasic";

export function Hero() {
  return (
    <section id="home" className="relative pt-32 pb-16 md:pt-40 md:pb-24 min-h-[800px] overflow-hidden flex items-center scroll-mt-20">
      
      {/* Full-page Spline Background */}
      <div className="absolute inset-0 w-full h-full z-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-y-0 right-0 w-full lg:w-[50vw] z-0 pointer-events-none">
          <SplineSceneBasic />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full pointer-events-none">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Text Content */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="max-w-2xl pointer-events-auto"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 border border-purple-100 text-purple-600 text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              <span>Brain-Scanning LLMs using Causality</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-gray-900 mb-6 leading-[1.1]">
              Causal Scan for <br className="hidden md:block" />
              LLM Misbehavior Detection
            </h1>
            
            <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-lg leading-relaxed">
              LLMSCAN systematically monitors the inner workings of an LLM through the lens of causal inference. By analyzing the causal contributions of input tokens and transformer layers, it proactively detects lies, jailbreaks, toxicity, and backdoor attacks.
            </p>
            
            <div className="flex flex-wrap items-center gap-4">
              <motion.a 
                href="https://github.com/shamakurasaitejagoud/LLM-Scan-for-misbehaviour-detection"
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-purple-600 text-white px-6 py-3 rounded-full font-medium shadow-lg shadow-purple-500/30 hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                View on GitHub
                <span>✨</span>
              </motion.a>
              
              <motion.div 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  href="/chat"
                  className="bg-white text-gray-700 border border-gray-200 px-6 py-3 rounded-full font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
                >
                  Get Started
                  <Play className="w-4 h-4 text-purple-600" />
                </Link>
              </motion.div>
            </div>
            
            <div className="mt-8 flex gap-2 flex-wrap">
               {['Lie Detection', 'Jailbreak Detection', 'Toxicity Detection', 'Backdoor Detection'].map((tag) => (
                 <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-md border border-gray-200">
                   {tag}
                 </span>
               ))}
            </div>
          </motion.div>

          {/* Right side is intentionally empty to let the Spline scene show through from the background */}
          <div className="hidden lg:block h-[400px] md:h-[600px] w-full pointer-events-none"></div>

        </div>
      </div>
    </section>
  );
}
