import React from 'react';
import { motion } from 'framer-motion';
import { Info, MapPin, FileText } from 'lucide-react';
import { ExtractedInfo } from '../types';

interface ExtractedInfoCardProps {
  data: ExtractedInfo;
}

const ExtractedInfoCard: React.FC<ExtractedInfoCardProps> = ({ data }) => {
  const infoGroups = [
    { 
      title: 'Property Details', 
      icon: <FileText className="h-5 w-5 text-blue-400" />,
      fields: ['Survey Number', 'Surnoc', 'Hissa'] 
    },
    { 
      title: 'Location', 
      icon: <MapPin className="h-5 w-5 text-purple-400" />,
      fields: ['Village', 'Hobli', 'Taluk', 'District'] 
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full backdrop-blur-lg bg-white/10 rounded-xl shadow-lg p-6 mt-8 border border-white/20"
    >
      <div className="flex items-center mb-4">
        <Info className="h-6 w-6 text-blue-400 mr-2" />
        <h2 className="text-xl font-semibold text-white">Extracted Information</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {infoGroups.map((group, index) => (
          <motion.div
            key={group.title}
            initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 + (index * 0.1) }}
            className="bg-white/5 rounded-lg p-4 backdrop-blur-sm border border-white/10"
          >
            <div className="flex items-center mb-3">
              {group.icon}
              <h3 className="text-lg font-medium text-white ml-2">{group.title}</h3>
            </div>
            
            <div className="space-y-3">
              {group.fields.map(field => (
                <div key={field} className="flex flex-col">
                  <span className="text-xs text-white/60 mb-1">{field}</span>
                  <span className="text-white font-medium bg-white/5 rounded px-3 py-2 truncate">
                    {data[field as keyof ExtractedInfo] || 'N/A'}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default ExtractedInfoCard;