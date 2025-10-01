/**
 * Audio Service for PropertyPro AI Real Estate Assistant
 * 
 * This service handles audio recording, playback, and media device management
 * for the voice command system.
 */

export interface AudioDevice {
  deviceId: string;
  label: string;
  kind: MediaDeviceKind;
}

export interface RecordingOptions {
  audioBitsPerSecond?: number;
  mimeType?: string;
  sampleRate?: number;
}

export interface AudioRecordingResult {
  audioBlob: Blob;
  duration: number;
  mimeType: string;
  size: number;
}

class AudioService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioStream: MediaStream | null = null;
  private audioChunks: Blob[] = [];
  private recordingStartTime: number = 0;
  private isRecording: boolean = false;

  /**
   * Check if MediaRecorder is supported
   */
  isMediaRecorderSupported(): boolean {
    return typeof MediaRecorder !== 'undefined';
  }

  /**
   * Check if getUserMedia is supported
   */
  isGetUserMediaSupported(): boolean {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  /**
   * Get available audio devices
   */
  async getAudioDevices(): Promise<AudioDevice[]> {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
        return [];
      }

      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices
        .filter(device => device.kind === 'audioinput')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
          kind: device.kind
        }));
    } catch (error) {
      console.error('Error getting audio devices:', error);
      return [];
    }
  }

  /**
   * Request microphone permission
   */
  async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop the stream immediately after getting permission
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Microphone permission denied:', error);
      return false;
    }
  }

  /**
   * Start audio recording
   */
  async startRecording(options: RecordingOptions = {}): Promise<void> {
    try {
      if (this.isRecording) {
        throw new Error('Recording is already in progress');
      }

      if (!this.isMediaRecorderSupported()) {
        throw new Error('MediaRecorder is not supported in this browser');
      }

      if (!this.isGetUserMediaSupported()) {
        throw new Error('getUserMedia is not supported in this browser');
      }

      // Request microphone access
      this.audioStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: options.sampleRate || 44100
        }
      });

      // Determine MIME type
      const mimeType = this.getSupportedMimeType(options.mimeType);
      
      // Create MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.audioStream, {
        mimeType,
        audioBitsPerSecond: options.audioBitsPerSecond || 128000
      });

      // Reset audio chunks
      this.audioChunks = [];
      this.recordingStartTime = Date.now();

      // Set up event handlers
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        this.stopRecording();
      };

      // Start recording
      this.mediaRecorder.start(100); // Collect data every 100ms
      this.isRecording = true;

    } catch (error) {
      console.error('Error starting recording:', error);
      this.cleanup();
      throw error;
    }
  }

  /**
   * Stop audio recording
   */
  async stopRecording(): Promise<AudioRecordingResult> {
    return new Promise((resolve, reject) => {
      if (!this.isRecording || !this.mediaRecorder) {
        reject(new Error('No recording in progress'));
        return;
      }

      const duration = Date.now() - this.recordingStartTime;

      this.mediaRecorder.onstop = () => {
        try {
          const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
          const audioBlob = new Blob(this.audioChunks, { type: mimeType });
          
          const result: AudioRecordingResult = {
            audioBlob,
            duration,
            mimeType,
            size: audioBlob.size
          };

          this.cleanup();
          resolve(result);
        } catch (error) {
          this.cleanup();
          reject(error);
        }
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Pause recording
   */
  pauseRecording(): void {
    if (this.mediaRecorder && this.isRecording && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.pause();
    }
  }

  /**
   * Resume recording
   */
  resumeRecording(): void {
    if (this.mediaRecorder && this.isRecording && this.mediaRecorder.state === 'paused') {
      this.mediaRecorder.resume();
    }
  }

  /**
   * Check if currently recording
   */
  getRecordingState(): 'idle' | 'recording' | 'paused' {
    if (!this.mediaRecorder) return 'idle';
    return this.mediaRecorder.state as 'idle' | 'recording' | 'paused';
  }

  /**
   * Get recording duration
   */
  getRecordingDuration(): number {
    if (!this.isRecording) return 0;
    return Date.now() - this.recordingStartTime;
  }

  /**
   * Get the current media stream (if recording)
   */
  getCurrentStream(): MediaStream | null {
    return this.audioStream;
  }

  /**
   * Get supported MIME types
   */
  private getSupportedMimeType(preferredMimeType?: string): string {
    const supportedTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/wav'
    ];

    if (preferredMimeType && MediaRecorder.isTypeSupported(preferredMimeType)) {
      return preferredMimeType;
    }

    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return 'audio/webm'; // Fallback
  }

  /**
   * Clean up resources
   */
  private cleanup(): void {
    this.isRecording = false;
    
    if (this.mediaRecorder) {
      this.mediaRecorder = null;
    }

    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }

    this.audioChunks = [];
    this.recordingStartTime = 0;
  }

  /**
   * Play audio blob
   */
  async playAudio(audioBlob: Blob): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio();
      const url = URL.createObjectURL(audioBlob);
      
      audio.src = url;
      audio.onended = () => {
        URL.revokeObjectURL(url);
        resolve();
      };
      audio.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Failed to play audio'));
      };
      
      audio.play().catch(reject);
    });
  }

  /**
   * Convert audio blob to file
   */
  audioBlobToFile(audioBlob: Blob, filename: string = 'recording.webm'): File {
    return new File([audioBlob], filename, { type: audioBlob.type });
  }

  /**
   * Get audio blob info
   */
  getAudioInfo(audioBlob: Blob): { size: number; type: string; duration?: number } {
    return {
      size: audioBlob.size,
      type: audioBlob.type,
      // Note: Duration would require additional processing
    };
  }
}

// Export singleton instance
export const audioService = new AudioService();

