import wave
import midi
from keras.models import load_model
from music21 import converter, instrument, note, chord, stream
import pickle
import numpy as np

def waveAudioEncrypt(songs,messages,audioId):
    song = wave.open(songs)
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    string= messages
    # Append dummy data to fill out rest of the bytes. Receiver shall detect and remove these characters.
    string = string + int((len(frame_bytes)-(len(string)*8*8))/8) *'#'
    # Convert text to bit array
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))

    # Replace LSB of each byte of the audio data by one bit from the text bit array
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    # Get the modified bytes
    frame_modified = bytes(frame_bytes)
    with wave.open("media/documents/{}.wav".format(audioId),'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)


def waveAudioDecrypt(audio):
    song = wave.open(audio, mode='rb')
    # Convert audio to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # Extract the LSB of each byte
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    # Convert byte array back to string
    string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
    # Cut off at the filler characters
    decoded = string.split("###")[0]
    
    return decoded

## process for the generation

def midigenerate(prediction_output):
    offset = 0 # Time
    output_notes = []

    for pattern in prediction_output:
        
        # if the pattern is a chord
        if ('+' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('+')
            temp_notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))  # create Note object for each note in the chord
                new_note.storedInstrument = instrument.Piano()
                temp_notes.append(new_note)
                
            
            new_chord = chord.Chord(temp_notes) # creates the chord() from the list of notes
            new_chord.offset = offset
            output_notes.append(new_chord)
        
        else:
                # if the pattern is a note
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)
            
        offset += 0.5

    return output_notes
    

## encrypt
def midiAudioEncrypt(messages,audioId):

    # loading the model weights
    model = load_model("static/model/new_weights.hdf5")

    # loading the model notes
    with open("static/model/notes", 'rb') as f:
        notes= pickle.load(f)

    pitchnames = sorted(set(notes))

    sequence_length = 100
    network_input = []

    ele_to_int = dict((ele, num) for num, ele in enumerate(pitchnames))

    for i in range(len(notes) - sequence_length):
        seq_in = notes[i : i+sequence_length] # contains 100 values
        network_input.append([ele_to_int[ch] for ch in seq_in])

    
    # Any random start index
    start = np.random.randint(len(network_input) - 1)

    # Mapping int_to_ele
    int_to_ele = dict((num, ele) for num, ele in enumerate(pitchnames))

    # Initial pattern 
    pattern = network_input[start]
    prediction_output = []

    n_vocab = len(pitchnames)
    # generate 200 elements
    
    for note_index in range(50):

        prediction_input = np.reshape(pattern, (1, len(pattern), 1)) # convert into numpy desired shape 
        prediction_input = prediction_input/float(n_vocab) # normalise
        
        prediction =  model.predict(prediction_input, verbose=0)
        
        idx = np.argmax(prediction)
        result = int_to_ele[idx]
        prediction_output.append(result) 
        
        pattern.append(idx)
        pattern = pattern[1:]

    output_notes = midigenerate(prediction_output)

    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp = "media/midi/{}.mid".format(audioId))


    # ## after the file is created encode the message in the file
    midi_song = 'media/midi/{}.mid'.format(audioId)
    ## read midi file
    tracks = midi.read_midifile(midi_song)
 
    # If the midi doesn't have tracks add one
    if len(tracks) == 0:
        tracks.append(midi.Track)

    # Instantiate a MIDI note off event, append it to the track
    off = midi.NoteOffEvent(tick=0, pitch=midi.G_3)
    tracks[0].insert(0, off)

    # Iterate message characters and insert them as program change event
    for character in messages:
        change_program = midi.ProgramChangeEvent(tick=0, data=[ord(character)])
        tracks[0].insert(0, change_program)

    # Instantiate a MIDI note on event, append it to the track
    on = midi.NoteOnEvent(tick=0, pitch=midi.G_3)
    tracks[0].insert(0, on)

    # Save the pattern to disk
    midi.write_midifile(midi_song, tracks)





def midiAudioDecrypt(audio):

    tracks = midi.read_midifile(audio)
    # Define a map and an index to store secrets
    message = ""
    
    # Iterate track events
    for event in tracks[0]:
       
        # When find on event with specific characteristics, create a list in the map
        if isinstance(event, midi.NoteOnEvent) and event.tick == 0 and event.get_pitch() == midi.G_3:
            pass
        # If find program change event store the character for the word into the map
        if isinstance(event, midi.ProgramChangeEvent) and event.tick == 0 :
            message += chr(event.data[0])
        
        # When find off event with specific characteristics, increment the index to store the next secret
        if isinstance(event, midi.NoteOffEvent) and event.tick == 0 and event.get_pitch() == midi.G_3:
            
            break

    print(message)
    return message[::-1]
   

