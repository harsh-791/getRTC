import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onDismiss: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onDismiss }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full backdrop-blur-md bg-red-600/20 border border-red-400/50 rounded-lg p-4 mb-6 shadow-lg"
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-white">{message}</p>
        </div>
        <button
          type="button"
          className="bg-red-400/10 rounded-md p-1.5 hover:bg-red-400/20 transition-colors"
          onClick={onDismiss}
        >
          <X className="h-4 w-4 text-red-300" />
        </button>
      </div>
    </motion.div>
  );
};

export default ErrorMessage;