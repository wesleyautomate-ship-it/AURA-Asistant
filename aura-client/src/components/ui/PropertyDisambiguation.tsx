/**
 * Property Disambiguation Component
 * =================================
 * 
 * Shows property selection dialog when multiple matches are found
 * during brochure generation
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, MapPin, DollarSign, X } from 'lucide-react';
import { PropertyMatch } from '../../utils/brochureProgressSteps';

interface PropertyDisambiguationProps {
  isOpen: boolean;
  matches: PropertyMatch[];
  query: string;
  message: string;
  onSelect: (propertyId: string) => void;
  onCancel: () => void;
  loading?: boolean;
}

export const PropertyDisambiguation: React.FC<PropertyDisambiguationProps> = ({
  isOpen,
  matches,
  query,
  message,
  onSelect,
  onCancel,
  loading = false,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
        onClick={onCancel}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', duration: 0.5 }}
          className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Select Property
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Found {matches.length} properties matching "{query}"
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors"
              disabled={loading}
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>

          {/* Message */}
          {message && (
            <div className="px-6 py-4 bg-blue-50 border-b border-gray-100">
              <p className="text-sm text-blue-800">{message}</p>
            </div>
          )}

          {/* Property List */}
          <div className="p-6 max-h-96 overflow-y-auto">
            <div className="space-y-3">
              {matches.map((property, index) => (
                <motion.button
                  key={property.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => onSelect(property.id)}
                  disabled={loading}
                  className="w-full p-4 text-left bg-gray-50 hover:bg-blue-50 rounded-xl border border-gray-200 hover:border-blue-200 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 group-hover:text-blue-900 transition-colors mb-2">
                        {property.title}
                      </h3>
                      
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        {property.address && (
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            <span>{property.address}</span>
                          </div>
                        )}
                        
                        {property.price && (
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            <span>{property.price}</span>
                          </div>
                        )}
                        
                        {property.property_type && (
                          <div className="flex items-center gap-1">
                            <Building2 className="w-3 h-3" />
                            <span>{property.property_type}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="w-8 h-8 bg-blue-100 group-hover:bg-blue-200 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 text-sm font-medium">
                          {index + 1}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-100 bg-gray-50">
            <p className="text-xs text-gray-500">
              Select a property to continue with brochure generation
            </p>
            <div className="flex gap-3">
              <button
                onClick={onCancel}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PropertyDisambiguation;