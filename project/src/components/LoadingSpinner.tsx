import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  text?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ text = 'Processing image...' }) => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center py-8"
    >
      <div className="relative h-24 w-24">
        <motion.div
          className="absolute inset-0 rounded-full border-4 border-t-blue-500 border-r-purple-500 border-b-indigo-500 border-l-transparent"
          animate={{ rotate: 360 }}
          transition={{ 
            duration: 1.5, 
            repeat: Infinity, 
            ease: "linear" 
          }}
        />
        <motion.div
          className="absolute inset-2 rounded-full border-4 border-t-transparent border-r-blue-400 border-b-purple-400 border-l-indigo-400"
          animate={{ rotate: -180 }}
          transition={{ 
            duration: 2, 
            repeat: Infinity, 
            ease: "linear" 
          }}
        />
        <motion.div
          className="absolute inset-4 rounded-full border-4 border-t-indigo-300 border-r-transparent border-b-blue-300 border-l-purple-300"
          animate={{ rotate: 360 }}
          transition={{ 
            duration: 2.5, 
            repeat: Infinity, 
            ease: "linear" 
          }}
        />
      </div>
      
      <motion.p 
        className="mt-6 text-white text-lg font-medium"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {text}
      </motion.p>
      
      <motion.div 
        className="mt-3 text-white/60 text-sm max-w-md text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        We're analyzing your property image and extracting information. This may take a moment...
      </motion.div>
    </motion.div>
  );
};

export default LoadingSpinner;