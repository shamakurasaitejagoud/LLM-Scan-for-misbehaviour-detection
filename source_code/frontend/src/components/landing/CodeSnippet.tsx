"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Terminal, Cpu, Network, LineChart, ShieldAlert, Sliders, Check, Database, FileText, Binary, Layers } from "lucide-react";
import { useState } from "react";

export function CodeSnippet() {
  const [activeTab, setActiveTab] = useState<"architecture" | "pipeline" | "ensemble">("architecture");

  const architectureSteps = [
    {
      icon: <Terminal className="w-5 h-5 text-purple-600" />,
      title: "1. Next.js Frontend",
      desc: "User submits prompt. Client checks JWT session and sends HTTP POST to /scan.",
      bg: "bg-purple-50/30"
    },
    {
      icon: <Database className="w-5 h-5 text-indigo-600" />,
      title: "2. FastAPI Backend",
      desc: "Authenticates session, manages MongoDB logs, and calls full_scan() on the model engine.",
      bg: "bg-indigo-50/30"
    },
    {
      icon: <Cpu className="w-5 h-5 text-pink-600" />,
      title: "3. MistralScanner Engine",
      desc: "Initializes Mistral-7B-Instruct-v0.2 with 4-bit NF4 quantization and registers hooks.",
      bg: "bg-pink-50/30"
    },
    {
      icon: <Network className="w-5 h-5 text-teal-600" />,
      title: "4. AIE Causal Auditing",
      desc: "Computes Layer logit-difference via skipping blocks, and Token causal weights via masking.",
      bg: "bg-teal-50/30"
    },
    {
      icon: <ShieldAlert className="w-5 h-5 text-red-600" />,
      title: "5. Stacked Ensemble Classifier",
      desc: "Processes causal features with stacked MLP + Random Forest + SVC to determine security threat.",
      bg: "bg-red-50/30"
    },
    {
      icon: <Check className="w-5 h-5 text-green-600" />,
      title: "6. MongoDB Logger & View",
      desc: "Logs prompt history, generated response, and safety metrics to database and Next.js frontend.",
      bg: "bg-green-50/30"
    }
  ];

  const pipelineSteps = [
    {
      icon: <FileText className="w-5 h-5 text-purple-600" />,
      title: "1. Input Prompt",
      desc: "Receives raw text query (jailbreak attempts, lies, backdoor triggers, etc.).",
      bg: "bg-purple-50/30"
    },
    {
      icon: <Layers className="w-5 h-5 text-indigo-600" />,
      title: "2. Hook Intercepts",
      desc: "HuggingFace forward hooks capture intermediate layer activations.",
      bg: "bg-indigo-50/30"
    },
    {
      icon: <Network className="w-5 h-5 text-pink-600" />,
      title: "3. Causal Feature Slice",
      desc: "Computes layer-wise causal logit-difference slices (layers 10-30).",
      bg: "bg-pink-50/30"
    },
    {
      icon: <Binary className="w-5 h-5 text-teal-600" />,
      title: "4. Feature Augmentation",
      desc: "Applies Log, Square, Sign, Diff transformations to expand features to 126 dimensions.",
      bg: "bg-teal-50/30"
    },
    {
      icon: <Sliders className="w-5 h-5 text-yellow-600" />,
      title: "5. MinMaxScaler Transformation",
      desc: "Normalizes the augmented 126-D feature vector to align with model training bounds.",
      bg: "bg-yellow-50/30"
    },
    {
      icon: <ShieldAlert className="w-5 h-5 text-red-600" />,
      title: "6. Ensemble Classifier & Report",
      desc: "Stacked MLP, RF, and SVC models output final class probabilities (Jailbreak, Lies, etc.).",
      bg: "bg-red-50/30"
    }
  ];

  const stepsData = activeTab === "architecture" ? architectureSteps : pipelineSteps;

  return (
    <section id="methodology" className="py-24 bg-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-50 rounded-full blur-3xl opacity-50 z-0 pointer-events-none"></div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-xs font-bold uppercase tracking-widest mb-4">
            Core Architecture
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            How LLMSCAN Detects Misbehavior
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Instead of treating language models as black boxes, LLMSCAN uses runtime Activation Intervention Evaluation (AIE) to diagnose safety threats from internal layer signals.
          </p>
        </div>

        <div className="w-full mb-20">
          {/* Tab Switched Header */}
          <div className="flex bg-gray-100 p-1 rounded-xl gap-1 mb-6 w-full border border-gray-200">
            <button
              onClick={() => setActiveTab("architecture")}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-300 ${activeTab === "architecture"
                ? "bg-white text-purple-600 shadow-sm border border-gray-100"
                : "text-gray-500 hover:text-gray-900"
                }`}
            >
              System Architecture Flow
            </button>
            <button
              onClick={() => setActiveTab("pipeline")}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-300 ${activeTab === "pipeline"
                ? "bg-white text-purple-600 shadow-sm border border-gray-100"
                : "text-gray-500 hover:text-gray-900"
                }`}
            >
              Feature Pipeline Flow
            </button>
            <button
              onClick={() => setActiveTab("ensemble")}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-300 ${activeTab === "ensemble"
                ? "bg-white text-purple-600 shadow-sm border border-gray-100"
                : "text-gray-500 hover:text-gray-900"
                }`}
            >
              Ensemble Pipeline
            </button>
          </div>

          <div className="mt-8">
            <AnimatePresence mode="wait">
              {activeTab !== "ensemble" ? (
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.2 }}
                  className="max-w-2xl mx-auto w-full flex flex-col"
                >
                  <div className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-sm min-h-[580px] flex flex-col justify-center">
                    <div className="relative flex-1 pl-6 border-l-2 border-purple-100 ml-3 space-y-4 my-2">
                      {stepsData.map((step, i) => (
                        <div
                          key={step.title}
                          className={`relative p-3 rounded-xl border border-gray-100 hover:border-purple-200 hover:shadow-md hover:shadow-purple-500/5 transition-all duration-300 ${step.bg}`}
                        >
                          {/* Connector Circle */}
                          <div className="absolute -left-[32px] top-1/2 -translate-y-1/2 w-4.5 h-4.5 rounded-full bg-white border-2 border-purple-500 flex items-center justify-center shadow-sm">
                            <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                          </div>

                          <div className="flex gap-3 items-center">
                            <div className="flex-shrink-0 p-2 rounded-lg bg-white shadow-sm border border-gray-100 flex items-center justify-center">
                              {step.icon}
                            </div>
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-0.5">{step.title}</h4>
                              <p className="text-xs text-gray-500 leading-normal">{step.desc}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="ensemble-table"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.2 }}
                  className="w-full space-y-6"
                >
                  <h3 className="text-xl font-semibold text-gray-900 mb-6">
                    Ensemble Pipeline Specifications
                  </h3>

                  <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              Level / Stage
                            </th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              Component
                            </th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              Optimization / Solvers
                            </th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              Parameters
                            </th>
                            <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                              Output Properties
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-100">
                          {[
                            {
                              stage: "Input Layer",
                              comp: "Data Preprocessing",
                              opt: "Standard / Min-Max Scaling",
                              params: "X ∈ ℝ¹²⁶",
                              out: "Uniform scale (mean = 0, var = 1)"
                            },
                            {
                              stage: "Level-0 Base",
                              comp: "Multi-Layer Perceptron (MLP)",
                              opt: "Adam Optimizer / Cross-Entropy Loss",
                              params: "24,642 weights & biases",
                              out: "Overconfident raw uncalibrated logits"
                            },
                            {
                              stage: "Level-0 Base",
                              comp: "Random Forest (RF)",
                              opt: "Bagging / Gini Impurity & Info Gain",
                              params: "≈204,600 split thresholds",
                              out: "Discrete vote fractions"
                            },
                            {
                              stage: "Level-0 Base",
                              comp: "Support Vector Classifier (SVC)",
                              opt: "Sequential Minimal Optimization / Hinge Loss",
                              params: "127 weights + support vectors",
                              out: "Infinite range margin distances ([-∞, +∞])"
                            },
                            {
                              stage: "Level-1 Calibrate",
                              comp: "CalibratedClassifierCV",
                              opt: "Platt Scaling via Maximum Likelihood Estimation",
                              params: "6 parameters per channel (A,B × 3 folds)",
                              out: "Mathematically sound posterior probabilities"
                            },
                            {
                              stage: "Level-1 Stack",
                              comp: "Meta-Classifier",
                              opt: "Weighted Logistic Regression / Consensus Layer",
                              params: "Optimized meta-weights (wm) + bias",
                              out: "Single, stable threat metric bounded to [0,1]"
                            }
                          ].map((row, idx) => (
                            <tr key={idx} className="hover:bg-purple-50/20 transition-colors">
                              <td className="px-4 py-3 text-xs font-semibold text-purple-700 whitespace-nowrap">
                                {row.stage}
                              </td>
                              <td className="px-4 py-3 text-xs font-medium text-gray-900 whitespace-nowrap">
                                {row.comp}
                              </td>
                              <td className="px-4 py-3 text-xs text-gray-500 whitespace-normal min-w-[150px]">
                                {row.opt}
                              </td>
                              <td className="px-4 py-3 text-xs text-indigo-600 font-mono whitespace-nowrap">
                                {row.params}
                              </td>
                              <td className="px-4 py-3 text-xs text-gray-600 whitespace-normal min-w-[150px]">
                                {row.out}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

      </div>
    </section>
  );
}
