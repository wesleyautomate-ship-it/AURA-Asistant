import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, Image } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as ImagePicker from 'expo-image-picker';

import { Document } from '@propertypro/features/types';

export type DocumentManagerProps = {
  documents: Document[];
  onDocumentsChange?: (documents: Document[]) => void;
  readOnly?: boolean;
};

const DocumentManager: React.FC<DocumentManagerProps> = ({
  documents = [],
  onDocumentsChange,
  readOnly = false,
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const pickDocument = async () => {
    if (isUploading || readOnly) return;

    try {
      setIsUploading(true);

      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*',
        copyToCacheDirectory: true,
      });

      if (result.type === 'success') {
        const fileInfo = await FileSystem.getInfoAsync(result.uri);

        if (fileInfo.exists) {
          const newDocument: Document = {
            id: Date.now().toString(),
            name: result.name,
            type: result.mimeType || 'application/octet-stream',
            url: result.uri,
            uploadedAt: new Date().toISOString(),
            size: fileInfo.size || 0,
          };

          onDocumentsChange?.([...documents, newDocument]);
        }
      }
    } catch (error) {
      console.error('Error picking document:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const takePhoto = async () => {
    if (isUploading || readOnly) return;

    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();

      if (!permissionResult.granted) {
        alert('Camera permission is required to take photos');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.cancelled) {
        const fileInfo = await FileSystem.getInfoAsync(result.uri);

        if (fileInfo.exists) {
          const newDocument: Document = {
            id: Date.now().toString(),
            name: `photo-${Date.now()}.jpg`,
            type: 'image/jpeg',
            url: result.uri,
            uploadedAt: new Date().toISOString(),
            size: fileInfo.size || 0,
          };

          onDocumentsChange?.([...documents, newDocument]);
        }
      }
    } catch (error) {
      console.error('Error taking photo:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const removeDocument = (id: string) => {
    if (readOnly) return;
    onDocumentsChange?.(documents.filter((doc) => doc.id !== id));
  };

  const renderDocument = ({ item }: { item: Document }) => {
    const isImage = item.type.startsWith('image/');
    const fileSize = (item.size / 1024).toFixed(1);

    return (
      <View style={styles.documentItem}>
        <View style={styles.documentIconContainer}>
          {isImage ? (
            <Image source={{ uri: item.url }} style={styles.documentThumbnail} />
          ) : (
            <MaterialIcons name="insert-drive-file" size={32} color="#6b7280" />
          )}
        </View>

        <View style={styles.documentInfo}>
          <Text style={styles.documentName} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={styles.documentMeta}>
            {item.type.split('/')[1]?.toUpperCase() || 'FILE'} - {fileSize} KB
          </Text>
        </View>

        <View style={styles.documentActions}>
          {!readOnly && (
            <TouchableOpacity style={[styles.iconButton, styles.removeButton]} onPress={() => removeDocument(item.id)}>
              <MaterialIcons name="delete-outline" size={22} color="#b91c1c" />
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Documents</Text>
        {!readOnly && (
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.actionButton, styles.uploadButton]}
              onPress={pickDocument}
              disabled={isUploading}
            >
              <MaterialIcons name="upload" size={18} color="#fff" />
              <Text style={styles.uploadButtonText}>{isUploading ? 'Uploading...' : 'Upload'}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.actionButton, styles.cameraButton]}
              onPress={takePhoto}
              disabled={isUploading}
            >
              <MaterialIcons name="photo-camera" size={18} color="#fff" />
            </TouchableOpacity>
          </View>
        )}
      </View>

      {!documents?.length ? (
        <View style={styles.emptyState}>
          <MaterialIcons name="cloud-upload" size={42} color="#9ca3af" />
          <Text style={styles.emptyStateText}>No documents yet</Text>
          {!readOnly && (
            <Text style={styles.emptyStateSubtext}>Upload files or take photos to get started</Text>
          )}
        </View>
      ) : (
        <FlatList
          data={documents}
          renderItem={renderDocument}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.documentsList}
          scrollEnabled={documents.length > 2}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 6,
    borderRadius: 6,
    marginLeft: 8,
  },
  uploadButton: {
    backgroundColor: '#ea580c',
    paddingHorizontal: 12,
  },
  cameraButton: {
    backgroundColor: '#4b5563',
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  emptyState: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyStateText: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
    fontWeight: '500',
  },
  emptyStateSubtext: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 4,
  },
  documentsList: {
    paddingBottom: 16,
  },
  documentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  documentIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 6,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    overflow: 'hidden',
  },
  documentThumbnail: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  documentInfo: {
    flex: 1,
    marginRight: 12,
    minWidth: 0,
  },
  documentName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 2,
  },
  documentMeta: {
    fontSize: 11,
    color: '#9ca3af',
  },
  documentActions: {
    flexDirection: 'row',
  },
  iconButton: {
    padding: 6,
    borderRadius: 6,
  },
  removeButton: {
    backgroundColor: '#fee2e2',
  },
});

export default DocumentManager;
