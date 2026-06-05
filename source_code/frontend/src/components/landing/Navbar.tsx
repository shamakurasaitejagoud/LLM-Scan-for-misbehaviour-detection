"use client";

import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, LogOut } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { LoginModal } from "./LoginModal";
import { useSession, signOut } from "next-auth/react";

export function Navbar() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("home");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { data: session } = useSession();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const sectionIds = ["home", "methodology", "evaluations", "about"];
    
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 180;

      // Special case: check if we reached the bottom of the page
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 80) {
        setActiveSection("about");
        return;
      }

      for (const id of sectionIds) {
        const el = document.getElementById(id);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(id);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-8 h-8 text-purple-600" />
              <span className="font-bold text-xl tracking-tight text-gray-900">LLM Scan</span>
            </div>

            {/* Nav Links */}
            <nav className="hidden md:flex space-x-8">
              <Link 
                href="#home" 
                className={`text-sm font-semibold transition-all duration-200 border-b-2 py-1 ${
                  activeSection === "home" 
                    ? "text-purple-600 border-purple-600" 
                    : "text-gray-500 hover:text-gray-900 border-transparent"
                }`}
              >
                Home
              </Link>
              <Link 
                href="#methodology" 
                className={`text-sm font-semibold transition-all duration-200 border-b-2 py-1 ${
                  activeSection === "methodology" 
                    ? "text-purple-600 border-purple-600" 
                    : "text-gray-500 hover:text-gray-900 border-transparent"
                }`}
              >
                Methodology
              </Link>
              <Link 
                href="#performance-plots" 
                className={`text-sm font-semibold transition-all duration-200 border-b-2 py-1 ${
                  activeSection === "evaluations" 
                    ? "text-purple-600 border-purple-600" 
                    : "text-gray-500 hover:text-gray-900 border-transparent"
                }`}
              >
                Performance
              </Link>
              <Link 
                href="#about" 
                className={`text-sm font-semibold transition-all duration-200 border-b-2 py-1 ${
                  activeSection === "about" 
                    ? "text-purple-600 border-purple-600" 
                    : "text-gray-500 hover:text-gray-900 border-transparent"
                }`}
              >
                About
              </Link>
            </nav>

            {/* CTA Buttons */}
            <div className="flex items-center gap-4">
              {session?.user ? (
                <div className="flex items-center gap-4">
                  <div className="relative" ref={dropdownRef}>
                    <div 
                      className="cursor-pointer"
                      onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    >
                      {/* Outer colorful ring (Rainbow Colors) */}
                      <div 
                        className="w-10 h-10 rounded-full flex items-center justify-center p-[2px]"
                        style={{ background: "conic-gradient(from 0deg, #ff0000, #ff8000, #ffff00, #00ff00, #00ffff, #0000ff, #8000ff, #ff00ff, #ff0000)" }}
                      >
                        {/* Gap between ring and avatar */}
                        <div className="w-full h-full bg-white rounded-full flex items-center justify-center p-[2px]">
                          {/* Avatar */}
                          <div className="w-full h-full bg-[#7B1FA2] rounded-full flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                              {session.user.email?.charAt(0).toUpperCase() || session.user.name?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Dropdown Menu */}
                    <AnimatePresence>
                      {isDropdownOpen && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 10 }}
                          className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
                        >
                          <div className="p-4 border-b border-gray-100">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {session.user.name || session.user.email?.split('@')[0]}
                            </p>
                            <p className="text-xs text-gray-500 truncate mt-1">
                              {session.user.email}
                            </p>
                          </div>
                          <div className="p-2">
                            <button
                              onClick={() => signOut({ callbackUrl: '/' })}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
                            >
                              <LogOut className="w-4 h-4" />
                              Sign out
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Link
                      href="/chat"
                      className="bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium shadow-md shadow-purple-500/20 hover:bg-purple-700 transition-colors inline-block"
                    >
                      Get Started
                    </Link>
                  </motion.div>
                </div>
              ) : (
                <>
                  <button 
                    onClick={() => setIsLoginOpen(true)}
                    className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Log in
                  </button>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Link
                      href="/chat"
                      className="bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium shadow-md shadow-purple-500/20 hover:bg-purple-700 transition-colors inline-block"
                    >
                      Get Started
                    </Link>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <LoginModal 
        isOpen={isLoginOpen} 
        onClose={() => setIsLoginOpen(false)} 
        onLoginSuccess={() => {
          setIsLoginOpen(false);
        }}
      />
    </>
  );
}
