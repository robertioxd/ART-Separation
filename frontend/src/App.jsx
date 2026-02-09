import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UploadZone } from './components/UploadZone';
import { ValidationView } from './components/ValidationView';
import { Maximize2, Zap } from 'lucide-react';

const API_BASE = "http://localhost:8000";

function App() {
  const [currentJobId, setCurrentJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState("idle"); // idle, uploading, processing, completed, error
  const [manifest, setManifest] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setJobStatus("uploading");
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_BASE}/jobs`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCurrentJobId(res.data.job_id);
      setJobStatus("processing");
    } catch (err) {
      console.error(err);
      setError("Upload failed. Please try again.");
      setJobStatus("idle");
    }
  };

  // Polling Logic
  useEffect(() => {
    if (jobStatus !== "processing" || !currentJobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/jobs/${currentJobId}`);
        if (res.data.status === "completed") {
          // Fetch the actual manifest content
          // The API returns manifest_url, but for MVP let's assume it returns the manifest directly or we fetch it.
          // Our backend currently returns {status: completed, manifest_url: ...}
          // We need to fetch that URL or just serve the JSON.
          // Let's cheat for MVP: reading the manifest JSON file via static files.
          // URL: http://localhost:8000/files/{jobId}/manifest.json

          const manifestRes = await axios.get(`${API_BASE}/files/${currentJobId}/manifest.json`);
          setManifest(manifestRes.data);
          setJobStatus("completed");
        }
      } catch (err) {
        console.error("Polling error", err);
        // Don't stop polling immediately on network hiccup, but maybe count errors?
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [currentJobId, jobStatus]);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/20">
      {/* Navbar */}
      <header className="border-b border-border/40 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary text-primary-foreground p-1.5 rounded-lg">
              <maximize2 className="w-5 h-5" />
            </div>
            <span className="font-bold text-xl tracking-tight">ChromaScreen <span className="text-primary text-sm font-normal opacity-80">v1.0</span></span>
          </div>
          <div className="flex items-center gap-4 text-sm font-medium text-muted-foreground">
            <span>Zero-RIP Engine</span>
            <div className="h-4 w-px bg-border" />
            <span className="flex items-center gap-1 text-green-500"><Zap className="w-3 h-3 fill-current" /> Online</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-6 py-12">
        <div className="max-w-5xl mx-auto space-y-12">

          {/* Hero Section (Only show when idle) */}
          {jobStatus === "idle" && (
            <div className="text-center space-y-4 mb-8">
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-br from-foreground to-muted-foreground bg-clip-text text-transparent">
                Separación de Color por IA
              </h1>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Sube tu diseño. Nuestra IA escalará, separará y tramará los colores automáticamente para serigrafía. Zero-RIP.
              </p>
            </div>
          )}

          {/* View Switching */}
          {jobStatus === "completed" && manifest ? (
            <ValidationView manifest={manifest} jobUrl={`${API_BASE}/files/${currentJobId}`} />
          ) : (
            <UploadZone
              onUpload={handleUpload}
              isUploading={jobStatus === "uploading" || jobStatus === "processing"}
              error={error}
            />
          )}

          {/* Processing State Indicator */}
          {jobStatus === "processing" && (
            <div className="text-center mt-8 space-y-3">
              <div className="inline-block relative">
                <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
              </div>
              <p className="text-muted-foreground font-medium animate-pulse">
                Procesando... (Escalado x4 + Pantone Matching + Ripping)
              </p>
            </div>
          )}

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 text-center text-sm text-muted-foreground">
        <p>© 2026 ChromaScreen AI. Built for Print.</p>
      </footer>
    </div>
  );
}

export default App;
