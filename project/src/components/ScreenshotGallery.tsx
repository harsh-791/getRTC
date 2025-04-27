import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Image,
  ExternalLink,
  Calendar,
  Download,
  ZoomIn,
} from "lucide-react";
import { Screenshot } from "../types";

interface ScreenshotGalleryProps {
  screenshots: Screenshot[];
}

const ScreenshotGallery: React.FC<ScreenshotGalleryProps> = ({
  screenshots,
}) => {
  const [selectedImage, setSelectedImage] = useState<Screenshot | null>(null);
  const [isZoomed, setIsZoomed] = useState(false);

  if (screenshots.length === 0) {
    return null;
  }

  const getYearFromFilename = (filename: string): string => {
    // Extract year from filename if possible, or return a placeholder
    const match = filename.match(/\b(19|20)\d{2}\b/);
    return match ? match[0] : "Year Data";
  };

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Error downloading image:", error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full mt-10"
    >
      <div className="flex items-center mb-6">
        <Calendar className="h-6 w-6 text-blue-400 mr-2" />
        <h2 className="text-xl font-semibold text-white">
          Available Year Records
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {screenshots.map((screenshot, index) => (
          <motion.div
            key={screenshot.name}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="group relative overflow-hidden rounded-xl backdrop-blur-lg bg-white/10 border border-white/20 shadow-lg hover:shadow-xl transition-shadow duration-300"
          >
            <div className="p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-purple-400 mr-2" />
                  <h3 className="text-lg font-medium text-white">
                    {getYearFromFilename(screenshot.name)}
                  </h3>
                </div>
                <div className="flex gap-2">
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-1 rounded-full bg-white/10 cursor-pointer"
                    onClick={() =>
                      handleDownload(screenshot.url, screenshot.name)
                    }
                  >
                    <Download className="h-4 w-4 text-green-300" />
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-1 rounded-full bg-white/10 cursor-pointer"
                    onClick={() => setSelectedImage(screenshot)}
                  >
                    <ZoomIn className="h-4 w-4 text-blue-300" />
                  </motion.div>
                </div>
              </div>

              <div
                className="relative h-48 rounded-lg overflow-hidden bg-black/20 cursor-pointer"
                onClick={() => setSelectedImage(screenshot)}
              >
                <img
                  src={screenshot.url}
                  alt={screenshot.name}
                  className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-3">
                  <span className="text-white text-sm font-medium truncate">
                    {screenshot.name}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md"
            onClick={() => {
              setIsZoomed(false);
              setSelectedImage(null);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="relative max-w-6xl w-full rounded-xl overflow-hidden bg-gray-900/95 shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center p-4 border-b border-white/10">
                <h3 className="text-xl font-medium text-white flex items-center">
                  <Image className="h-5 w-5 mr-2 text-blue-400" />
                  {selectedImage.name}
                </h3>
                <div className="flex gap-2">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() =>
                      handleDownload(selectedImage.url, selectedImage.name)
                    }
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2 text-white/70"
                  >
                    <Download className="h-5 w-5" />
                    <span>Download</span>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setIsZoomed(!isZoomed)}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2 text-white/70"
                  >
                    <ZoomIn className="h-5 w-5" />
                    <span>{isZoomed ? "Zoom Out" : "Zoom In"}</span>
                  </motion.button>
                  <button
                    onClick={() => {
                      setIsZoomed(false);
                      setSelectedImage(null);
                    }}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <X className="h-5 w-5 text-white/70" />
                  </button>
                </div>
              </div>
              <div className="p-4">
                <motion.img
                  src={selectedImage.url}
                  alt={selectedImage.name}
                  className={`w-full h-auto ${
                    isZoomed ? "max-h-[90vh]" : "max-h-[70vh]"
                  } object-contain rounded transition-all duration-300`}
                  animate={{
                    scale: isZoomed ? 1.1 : 1,
                    transition: { type: "spring", damping: 25, stiffness: 300 },
                  }}
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ScreenshotGallery;
