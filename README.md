Ear Training Game

This is a Python-based ear training game designed to help users develop their relative pitch perception, especially for differentiating microtonal intervals. 
The game presents two consecutive tones (using sine waves) and challenges you to identify both the direction (sharp/flat) and the detune amount (in cents).



This project requires Python 3 and the following non-standard libraries:

	•	numpy
	•	sounddevice
	•	readchar



Sample Gameplay:

"
=== Round 37 === (Round 37/40) Player has 4/5 Oopsie Daisies Left
Playing base tone: F#4 (377.14 Hz)
Playing detuned tone...
Press UP for sharp, DOWN for flat, SPACE to replay the tones, or Q to quit.
Direction: Correct!
Guess the detune amount (in cents) 12.08 - 48.32 (or SPACE to replay the tones or 'q' to quit): 20
Cents: Correct! Offset = 16.05

=== Round 38 === (Round 38/40) Player has 4/5 Oopsie Daisies Left
Playing base tone: A4 (440.00 Hz)
Playing detuned tone...
Press UP for sharp, DOWN for flat, SPACE to replay the tones, or Q to quit.
Direction: Correct!
Guess the detune amount (in cents) 11.84 - 47.35 (or SPACE to replay the tones or 'q' to quit): 40
Cents: Correct! Offset = 35.05

=== Round 39 === (Round 39/40) Player has 4/5 Oopsie Daisies Left
Playing base tone: G#3 (204.29 Hz)
Playing detuned tone...
Press UP for sharp, DOWN for flat, SPACE to replay the tones, or Q to quit.
Direction: Incorrect!
Guess the detune amount (in cents) 11.60 - 46.41 (or SPACE to replay the tones or 'q' to quit): 23
Cents: Incorrect! The actual detune was 15.51 cents.

=== Round 40 === (Round 40/40) Player has 3/5 Oopsie Daisies Left
Playing base tone: A2 (110.00 Hz)
Playing detuned tone...
Press UP for sharp, DOWN for flat, SPACE to replay the tones, or Q to quit.
Direction: Incorrect!
Guess the detune amount (in cents) 11.37 - 45.48 (or SPACE to replay the tones or 'q' to quit): 23
Cents: Incorrect! The actual detune was 11.85 cents.

=== Game Over ===
Rounds Played: 40
Direction Score: 35/40
Distance Score: 11/40
Direction Accuracy: 88%
Distance Accuracy: 28%
"


