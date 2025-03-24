import numpy as np
import random
import time
import math
import sys
import sounddevice as sd
import readchar

def generate_sine_wave(frequency, duration, sample_rate=44100, volume=0.3):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    note = np.sin(frequency * 2 * np.pi * t)
    # Scale to 16-bit range
    audio = note * (2**15 - 1) * volume
    return audio.astype(np.int16)

def play_audio(audio, sample_rate=44100):
    sd.play(audio, sample_rate)
    sd.wait()

def frequency_to_note_name(freq):
    if freq <= 0:
        return "N/A"
    # Convert frequency to MIDI note number using A4 (440 Hz) as reference.
    midi = round(69 + 12 * math.log2(freq / 440.0))
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note = note_names[midi % 12]
    octave = (midi // 12) - 1
    return f"{note}{octave}"

def play_correct_feedback(sample_rate=44100):
    # Plays 8 notes for a fully correct answer (both direction and cents correct)
    correct_freqs = [55.0, 41.20, 110.0, 82.41, 220.0, 164.81, 440.0, 329.63]
    note_duration = 0.1  # seconds for each note
    silence_duration = 0.025  # pause between notes
    final_silence_duration = 0.5

    feedback_audio = np.array([], dtype=np.int16)
    for f in correct_freqs:
        note_audio = generate_sine_wave(f, note_duration, sample_rate)
        silence = np.zeros(int(silence_duration * sample_rate), dtype=np.int16)
        feedback_audio = np.concatenate((feedback_audio, note_audio, silence))
    final_silence = np.zeros(int(final_silence_duration * sample_rate), dtype=np.int16)
    feedback_audio = np.concatenate((feedback_audio, final_silence))
    play_audio(feedback_audio, sample_rate)

def play_incorrect_feedback(sample_rate=44100):
    # Plays a descending chromatic scale (or your preferred feedback) for both wrong
    start_freq = 246.94  # B3
    num_notes = 8
    note_duration = 0.2
    silence_duration = 0.05
    final_silence_duration = 0.5

    feedback_audio = np.array([], dtype=np.int16)
    for i in range(num_notes):
        current_duration = note_duration * 2 if i == num_notes - 1 else note_duration
        freq = start_freq * (2 ** (-i / 12))
        note_audio = generate_sine_wave(freq, current_duration, sample_rate)
        if i < num_notes - 1:
            silence = np.zeros(int(silence_duration * sample_rate), dtype=np.int16)
            feedback_audio = np.concatenate((feedback_audio, note_audio, silence))
        else:
            feedback_audio = np.concatenate((feedback_audio, note_audio))
    final_silence = np.zeros(int(final_silence_duration * sample_rate), dtype=np.int16)
    feedback_audio = np.concatenate((feedback_audio, final_silence))
    play_audio(feedback_audio, sample_rate)

def play_wrong_direction_accurate_feedback(sample_rate=44100):
    """
    Plays a wobble effect to symbolize being "mixed around" when the direction guess is wrong 
    but the cents guess is accurate. The tone's frequency is modulated with an effect that 
    produces about 4 "wah" cycles over its duration, with increasing modulation amplitude.
    """
    duration = 0.8  # seconds, adjust as desired
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    
    b = 300.0  # base frequency in Hz (adjust as desired)
    c = 80.0   # modulation amplitude factor (adjust as desired)
    # Choose m so that we get about 4 cycles over the tone's duration.
    # For 4 cycles, total radians = 4*2π = 8π. So m = (8π/duration)
    m = 8 * np.pi / duration  # modulation frequency
    
    # Compute the phase: φ(t) = 2π * [ b*t - (c/m)*t*cos(m*t) + (c/m^2)*sin(m*t) ]
    phase = 2 * np.pi * (b * t - (c / m) * t * np.cos(m * t) + (c / m**2) * np.sin(m * t))
    x = np.sin(phase)
    
    # Scale to 16-bit audio
    volume = 0.3
    audio = (x * (2**15 - 1) * volume).astype(np.int16)
    
    play_audio(audio, sample_rate)

def play_correct_direction_inaccurate_feedback(sample_rate=44100):
    """
    Plays 2 notes in sequence: C3 and A♯2.
    Used when the direction guess is correct but the cents guess is off.
    """
    freqs = [261.63, 185,277.18]  # Approximate frequencies for C,f#,c#.
    note_duration = 0.1
    silence_duration = 0.05
    final_silence_duration = 0.5

    feedback_audio = np.array([], dtype=np.int16)
    for i, f in enumerate(freqs):
        note_audio = generate_sine_wave(f, note_duration, sample_rate)
        if i < len(freqs) - 1:
            silence = np.zeros(int(silence_duration * sample_rate), dtype=np.int16)
            feedback_audio = np.concatenate((feedback_audio, note_audio, silence))
        else:
            feedback_audio = np.concatenate((feedback_audio, note_audio))
    play_audio(feedback_audio, sample_rate)

def main():
    max_rounds = 40  # Total rounds
    direction_score = 0
    accuracy_score = 0
    wrong_both_count = 0  # Count rounds where both direction and cents are wrong
    sample_rate = 44100
    duration = 1.0  # seconds per tone

    # List of possible base frequencies (from A2 ~110 Hz to A5 ~880 Hz)
    base_frequencies = np.linspace(110, 880, num=50)


    print("Welcome to the Ear Training Game!")
    print("There are 40 rounds. At any prompt, type 'q' to quit.\n")
    # At the beginning of your main() function, prompt for difficulty:
    difficulty = input("Choose difficulty (hard/medium/easy): ").strip().lower()
    if difficulty == "hard":
        decay = 0.90
    elif difficulty == "medium":
        decay = 0.94
    elif difficulty == "easy":
        decay = 0.98
    else:
        print("Invalid choice, defaulting to hard.")
        decay = 0.90
    
    for round_number in range(max_rounds):
        current_round = round_number + 1
        oopsie_daisies_left = 5 - wrong_both_count
        print(f"\n=== Round {current_round} === (Round {current_round}/{max_rounds}) Player has {oopsie_daisies_left}/5 Oopsie Daisies Left")
        base_freq = random.choice(base_frequencies)
        
        # Determine maximum detune offset (in cents) for this round
        max_offset = 100 * (decay ** round_number)
        if max_offset <= 2:
            lower_bound = 1
            upper_bound = 2
        else:
            lower_bound = (max_offset/4)  # User-adjusted lower bound
            upper_bound = max_offset
        
        # Pick a random offset (in cents) within the specified range
        offset = random.uniform(lower_bound, upper_bound)
        # Randomly decide if the detune is sharp or flat
        is_sharp = random.choice([True, False])
        signed_offset = offset if is_sharp else -offset
        
        # Calculate the detuned frequency: f' = f * 2^(cents/1200)
        detuned_freq = base_freq * (2 ** (signed_offset / 1200))
        
        base_note_name = frequency_to_note_name(base_freq)
        print(f"Playing base tone: {base_note_name} ({base_freq:.2f} Hz)")
        audio_base = generate_sine_wave(base_freq, duration, sample_rate)
        play_audio(audio_base, sample_rate)
        
        time.sleep(0.5)
        
        print("Playing detuned tone...")
        audio_detuned = generate_sine_wave(detuned_freq, duration, sample_rate)
        play_audio(audio_detuned, sample_rate)
        
        # Unified prompt: allow replay, directional guess, or quitting.
        guess_direction = None
        while guess_direction is None:
            print("Press UP for sharp, DOWN for flat, SPACE to replay the tones, or Q to quit.")
            key = readchar.readkey()
            if key == readchar.key.UP:
                guess_direction = "up"
            elif key == readchar.key.DOWN:
                guess_direction = "down"
            elif key == " ":
                print("Replaying tones...")
                play_audio(audio_base, sample_rate)
                time.sleep(0.5)
                play_audio(audio_detuned, sample_rate)
            elif key.lower() == "q":
                sys.exit("Quitting the game.")
            else:
                print("Invalid key. Please press UP, DOWN, SPACE, or Q.")

        # Evaluate direction
        if (guess_direction == 'up' and is_sharp) or (guess_direction == 'down' and not is_sharp):
            print("Direction: Correct!")
            direction_score += 1
            direction_correct = True
        else:
            print("Direction: Incorrect!")
            direction_correct = False

        # Prompt for cents guess until valid input is received.
        while True:
            cents_input_raw = input(f"Guess the detune amount (in cents) {lower_bound:.2f} - {upper_bound:.2f} (or SPACE to replay the tones or 'q' to quit): ")
            # Check if user wants to quit:
            if cents_input_raw.lower().strip() == 'q':
                sys.exit("Quitting the game.")
            # Check if user pressed SPACE (we check raw input so spaces aren't stripped)
            if cents_input_raw == " ":
                print("Replaying tones...")
                play_audio(audio_base, sample_rate)
                time.sleep(0.5)
                play_audio(audio_detuned, sample_rate)
                continue  # prompt again
            # Attempt to parse the input as a float:
            try:
                guess_cents = float(cents_input_raw)
                break  # valid input, exit the loop
            except ValueError:
                # Invalid input; prompt again without any message.
                continue

        # Evaluate cents guess
        if guess_cents is not None:
            if 0.8 * guess_cents <= offset <= 1.2 * guess_cents:
                print(f"Cents: Correct! Offset = {offset:.2f}")
                cents_correct = True
                if direction_correct:
                    accuracy_score += 1
            else:
                print(f"Cents: Incorrect! The actual detune was {offset:.2f} cents.")
                cents_correct = False
        else:
            print("Cents: No valid guess provided.")
            cents_correct = False

        # Play appropriate feedback sound based on the outcome.
        if direction_correct and cents_correct:
            play_correct_feedback(sample_rate)
        elif (not direction_correct) and (not cents_correct):
            play_incorrect_feedback(sample_rate)
        elif (not direction_correct) and cents_correct:
            play_wrong_direction_accurate_feedback(sample_rate)
        elif direction_correct and (not cents_correct):
            play_correct_direction_inaccurate_feedback(sample_rate)
        
        # If both direction and cents are wrong, count it as a completely wrong round.
        if not direction_correct and not cents_correct:
            wrong_both_count += 1
            if wrong_both_count >= 5:
                print("\nYou've gotten 5 rounds completely wrong (both direction and cents).")
                break

    total_rounds = round_number + 1  # since round_number is 0-indexed
    print("\n=== Game Over ===")
    print(f"Rounds Played: {total_rounds}")
    print(f"Direction Score: {direction_score}/{total_rounds}")
    print(f"Accuracy Score : {accuracy_score}/{total_rounds}")
    direction_accuracy = (direction_score / total_rounds) * 100
    overall_accuracy = (accuracy_score / total_rounds) * 100
    print(f"Direction Precision: {direction_accuracy:.0f}%")
    print(f"Accuracy Precision: {overall_accuracy:.0f}%")

if __name__ == "__main__":
    main()
