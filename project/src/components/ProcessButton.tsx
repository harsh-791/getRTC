import React from 'react';
import { motion } from 'framer-motion';
import { CpuIcon } from 'lucide-react';

interface ProcessButtonProps {
  onClick: () => void;
  disabled: boolean;
}

const ProcessButton: React.FC<ProcessButtonProps> = ({ onClick, disabled }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full flex justify-center mt-6"
    >
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        className={`px-6 py-3 rounded-xl shadow-lg flex items-center justify-center text-white font-medium ${
          disabled
            ? 'bg-gray-400/80 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
        }`}
        onClick={onClick}
        disabled={disabled}
      >
        <CpuIcon className="mr-2 h-5 w-5" />
        Process Image
      </motion.button>
    </motion.div>
  );
};

export default ProcessButton;