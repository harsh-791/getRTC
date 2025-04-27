import React from 'react';
import { motion } from 'framer-motion';
import { FileImage } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full py-6 mb-8"
    >
      <motion.div 
        className="flex items-center justify-center"
        whileHover={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 400, damping: 10 }}
      >
        <motion.div
          animate={{ 
            rotate: [0, 10, 0, -10, 0],
            transition: { duration: 2, repeat: Infinity, ease: "easeInOut" }
          }}
        >
          <FileImage className="h-8 w-8 text-blue-400 mr-3" />
        </motion.div>
        <h1 className="text-2xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-300 to-purple-300">
          Property Image Processor
        </h1>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="text-center mt-3 max-w-2xl mx-auto"
      >
        <p className="text-white/70 text-sm md:text-base">
          Upload property images to extract survey details and view historical records
        </p>
      </motion.div>
    </motion.header>
  );
};

export default Header;