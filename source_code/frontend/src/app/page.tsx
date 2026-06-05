// Vercel build trigger
import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { CodeSnippet } from "@/components/landing/CodeSnippet";
import { Features } from "@/components/landing/Features";
import { About } from "@/components/landing/About";
import { Footer } from "@/components/landing/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <Hero />
      <CodeSnippet />
      <Features />
      <About />
      <Footer />
    </main>
  );
}
