"""
STT (Speech-to-Text) Listener using OpenAI Whisper.

Captures audio from microphone and transcribes it to text.
"""

import whisper
import sounddevice as sd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class STTListener:
    """Speech-to-Text listener using Whisper for transcription."""
    
    def __init__(self, model_size: str = "base", sample_rate: int = 16000):
        """
        Initialize the STT listener.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            sample_rate: Audio sample rate in Hz (default 16000 for Whisper)
        """
        self.model_size = model_size
        self.sample_rate = sample_rate
        self.model = None
        logger.info(f"Initializing STT listener with model: {model_size}")
        
    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
    
    def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array
        """
        logger.info(f"Recording audio for {duration} seconds...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait until recording is finished
        logger.info("Recording complete")
        return audio.flatten()
    
    def transcribe_audio(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text using Whisper.
        
        Args:
            audio: Audio data as numpy array
            
        Returns:
            Transcribed text string
        """
        if self.model is None:
            self.load_model()
        
        logger.info("Transcribing audio...")
        result = self.model.transcribe(audio, language="en")
        text = result["text"].strip()
        logger.info(f"Transcription: {text}")
        return text
    
    def listen(self, duration: float = 5.0) -> str:
        """
        Record and transcribe audio in one step.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text string
        """
        audio = self.record_audio(duration)
        return self.transcribe_audio(audio)
    
    def listen_push_to_talk(self) -> Optional[str]:
        """
        Listen with push-to-talk (waits for Enter key press).
        
        Returns:
            Transcribed text or None if cancelled
        """
        print("\n[Press Enter to start recording, then Enter again to stop]")
        input("Press Enter to start recording...")
        
        print("Recording... (Press Enter to stop)")
        # Simple implementation: record until Enter is pressed again
        # For better UX, could use keyboard library for non-blocking input
        import threading
        import queue
        
        recording_queue = queue.Queue()
        stop_recording = threading.Event()
        
        def record_until_stop():
            """Record audio until stop event is set."""
            audio_chunks = []
            chunk_duration = 0.5  # Record in 0.5 second chunks
            
            while not stop_recording.is_set():
                chunk = sd.rec(
                    int(chunk_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype=np.float32
                )
                sd.wait()
                audio_chunks.append(chunk.flatten())
            
            # Concatenate all chunks
            if audio_chunks:
                full_audio = np.concatenate(audio_chunks)
                recording_queue.put(full_audio)
        
        # Start recording thread
        record_thread = threading.Thread(target=record_until_stop, daemon=True)
        record_thread.start()
        
        # Wait for Enter to stop
        input()
        stop_recording.set()
        record_thread.join(timeout=2.0)
        
        # Get recorded audio
        try:
            audio = recording_queue.get(timeout=1.0)
            return self.transcribe_audio(audio)
        except queue.Empty:
            logger.warning("No audio recorded")
            return None
