import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
import tempfile
import os
import threading
import time

# Try to import pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Warning: pygame not installed. Install with: pip install pygame")

# Path to MP3 file
AUDIO_FILE = r"C:\Dev\cursor_ai\AndrewDaly.github.io\python_projects_audio\toms_diner.mp3"

class AudioVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Waveform Visualizer")
        self.root.geometry("1400x700")
        
        self.is_playing = False
        self.is_paused = False
        self.audio_path = None
        self.play_start_time = 0
        self.paused_position = 0
        self.current_position = 0
        self.play_marker = None
        self.animation_running = False
        self.window_size = 10.0  # 10 second window
        self.scroll_position = 0.0  # Current scroll position in seconds
        self.match_regions = []  # Store matched regions for highlighting
        self.match_highlights = []  # Store highlight rectangles for zoomed view
        self.full_match_highlights = []  # Store highlight rectangles for full view
        
        # Control frame
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        # Play button
        self.play_button = tk.Button(
            control_frame, 
            text="▶ Play", 
            width=12, 
            font=("Arial", 12),
            command=self.toggle_playback
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Find repeats button
        self.find_repeats_button = tk.Button(
            control_frame,
            text="Find Repeats",
            width=12,
            font=("Arial", 12),
            command=self.find_repeated_substrings
        )
        self.find_repeats_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="", font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Load audio
        print("Loading audio file...")
        try:
            audio = AudioSegment.from_mp3(AUDIO_FILE)
            
            # Export to WAV for pygame playback
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            self.audio_path = temp_wav.name
            audio.export(self.audio_path, format="wav")
            temp_wav.close()
            
            samples = np.array(audio.get_array_of_samples())
            
            # Convert to mono if stereo
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)
            
            self.samples = samples
            self.sample_rate = audio.frame_rate
            self.duration = len(audio) / 1000.0  # Duration in seconds
            
            # Normalize samples to [-1, 1] range
            if samples.dtype == np.int16:
                samples_normalized = samples.astype(np.float32) / 32768.0
            elif samples.dtype == np.int32:
                samples_normalized = samples.astype(np.float32) / 2147483648.0
            else:
                samples_normalized = samples.astype(np.float32)
                if samples_normalized.max() > 1.0:
                    samples_normalized = samples_normalized / np.abs(samples_normalized).max()
            
            self.samples_normalized = samples_normalized
            
            # Create visualizations
            self.create_visualizations()
            
            print("Audio loaded and visualized successfully!")
        except Exception as e:
            print(f"Error loading audio: {e}")
            error_label = tk.Label(root, text=f"Error loading audio: {e}", fg="red")
            error_label.pack()
    
    def create_visualizations(self):
        """Create waveform visualizations with scrolling window and full waveform overview"""
        # Create figure with two subplots (full view on top, zoomed view on bottom)
        self.fig = plt.figure(figsize=(14, 7), dpi=100)
        gs = self.fig.add_gridspec(2, 1, height_ratios=[1, 1.5], hspace=0.3)
        
        # Create full time axis for entire audio
        self.full_time_axis = np.arange(len(self.samples_normalized)) / self.sample_rate
        
        # Top subplot: Full waveform overview
        self.ax_full = self.fig.add_subplot(gs[0, 0])
        self.ax_full.set_title(f"Full Waveform Overview - {self.duration:.2f} seconds", fontsize=12, fontweight='bold', pad=5)
        self.ax_full.set_xlabel("Time (seconds)", fontsize=10)
        self.ax_full.set_ylabel("Amplitude", fontsize=10)
        self.ax_full.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_full.set_ylim(-1.1, 1.1)
        self.ax_full.set_xlim(0, self.duration)
        
        # Draw full waveform (downsampled for display)
        display_step = max(1, len(self.samples_normalized) // 5000)  # Show ~5000 points
        full_display_samples = self.samples_normalized[::display_step]
        full_display_time = self.full_time_axis[::display_step]
        self.ax_full.plot(full_display_time, full_display_samples, linewidth=0.5, color='#2C3E50', alpha=0.7, zorder=1)
        self.ax_full.fill_between(full_display_time, full_display_samples, 0, alpha=0.3, color='#4A90E2', zorder=0)
        
        # Initialize full view match highlights
        self.full_match_highlights = []
        
        # Bottom subplot: Zoomed scrolling window
        self.ax = self.fig.add_subplot(gs[1, 0])
        self.ax.set_title("Zoomed View (10s window)", fontsize=12, fontweight='bold', pad=5)
        self.ax.set_xlabel("Time (seconds)", fontsize=10)
        self.ax.set_ylabel("Amplitude", fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax.set_ylim(-1.1, 1.1)
        
        # Initialize empty line for animation
        self.wave_line, = self.ax.plot([], [], linewidth=1.2, color='#2C3E50', zorder=2)
        self.wave_fill_collections = []
        
        # Add play marker to zoomed view
        self.play_marker = self.ax.axvline(x=0, color='red', linewidth=2.5, linestyle='-', alpha=0.9, zorder=10)
        
        # Initialize match highlights list for zoomed view
        self.match_highlights = []
        
        # Set initial window view
        self.ax.set_xlim(0, self.window_size)
        
        plt.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Start animation
        self.animation_frame = 0
        self.start_animation()
    
    def start_animation(self):
        """Start the waveform animation"""
        # Use tkinter's after method for animation instead of FuncAnimation
        # (FuncAnimation doesn't work well with tkinter)
        self.animate_waveforms()
    
    def animate_waveforms(self):
        """Animate the waveform with scrolling window and moving wave lines"""
        if not hasattr(self, 'full_time_axis'):
            return
        
        # Calculate animation phase for wave movement effect
        phase = self.animation_frame * 0.02  # Slow, smooth animation
        
        # Determine the visible window (adjust if audio is shorter than window)
        actual_window_size = min(self.window_size, self.duration)
        
        if self.is_playing and not self.is_paused:
            # Follow playback position
            window_start = max(0, self.current_position - 2.0)  # Keep marker 2 seconds from left edge
            window_start = min(window_start, max(0, self.duration - actual_window_size))
            self.scroll_position = window_start
        else:
            # Auto-scroll when not playing
            max_scroll = max(0, self.duration - actual_window_size)
            if max_scroll > 0:
                self.scroll_position = (self.scroll_position + 0.05) % max_scroll
            else:
                self.scroll_position = 0
        
        window_end = min(self.scroll_position + actual_window_size, self.duration)
        
        # Get indices for the visible window
        start_idx = int(self.scroll_position * self.sample_rate)
        end_idx = int(window_end * self.sample_rate)
        start_idx = max(0, min(start_idx, len(self.samples_normalized) - 1))
        end_idx = max(start_idx + 1, min(end_idx, len(self.samples_normalized)))
        
        # Extract visible samples
        visible_samples = self.samples_normalized[start_idx:end_idx]
        visible_time = self.full_time_axis[start_idx:end_idx]
        
        if len(visible_samples) == 0:
            self.root.after(3, self.animate_waveforms)
            return
        
        # Create animated wave effect with sine/cosine modulation
        # This makes the wave lines appear to move and flow organically
        t_visible = visible_time - visible_time[0]  # Normalize to start at 0
        animated_samples = visible_samples.copy()
        
        # Add multiple wave motion effects for organic, flowing animation
        # Combine multiple frequencies for a more natural wave motion
        wave_modulation = (
            0.02 * np.sin(2 * np.pi * 1.5 * t_visible + phase) +
            0.015 * np.cos(2 * np.pi * 2.5 * t_visible + phase * 1.3) +
            0.01 * np.sin(2 * np.pi * 3.5 * t_visible + phase * 0.7)
        )
        animated_samples = animated_samples + wave_modulation
        
        # Update the line data
        self.wave_line.set_data(visible_time, animated_samples)
        
        # Update fill area (remove old, add new)
        for collection in self.wave_fill_collections:
            collection.remove()
        self.wave_fill_collections.clear()
        
        fill_collection = self.ax.fill_between(visible_time, animated_samples, 0, 
                                               alpha=0.6, color='#4A90E2', zorder=1)
        self.wave_fill_collections.append(fill_collection)
        
        # Update x-axis limits to show the window
        self.ax.set_xlim(self.scroll_position, window_end)
        
        # Update play marker position
        self.update_play_marker()
        
        # Redraw canvas
        self.canvas.draw()
        
        # Increment frame and schedule next update
        self.animation_frame += 1
        self.root.after(3, self.animate_waveforms)  # ~300 FPS
    
    def update_play_marker(self):
        """Update the play marker position based on current playback time"""
        if self.is_playing and HAS_PYGAME and not self.is_paused:
            try:
                # Get current playback position
                # pygame doesn't directly give position, so we estimate based on start time
                elapsed = time.time() - self.play_start_time
                self.current_position = self.paused_position + elapsed
                
                # Clamp to duration
                if self.current_position > self.duration:
                    self.current_position = self.duration
                    self.is_playing = False
                    self.is_paused = False
                    self.play_button.config(text="▶ Play")
                
                # Update marker
                if self.play_marker:
                    self.play_marker.set_xdata([self.current_position, self.current_position])
            except:
                pass
        elif self.is_paused:
            # Keep marker at paused position
            if self.play_marker:
                self.play_marker.set_xdata([self.current_position, self.current_position])
        else:
            # Hide marker when not playing
            if self.play_marker:
                self.play_marker.set_xdata([-1, -1])  # Move off-screen
    
    def toggle_playback(self):
        """Toggle audio playback"""
        if not HAS_PYGAME:
            print("pygame not available for playback")
            return
        
        if not self.audio_path:
            print("No audio file loaded")
            return
        
        if self.is_playing:
            if self.is_paused:
                # Resume playback
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_start_time = time.time()
                self.play_button.config(text="⏸ Pause")
            else:
                # Pause playback
                pygame.mixer.music.pause()
                self.is_paused = True
                self.paused_position = self.current_position
                self.play_button.config(text="▶ Play")
        else:
            try:
                # Start playing from beginning or paused position
                pygame.mixer.music.load(self.audio_path)
                if self.paused_position > 0:
                    # Try to seek (pygame doesn't support seeking well, so we'll just restart)
                    # For now, restart from beginning
                    self.paused_position = 0
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_start_time = time.time()
                self.current_position = self.paused_position
                self.play_button.config(text="⏸ Pause")
                
                # Monitor playback to update button when finished
                self.root.after(100, self.check_playback)
            except Exception as e:
                print(f"Error playing audio: {e}")
    
    def check_playback(self):
        """Check if playback has finished"""
        if self.is_playing and not self.is_paused:
            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                self.is_paused = False
                self.current_position = 0
                self.paused_position = 0
                self.play_button.config(text="▶ Play")
                self.update_play_marker()
            else:
                self.root.after(100, self.check_playback)
    
    def find_repeated_substrings(self):
        """Find the longest repeated substring in the waveform (optimized fast search)"""
        self.status_label.config(text="Analyzing...", fg="blue")
        self.root.update()
        
        # Aggressively downsample for speed (work with ~2000 samples max)
        max_samples = 2000
        step = 1
        if len(self.samples_normalized) > max_samples:
            step = len(self.samples_normalized) // max_samples
            downsampled = self.samples_normalized[::step]
            downsampled_rate = self.sample_rate / step
        else:
            downsampled = self.samples_normalized
            downsampled_rate = self.sample_rate
        
        # Larger window: search for 10-20 second substrings
        min_length = int(10.0 * downsampled_rate)  # Minimum 10 seconds
        max_length = min(int(20.0 * downsampled_rate), len(downsampled) // 2)  # Max 20 seconds
        
        # Sample only a few dozen positions instead of all
        num_samples = 50  # Only check 50 starting positions
        position_step = max(1, (len(downsampled) - max_length) // num_samples)
        
        # Try only a few length variations (larger steps)
        length_step = max(1, int(downsampled_rate * 1.0))  # Step by 1 second
        
        print(f"Fast search: {num_samples} positions, lengths {min_length/downsampled_rate:.1f}s-{max_length/downsampled_rate:.1f}s...")
        
        best_match_length = 0
        best_positions = None
        best_correlation = -1  # Start with -1 to accept any match
        
        # Try different substring lengths (fewer iterations)
        for length in range(max_length, min_length - 1, -length_step):
            # Sample only a few dozen starting positions
            positions1 = list(range(0, len(downsampled) - length, position_step))
            if len(positions1) > num_samples:
                positions1 = positions1[:num_samples]
            
            for start1 in positions1:
                substring1 = downsampled[start1:start1 + length]
                
                # Sample positions for comparison (only check a few dozen)
                positions2 = list(range(start1 + length, len(downsampled) - length + 1, position_step))
                if len(positions2) > num_samples:
                    positions2 = positions2[:num_samples]
                
                for start2 in positions2:
                    substring2 = downsampled[start2:start2 + length]
                    
                    # Quick similarity check
                    if len(substring1) == len(substring2):
                        # Fast normalized correlation
                        norm1 = np.linalg.norm(substring1)
                        norm2 = np.linalg.norm(substring2)
                        
                        if norm1 > 1e-6 and norm2 > 1e-6:
                            correlation = np.dot(substring1, substring2) / (norm1 * norm2)
                            
                            # Track the best match regardless of threshold
                            if correlation > best_correlation:
                                best_match_length = length
                                best_positions = (start1, start2, length)
                                best_correlation = correlation
        
        # Convert back to original sample indices and time
        # Always return the best match found, even if correlation is low
        if best_positions and best_correlation > 0:
            start1_idx, start2_idx, match_length = best_positions
            # Convert to original indices
            if len(self.samples_normalized) > max_samples:
                orig_start1 = start1_idx * step
                orig_start2 = start2_idx * step
                orig_length = match_length * step
            else:
                orig_start1 = start1_idx
                orig_start2 = start2_idx
                orig_length = match_length
            
            # Convert to time
            time1 = orig_start1 / self.sample_rate
            time2 = orig_start2 / self.sample_rate
            duration = orig_length / self.sample_rate
            
            self.match_regions = [
                (time1, time1 + duration),
                (time2, time2 + duration)
            ]
            
            # Clear old highlights
            self.clear_highlights()
            
            # Add new highlights
            self.add_highlights()
            
            # Update status with correlation score
            correlation_pct = best_correlation * 100
            self.status_label.config(
                text=f"Best match: {duration:.2f}s at {time1:.2f}s and {time2:.2f}s ({correlation_pct:.1f}% similarity)",
                fg="green" if correlation_pct > 80 else "orange" if correlation_pct > 60 else "red"
            )
            
            print(f"Found closest repeated substring:")
            print(f"  Length: {duration:.2f} seconds")
            print(f"  Similarity: {correlation_pct:.1f}%")
            print(f"  First occurrence: {time1:.2f}s - {time1 + duration:.2f}s")
            print(f"  Second occurrence: {time2:.2f}s - {time2 + duration:.2f}s")
            
            # Redraw
            self.canvas.draw()
        else:
            self.status_label.config(text="No repeated substrings found", fg="red")
            print("No repeated substrings found")
    
    def clear_highlights(self):
        """Remove existing highlight rectangles from both views"""
        for rect in self.match_highlights:
            rect.remove()
        self.match_highlights.clear()
        
        for rect in self.full_match_highlights:
            rect.remove()
        self.full_match_highlights.clear()
    
    def add_highlights(self):
        """Add highlight rectangles for matched regions on both views"""
        for start_time, end_time in self.match_regions:
            # Highlight on full waveform view (top)
            rect_full = plt.Rectangle(
                (start_time, -1.1), 
                end_time - start_time, 
                2.2,
                facecolor='yellow', 
                alpha=0.4, 
                edgecolor='orange', 
                linewidth=2,
                zorder=5
            )
            self.ax_full.add_patch(rect_full)
            self.full_match_highlights.append(rect_full)
            
            # Highlight on zoomed view (bottom) - only if visible in current window
            if (start_time < self.scroll_position + self.window_size and 
                end_time > self.scroll_position):
                rect_zoom = plt.Rectangle(
                    (start_time, -1.1), 
                    end_time - start_time, 
                    2.2,
                    facecolor='yellow', 
                    alpha=0.3, 
                    edgecolor='orange', 
                    linewidth=2,
                    zorder=5
                )
                self.ax.add_patch(rect_zoom)
                self.match_highlights.append(rect_zoom)
    
    def __del__(self):
        """Cleanup temporary file"""
        if self.audio_path and os.path.exists(self.audio_path):
            try:
                os.unlink(self.audio_path)
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVisualizer(root)
    root.mainloop()
