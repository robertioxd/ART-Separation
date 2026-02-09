import React, { useState, useEffect } from 'react';
import { Layers, Eye, EyeOff, Check, ZoomIn } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export function ValidationView({ manifest, jobUrl }) {
    const [layers, setLayers] = useState([]);
    const [activeLayers, setActiveLayers] = useState(new Set());
    const [zoom, setZoom] = useState(1);

    // Parse manifest separations
    useEffect(() => {
        if (manifest?.separations) {
            const parsed = manifest.separations.map((sep, idx) => ({
                id: `vis-${idx}`,
                name: sep.metadata?.shape ? `${sep.metadata.shape} ${sep.metadata.angle}°` : `Layer ${idx + 1}`,
                // Fix path: backend saves absolute path, we need to serve it relative or via API.
                // For MVP, assume backend serves files statically or specific endpoint.
                // Since we didn't setup static serving of 'temp_jobs' yet, this will break unless we fix backend.
                // Let's assume endpoint: /jobs/{jobId}/files/{filename}
                src: sep.output_path,
                color: "#000000", // Default black ink
                // If we had Pantone info here, we'd use it.
                ...sep
            }));
            setLayers(parsed);
            setActiveLayers(new Set(parsed.map(l => l.id)));
        }
    }, [manifest]);

    const toggleLayer = (id) => {
        const next = new Set(activeLayers);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        setActiveLayers(next);
    };

    return (
        <div className="w-full max-w-6xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Separation Preview</h2>
                    <p className="text-muted-foreground">Job ID: {manifest.job_id}</p>
                </div>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-lg text-sm font-medium hover:bg-secondary/80">
                        <ZoomIn className="w-4 h-4" /> Zoom {Math.round(zoom * 100)}%
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Layer Controls */}
                <div className="space-y-4 lg:col-span-1">
                    <div className="bg-card border rounded-xl p-4 space-y-3">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-4">
                            <Layers className="w-4 h-4" /> Layers ({layers.length})
                        </div>

                        {layers.map((layer) => (
                            <motion.div
                                key={layer.id}
                                layout
                                onClick={() => toggleLayer(layer.id)}
                                className={cn(
                                    "flex items-center gap-3 p-3 rounded-lg cursor-pointer border transition-all",
                                    activeLayers.has(layer.id)
                                        ? "bg-primary/5 border-primary/20"
                                        : "hover:bg-muted border-transparent opacity-60"
                                )}
                            >
                                <div
                                    className="w-4 h-4 rounded-full border shadow-sm"
                                    style={{ backgroundColor: layer.color }}
                                />
                                <span className="flex-1 text-sm font-medium truncate">{layer.name}</span>
                                {activeLayers.has(layer.id) ? (
                                    <Eye className="w-4 h-4 text-primary" />
                                ) : (
                                    <EyeOff className="w-4 h-4 text-muted-foreground" />
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Canvas / Composite View */}
                <div className="lg:col-span-3 bg-card border rounded-xl p-8 min-h-[500px] flex items-center justify-center relative overflow-hidden bg-[url('https://repo.antigravity.run/grid.png')]">
                    {/* Note: In real implementation, we would stack images using multiply blend mode CSS */}
                    <div className="relative shadow-2xl bg-white" style={{ width: '400px', height: '500px' }}> {/* Mock dimensions */}
                        {layers.map(layer => (
                            <img
                                key={layer.id}
                                src={`http://localhost:8000/files?path=${encodeURIComponent(layer.src)}`} // Temporary Hack for file serving
                                className={cn(
                                    "absolute inset-0 w-full h-full object-contain mix-blend-multiply transition-opacity duration-300",
                                    activeLayers.has(layer.id) ? "opacity-100" : "opacity-0"
                                )}
                                alt={layer.name}
                            />
                        ))}

                        {!layers.length && (
                            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
                                No layers to display
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
