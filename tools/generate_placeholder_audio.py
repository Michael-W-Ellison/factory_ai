#!/usr/bin/env python3
"""
Generate placeholder audio files for the game.

Creates simple synthesized sounds for all required audio assets.
These can be replaced with proper sound design later.
"""

import os
import struct
import math
import wave
import random

# Sound directory
SOUND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sounds')

# Audio parameters
SAMPLE_RATE = 44100
CHANNELS = 1  # Mono for SFX
SAMPLE_WIDTH = 2  # 16-bit


def generate_sine_wave(frequency: float, duration: float, volume: float = 0.5,
                       fade_in: float = 0.01, fade_out: float = 0.05) -> bytes:
    """Generate a sine wave with fade in/out."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    fade_in_samples = int(SAMPLE_RATE * fade_in)
    fade_out_samples = int(SAMPLE_RATE * fade_out)

    for i in range(num_samples):
        # Calculate envelope
        if i < fade_in_samples:
            envelope = i / fade_in_samples
        elif i > num_samples - fade_out_samples:
            envelope = (num_samples - i) / fade_out_samples
        else:
            envelope = 1.0

        # Generate sample
        t = i / SAMPLE_RATE
        sample = math.sin(2 * math.pi * frequency * t) * volume * envelope
        samples.append(int(sample * 32767))

    return struct.pack('<' + 'h' * len(samples), *samples)


def generate_noise(duration: float, volume: float = 0.3,
                   fade_in: float = 0.1, fade_out: float = 0.2) -> bytes:
    """Generate white noise with fade in/out."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    fade_in_samples = int(SAMPLE_RATE * fade_in)
    fade_out_samples = int(SAMPLE_RATE * fade_out)

    for i in range(num_samples):
        if i < fade_in_samples:
            envelope = i / fade_in_samples
        elif i > num_samples - fade_out_samples:
            envelope = (num_samples - i) / fade_out_samples
        else:
            envelope = 1.0

        sample = (random.random() * 2 - 1) * volume * envelope
        samples.append(int(sample * 32767))

    return struct.pack('<' + 'h' * len(samples), *samples)


def generate_beep(frequencies: list, durations: list, volume: float = 0.5) -> bytes:
    """Generate a multi-tone beep sequence."""
    data = b''
    for freq, dur in zip(frequencies, durations):
        if freq == 0:
            # Silence
            num_samples = int(SAMPLE_RATE * dur)
            data += struct.pack('<' + 'h' * num_samples, *([0] * num_samples))
        else:
            data += generate_sine_wave(freq, dur, volume)
    return data


