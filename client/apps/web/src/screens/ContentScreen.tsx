import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity } from 'react-native';

const TYPES = ['description', 'social', 'email', 'brochure'] as const;
const TONES = ['professional', 'casual', 'luxury', 'friendly'] as const;

export default function ContentScreen() {
  const [contentType, setContentType] = useState<typeof TYPES[number]>('description');
  const [tone, setTone] = useState<typeof TONES[number]>('professional');
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');

  const generate = () => {
    const base = `Type: ${contentType} | Tone: ${tone}`;
    const body = prompt ? `\n\nDraft based on your prompt:\n${prompt}` : '\n\nDraft based on starter template.';
    setOutput(`${base}${body}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Content Generator</Text>

      <Text style={styles.label}>Content Type</Text>
      <View style={styles.row}>
        {TYPES.map(t => (
          <TouchableOpacity key={t} onPress={() => setContentType(t)} style={[styles.pill, contentType === t && styles.pillActive]}>
            <Text style={[styles.pillText, contentType === t && styles.pillTextActive]}>{t}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Tone</Text>
      <View style={styles.row}>
        {TONES.map(t => (
          <TouchableOpacity key={t} onPress={() => setTone(t)} style={[styles.pill, tone === t && styles.pillActive]}>
            <Text style={[styles.pillText, tone === t && styles.pillTextActive]}>{t}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Prompt</Text>
      <TextInput
        placeholder="Describe what you want to generate..."
        value={prompt}
        onChangeText={setPrompt}
        style={styles.textarea}
        multiline
      />

      <TouchableOpacity onPress={generate} style={styles.generateBtn}>
        <Text style={styles.generateText}>Generate</Text>
      </TouchableOpacity>

      {output ? (
        <View style={styles.preview}>
          <Text style={styles.previewTitle}>Preview</Text>
          <Text style={styles.previewBody}>{output}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12, color: '#111827' },
  label: { color: '#4B5563', fontWeight: '700', marginTop: 8, marginBottom: 6 },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  pill: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 9999, backgroundColor: '#F3F4F6' },
  pillActive: { backgroundColor: '#111827' },
  pillText: { color: '#111827', fontWeight: '700', textTransform: 'capitalize' },
  pillTextActive: { color: '#fff' },
  textarea: { minHeight: 100, borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 12, padding: 12, backgroundColor: '#fff' },
  generateBtn: { backgroundColor: '#111827', paddingVertical: 12, borderRadius: 12, alignItems: 'center', marginTop: 12 },
  generateText: { color: '#fff', fontWeight: '800' },
  preview: { marginTop: 16, padding: 12, backgroundColor: '#F9FAFB', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  previewTitle: { color: '#111827', fontWeight: '800', marginBottom: 8 },
  previewBody: { color: '#111827' },
});
