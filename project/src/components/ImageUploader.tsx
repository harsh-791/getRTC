import React, { useState, useRef } from 'react';
import { Upload, ImagePlus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ImageUploaderProps {
  onImageSelected: (file: File) => void;
  disabled: boolean;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageSelected, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      handleFile(file);
    }
  };

  const handleFile = (file: File) => {
    if (file.type.startsWith('image/')) {
      setPreview(URL.createObjectURL(file));
      onImageSelected(file);
    }
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div
        className={`relative bg-white/10 backdrop-blur-lg border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
          isDragging 
            ? 'border-blue-400 bg-blue-50/20' 
            : 'border-gray-300/50 hover:border-blue-300/70 hover:bg-white/20'
        } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        style={{ minHeight: '280px' }}
      >
        <input
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
          ref={fileInputRef}
          disabled={disabled}
        />
        
        <AnimatePresence mode="wait">
          {preview ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="relative w-full h-full flex flex-col items-center"
            >
              <motion.img 
                src={preview} 
                alt="Preview"
                className="max-h-60 max-w-full object-contain rounded-lg shadow-lg mb-4"
                layoutId="uploadedImage"
              />
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-white/90 text-sm mt-2"
              >
                Image selected. {!disabled && "Click or drag to replace."}
              </motion.p>
            </motion.div>
          ) : (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center"
            >
              <motion.div
                className="flex flex-col items-center justify-center"
                animate={isDragging ? { scale: 1.05 } : { scale: 1 }}
              >
                <motion.div
                  animate={isDragging ? 
                    { y: [0, -10, 0], transition: { repeat: Infinity, duration: 1.5 } } : 
                    { y: 0 }
                  }
                >
                  {isDragging ? (
                    <Upload className="h-16 w-16 text-blue-400 mb-4" />
                  ) : (
                    <ImagePlus className="h-16 w-16 text-white/70 mb-4" />
                  )}
                </motion.div>
                <h3 className="text-xl font-medium text-white mb-2">
                  {isDragging ? 'Drop image here' : 'Upload Property Image'}
                </h3>
                <p className="text-white/70 text-sm mb-6 max-w-xs">
                  Drag and drop your image here, or click to select a file
                </p>
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="px-5 py-2.5 bg-blue-600/90 hover:bg-blue-700 text-white rounded-lg shadow-md transition-all duration-200"
                  disabled={disabled}
                >
                  <span className="flex items-center">
                    <Upload className="h-4 w-4 mr-2" />
                    Select Image
                  </span>
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ImageUploader;