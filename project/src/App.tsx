import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { processImage, getScreenshots } from './services/api';
import { ExtractedInfo, Screenshot } from './types';
import ImageUploader from './components/ImageUploader';
import ProcessButton from './components/ProcessButton';
import LoadingSpinner from './components/LoadingSpinner';
import ExtractedInfoCard from './components/ExtractedInfoCard';
import ScreenshotGallery from './components/ScreenshotGallery';
import Background from './components/Background';
import ErrorMessage from './components/ErrorMessage';
import Header from './components/Header';

function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedInfo, setExtractedInfo] = useState<ExtractedInfo | null>(null);
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [recordId, setRecordId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);

  // Handle image processing
  const handleProcessImage = async () => {
    if (!selectedImage) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await processImage(selectedImage);
      
      if (response.success) {
        setExtractedInfo(response.extracted_info);
        setScreenshots(response.screenshots || []);
        setRecordId(response.record_id);
      } else {
        setError(response.message || 'Failed to process image');
      }
    } catch (err) {
      setError('An error occurred while processing the image. Please try again.');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Set up screenshot polling
  useEffect(() => {
    if (recordId) {
      // Initial fetch
      fetchScreenshots();
      
      // Set up polling every 5 seconds
      const interval = window.setInterval(fetchScreenshots, 5000);
      setPollingInterval(interval);
      
      return () => {
        if (pollingInterval) {
          clearInterval(pollingInterval);
        }
      };
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recordId]);

  // Clean up polling when component unmounts
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // Fetch screenshots from API
  const fetchScreenshots = async () => {
    if (!recordId) return;
    
    try {
      const response = await getScreenshots(recordId);
      
      if (response.success && response.screenshots) {
        setScreenshots(response.screenshots);
      }
    } catch (err) {
      console.error('Error fetching screenshots:', err);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden text-white">
      <Background />
      
      <div className="container mx-auto px-4 py-8 max-w-5xl relative z-10">
        <Header />
        
        <AnimatePresence>
          {error && (
            <ErrorMessage 
              message={error} 
              onDismiss={() => setError(null)} 
            />
          )}
        </AnimatePresence>
        
        <motion.div 
          className="backdrop-blur-lg bg-white/5 rounded-2xl shadow-xl border border-white/10 p-6 md:p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {isProcessing ? (
            <LoadingSpinner />
          ) : (
            <>
              <ImageUploader 
                onImageSelected={setSelectedImage} 
                disabled={isProcessing} 
              />
              
              {selectedImage && (
                <ProcessButton 
                  onClick={handleProcessImage} 
                  disabled={!selectedImage || isProcessing} 
                />
              )}
            </>
          )}
          
          {extractedInfo && !isProcessing && (
            <ExtractedInfoCard data={extractedInfo} />
          )}
        </motion.div>
        
        {screenshots.length > 0 && !isProcessing && (
          <ScreenshotGallery screenshots={screenshots} />
        )}
      </div>
    </div>
  );
}

export default App;