def generate_sweep(start_freq: float, end_freq: float, duration: float,
                   volume: float = 0.5) -> bytes:
    """Generate a frequency sweep."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []

    fade_samples = int(SAMPLE_RATE * 0.02)

    for i in range(num_samples):
        t = i / SAMPLE_RATE
        progress = i / num_samples

        # Exponential frequency sweep
        freq = start_freq * ((end_freq / start_freq) ** progress)

        # Envelope
        if i < fade_samples:
            envelope = i / fade_samples
        elif i > num_samples - fade_samples:
            envelope = (num_samples - i) / fade_samples
        else:
            envelope = 1.0

        sample = math.sin(2 * math.pi * freq * t) * volume * envelope
        samples.append(int(sample * 32767))

    return struct.pack('<' + 'h' * len(samples), *samples)


def save_wav(filename: str, data: bytes, channels: int = 1):
    """Save audio data as WAV file."""
    filepath = os.path.join(SOUND_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(data)

    print(f"  Created: {filename}")


def generate_ui_sounds():
    """Generate UI sound effects."""
    print("\nGenerating UI sounds...")

    # Click - short high beep
    save_wav('ui/click.wav', generate_beep([800, 600], [0.03, 0.02], 0.4))

    # Hover - very short soft beep
    save_wav('ui/hover.wav', generate_beep([500], [0.02], 0.2))

    # Open - ascending tones
    save_wav('ui/open.wav', generate_beep([400, 500, 600], [0.05, 0.05, 0.08], 0.3))

    # Close - descending tones
    save_wav('ui/close.wav', generate_beep([600, 500, 400], [0.05, 0.05, 0.08], 0.3))

    # Error - low harsh tone
    save_wav('ui/error.wav', generate_beep([200, 150], [0.1, 0.15], 0.5))

    # Success - pleasant ascending
    save_wav('ui/success.wav', generate_beep([400, 500, 700], [0.08, 0.08, 0.12], 0.4))


def generate_game_sounds():
    """Generate game event sounds."""
    print("\nGenerating game sounds...")

    # Build place - solid thud
    save_wav('game/build_place.wav', generate_beep([150, 100], [0.05, 0.1], 0.5))

    # Build complete - triumphant
    save_wav('game/build_complete.wav', generate_beep([400, 500, 600, 800], [0.1, 0.1, 0.1, 0.2], 0.4))

    # Demolish - descending crash
    save_wav('game/demolish.wav', generate_sweep(400, 80, 0.3, 0.5))

    # Research complete - discovery sound
    save_wav('game/research_complete.wav', generate_beep([300, 400, 500, 600, 800], [0.1, 0.1, 0.1, 0.1, 0.3], 0.4))

    # Research start - initiating
    save_wav('game/research_start.wav', generate_beep([400, 450, 500], [0.08, 0.08, 0.1], 0.3))

    # Money gain - pleasant cha-ching
    save_wav('game/money_gain.wav', generate_beep([600, 800, 1000], [0.05, 0.05, 0.1], 0.4))

    # Money loss - disappointing
    save_wav('game/money_loss.wav', generate_beep([400, 300, 200], [0.08, 0.08, 0.1], 0.4))


def generate_robot_sounds():
    """Generate robot-related sounds."""
    print("\nGenerating robot sounds...")

    # Select - electronic blip
    save_wav('robot/select.wav', generate_beep([600, 800], [0.03, 0.05], 0.4))

    # Move - servo whir
    save_wav('robot/move.wav', generate_sweep(200, 400, 0.15, 0.3))

    # Collect - suction
    save_wav('robot/collect.wav', generate_sweep(600, 300, 0.2, 0.4))

    # Deposit - release
    save_wav('robot/deposit.wav', generate_sweep(300, 500, 0.15, 0.3))

    # Low battery - warning beeps
    save_wav('robot/low_battery.wav', generate_beep([400, 0, 400, 0, 400], [0.1, 0.05, 0.1, 0.05, 0.1], 0.5))


def generate_alert_sounds():
    """Generate alert sounds."""
    print("\nGenerating alert sounds...")

    # Warning - attention getting
    save_wav('alerts/warning.wav', generate_beep([500, 0, 500], [0.15, 0.05, 0.15], 0.5))

    # Danger - urgent
    save_wav('alerts/danger.wav', generate_beep([600, 400, 600, 400], [0.1, 0.1, 0.1, 0.1], 0.6))

    # Inspection - official sounding
    save_wav('alerts/inspection.wav', generate_beep([400, 500, 400, 500, 600], [0.15, 0.15, 0.15, 0.15, 0.2], 0.5))

    # Police - siren-like
    data = b''
    for _ in range(3):
        data += generate_sweep(400, 800, 0.3, 0.5)
        data += generate_sweep(800, 400, 0.3, 0.5)
    save_wav('alerts/police.wav', data)


def generate_ambient_sounds():
    """Generate ambient background sounds."""
    print("\nGenerating ambient sounds...")

    # Factory hum - low drone (longer duration for looping)
    data = generate_sine_wave(60, 2.0, 0.2, 0.2, 0.2)
    # Add harmonics
    data2 = generate_sine_wave(120, 2.0, 0.1, 0.2, 0.2)
    # Mix by averaging
    mixed = []
    for i in range(0, len(data), 2):
        s1 = struct.unpack('<h', data[i:i+2])[0]
        s2 = struct.unpack('<h', data2[i:i+2])[0]
        mixed.append(int((s1 + s2) / 2))
    save_wav('ambient/factory_hum.wav', struct.pack('<' + 'h' * len(mixed), *mixed))

    # City ambience - subtle noise
    save_wav('ambient/city.wav', generate_noise(3.0, 0.15, 0.3, 0.3))


def generate_music_tracks():
    """Generate placeholder music tracks (simple loops)."""
    print("\nGenerating music tracks...")

    def generate_simple_melody(notes: list, duration_per_note: float, volume: float = 0.3) -> bytes:
        """Generate a simple melody from note frequencies."""
        data = b''
        for note in notes:
            if note == 0:
                # Rest
                num_samples = int(SAMPLE_RATE * duration_per_note)
                data += struct.pack('<' + 'h' * num_samples, *([0] * num_samples))
            else:
                data += generate_sine_wave(note, duration_per_note, volume, 0.02, 0.05)
        return data

    # Menu theme - calm, looping melody
    # C major pentatonic scale notes
    menu_notes = [262, 294, 330, 392, 440, 392, 330, 294] * 4  # C D E G A G E D repeated
    save_wav('music/menu_theme.ogg', generate_simple_melody(menu_notes, 0.3, 0.25))

    # Gameplay - upbeat work rhythm
    gameplay_notes = [330, 392, 440, 392, 330, 294, 330, 0] * 4  # E G A G E D E rest
    save_wav('music/gameplay.ogg', generate_simple_melody(gameplay_notes, 0.25, 0.2))

    # Tense - minor key, faster
    tense_notes = [220, 262, 220, 196, 220, 262, 294, 262] * 4  # A C A G A C D C (minor feel)
    save_wav('music/tense.ogg', generate_simple_melody(tense_notes, 0.2, 0.25))

    # Victory - triumphant
    victory_notes = [262, 330, 392, 523, 0, 523, 523, 523, 659, 523]  # C E G C rest C C C E C
    save_wav('music/victory.ogg', generate_simple_melody(victory_notes, 0.4, 0.3))

    # Defeat - somber
    defeat_notes = [220, 196, 175, 165, 0, 165, 0, 165]  # A G F E rest E rest E
    save_wav('music/defeat.ogg', generate_simple_melody(defeat_notes, 0.5, 0.25))


def main():
    """Generate all placeholder audio files."""
    print("=" * 50)
    print("Generating Placeholder Audio Files")
    print("=" * 50)

    generate_ui_sounds()
    generate_game_sounds()
    generate_robot_sounds()
    generate_alert_sounds()
    generate_ambient_sounds()
    generate_music_tracks()

    print("\n" + "=" * 50)
    print("Audio generation complete!")
    print("=" * 50)

    # Count files
    total = 0
    for root, dirs, files in os.walk(SOUND_DIR):
        for f in files:
            if f.endswith(('.wav', '.ogg', '.mp3')):
                total += 1
    print(f"\nTotal audio files created: {total}")


if __name__ == '__main__':
    main()
