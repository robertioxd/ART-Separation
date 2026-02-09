import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileImage, AlertCircle } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export function UploadZone({ onUpload, isUploading, error }) {
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles?.length > 0) {
            onUpload(acceptedFiles[0]);
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.webp']
        },
        maxFiles: 1,
        disabled: isUploading
    });

    return (
        <div className="w-full max-w-xl mx-auto">
            <motion.div
                layout
                {...getRootProps()}
                className={cn(
                    "relative border-2 border-dashed rounded-xl p-12 transition-all duration-200 cursor-pointer overflow-hidden",
                    isDragActive ? "border-primary bg-primary/5 scale-[1.02]" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
                    isUploading && "opacity-50 cursor-not-allowed pointer-events-none"
                )}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center justify-center text-center gap-4">
                    <div className={cn(
                        "p-4 rounded-full transition-colors",
                        isDragActive ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                    )}>
                        {isUploading ? (
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                            >
                                <div className="w-8 h-8 border-2 border-current border-t-transparent rounded-full" />
                            </motion.div>
                        ) : (
                            <UploadCloud className="w-8 h-8" />
                        )}
                    </div>

                    <div className="space-y-1">
                        <h3 className="font-semibold text-lg tracking-tight">
                            {isUploading ? "Uploading & Processing..." : "Upload Artwork"}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            {isDragActive ? "Drop your masterpiece here" : "Drag & drop or click to browse"}
                        </p>
                    </div>
                </div>

                {isDragActive && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="absolute inset-0 bg-primary/5 backdrop-blur-[1px]"
                    />
                )}
            </motion.div>

            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mt-4 p-4 rounded-lg bg-destructive/10 text-destructive flex items-center gap-3 border border-destructive/20"
                    >
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p className="text-sm font-medium">{error}</p>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
