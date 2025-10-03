import React, { useMemo, useRef, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';

type Message = { id: string; role: 'user' | 'assistant'; content: string };

const initialMessages: Message[] = [
  { id: 'm-1', role: 'assistant', content: 'Hi! How can I help with your real estate tasks today?' },
];

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const listRef = useRef<FlatList<Message>>(null);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    const userMsg: Message = { id: `u-${Date.now()}`, role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    // Mock assistant response
    setTimeout(() => {
      setMessages(prev => [...prev, { id: `a-${Date.now()}`, role: 'assistant', content: `Got it: ${text}` }]);
      listRef.current?.scrollToEnd({ animated: true });
    }, 400);
  };

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[styles.bubble, item.role === 'user' ? styles.user : styles.assistant]}>
      <Text style={[styles.bubbleText, item.role === 'user' ? styles.userText : styles.assistantText]}>{item.content}</Text>
    </View>
  );

  return (
    <KeyboardAvoidingView behavior={Platform.select({ ios: 'padding', android: undefined })} style={styles.flex}>
      <View style={styles.container}>
        <Text style={styles.title}>AI Assistant</Text>
        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(m) => m.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
        />
        <View style={styles.inputRow}>
          <TextInput
            value={input}
            onChangeText={setInput}
            placeholder="Type a message..."
            style={styles.input}
            returnKeyType="send"
            onSubmitEditing={send}
          />
          <TouchableOpacity onPress={send} style={styles.sendBtn}>
            <Text style={styles.sendText}>Send</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12, color: '#111827' },
  list: { gap: 8, paddingBottom: 8 },
  bubble: { paddingHorizontal: 12, paddingVertical: 10, borderRadius: 14, maxWidth: '80%' },
  user: { alignSelf: 'flex-end', backgroundColor: '#111827' },
  assistant: { alignSelf: 'flex-start', backgroundColor: '#F3F4F6' },
  bubbleText: { fontSize: 14 },
  userText: { color: '#fff' },
  assistantText: { color: '#111827' },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 },
  input: { flex: 1, backgroundColor: '#F9FAFB', borderRadius: 12, paddingHorizontal: 12, paddingVertical: 10 },
  sendBtn: { backgroundColor: '#111827', paddingHorizontal: 14, paddingVertical: 10, borderRadius: 12 },
  sendText: { color: '#fff', fontWeight: '700' },
});
