import io
import mido
import re
import hashlib

from . import hydata
from . import hymisc


class SongTimestamp:
    """Associates a timecode with a chord and some gameplay modifiers."""
    def __init__(self):      
        self.timecode = None
        self.chord = None
        
        self.flag_solo = False
        self.flag_sp = False
        self.activation_length = None

    def __str__(self):
        if self.flag_sp:
            mod = ", SP"
        elif self.activation_length:
            mod = f", Fill ({self.activation_length})"
        else:
            mod = ""
        return f"[{self.timecode.measurestr()}: {self.chord.rowstr()}{mod}]"

    def has_activation(self):
        return self.activation_length is not None


class SongIter:
    def __init__(self, song):
        self.i = 0
        self.tick = 0
        self.tpm_keys = list(song.tpm_changes.keys())
        self.tpm = song.tpm_changes[self.tpm_keys.pop(0)]
        self.bpm_keys = list(song.bpm_changes.keys())
        self.bpm = song.bpm_changes[self.bpm_keys.pop(0)]
        self.song = song

    def __iter__(self):
        return self
        
    def __next__(self):
        try:
            ts = self.song[self.i]
            self.i += 1
        except IndexError:
            raise StopIteration

        self.tick = ts.timecode.ticks
        pre_tpm = self.tpm
        if self.tpm_keys:
            if self.tick == self.tpm_keys[0]:
                # Timestamp is exactly on a timesig change
                self.tpm = self.song.tpm_changes[self.tpm_keys.pop(0)]
            elif self.tick > self.tpm_keys[0]:
                # Timestamp is past a timesig change, not on a border
                pre_tpm = self.tpm = self.song.tpm_changes[self.tpm_keys.pop(0)]
                
        if self.bpm_keys and self.tick >= self.bpm_keys[0]:
            self.bpm = self.song.bpm_changes[self.bpm_keys.pop(0)]
        
        return (ts, pre_tpm, self.tpm, self.bpm)

class Song:
    """The structure for charts that have been loaded in. A sequence of
    timestamps, plus tempo/meter changes.
    """
    def __init__(self, resolution):
        self._sequence = []
        
        """This song's conversions from ticks to any other time unit."""
        self.tick_resolution = resolution
        self.tpm_changes = {0: resolution * 4}
        self.bpm_changes = {}
        
        """Stub for song-wide analysis."""
        self.features = []
        
    def __iter__(self):
        return SongIter(self)
    
    def __getitem__(self, i, objtype=None):
        return self._sequence[i]
        
    def add_timestamp(self, ts):
        self._sequence.append(ts)
        
    @property
    def last(self):
        return self._sequence[-1]
    
    def check_activations(self):
        """ If a chart has no drum fills, add them in like Clone Hero would.
        
        Rule: Try to put activations on downbeats. A note needs to be within
        1/2 beat of the downbeat. Choose the closest note and if there's a tie
        use the later note. Activations are 1/2 measure long.
        Whenever an activation is placed, ignore the next 3 measures.
        """
        if all(not ts.has_activation() for ts in self._sequence):
            self.features.append('Auto-Generated Fills')
            
            # Each measure's closest note for becoming an activation fill
            measuremap = {}
            
            downbeat_ref = self.start_time()
            for timestamp, pre_tpm, tpm, bpm in self:
                if timestamp.chord is None:
                    continue
                # Downbeats near this chord
                for measure in [
                    timestamp.timecode.measure_beats_ticks[0] + 1,
                    timestamp.timecode.measure_beats_ticks[0] + 2
                ]:
                    # Get the tick location of this downbeat
                    if measure not in measuremap:
                        downbeat_ref = downbeat_ref.plusmeasure(
                            measure - (downbeat_ref.measure_beats_ticks[0] + 1),
                            self
                        )
                        measuremap[measure] = (downbeat_ref.ticks, None, None, None)
                    tick, best_ts, bestdist, _ = measuremap[measure]
                    
                    # Update the closest chord to this downbeat
                    dist = abs(tick - timestamp.timecode.ticks)
                    if best_ts is None or dist <= bestdist:
                        measuremap[measure] = (tick, timestamp, dist, pre_tpm)

            ACT_COOLDOWN_MEASURES = 4
            MAX_DISTANCE = self.tick_resolution // 2
            last_act_measure = None
            for measure in measuremap.keys():
                if last_act_measure is not None and measure < last_act_measure + ACT_COOLDOWN_MEASURES:
                    continue
                _, ts, bestdist, pre_tpm = measuremap[measure]
                if ts is not None and bestdist <= MAX_DISTANCE:
                    ts.activation_length = pre_tpm // 2
                    last_act_measure = measure

    def start_time(self):
        return hymisc.Timecode(0, self.tick_resolution, self.tpm_changes, self.bpm_changes)


class MidiParser:
    """Reads a .mid file to create a Song object."""
    def __init__(self):
        self.song = None
        
        # Parsing mode
        self.mode_difficulty = None
        self.mode_pro = None
        self.mode_bass2x = None
        
        # Parsing state
        self._chord = None
        self._msg_buffer = None
        self._flag_solo = None
        self._flag_cymbals = None
        self._flag_disco = None
        self._fill_start_tick = None
        self._fill_end_tick = None
        self._dynamics_enabled = None
        self._sp_start_tick = None

    def optype(self, msg, tick):
        """Parses individual midi messages into the actual actions the parser
        will take based on that message.
        
        We figure out these payloads but don't run them right away because 
        we may want to run them in a particular order, or filter them.
        
        See: op_* functions.
        
        Returns: (op_phase, op_func, *args)
        
        """
        # The actual conditions for note on/off in practice
        is_noteon = (
            msg.type == 'note_on' and msg.velocity > 0
        )
        is_noteoff = (
            msg.type == 'note_off'
            or msg.type == 'note_on' and msg.velocity == 0
        )
        
        # Text events that are used for disco flip
        r_disco_on_x = r'\[?mix.3.drums\d?d\]?'
        r_disco_off_x = r'\[?mix.3.drums\d?(dnoflip)?\]?'
        
        r_dynamics = r'\[?ENABLE_CHART_DYNAMICS\]?'
            
        # Interpret midi message for which procedure to return
        match msg:
            case mido.MetaMessage(text=t) if re.fullmatch(r_dynamics, t):
                return ('pre', self.op_enable_dynamics)
            case mido.MetaMessage(text=t) if re.fullmatch(r_disco_on_x, t):
                return ('pre', self.op_disco, True)
            case mido.MetaMessage(text=t) if re.fullmatch(r_disco_off_x, t):
                return ('pre', self.op_disco, False)
            case mido.MetaMessage(type='set_tempo'):
                return ('time', self.op_tempo, tick, msg.tempo)
            case mido.MetaMessage(type='time_signature'):
                return ('time', self.op_timesig, tick, msg.numerator, msg.denominator)
            case mido.Message(note=120) if is_noteon:
                return ('post-delayed', self.op_fillstart, tick)
            case mido.Message(note=120) if is_noteoff:
                return ('pre', self.op_store_fillend, tick)
            case mido.Message(note=116) if is_noteon:
                return ('pre' if self._sp_start_tick is None else 'pre-delayed', self.op_sp_start, tick)
            case mido.Message(note=116) if is_noteoff:
                return ('pre-delayed' if self._sp_start_tick is None else 'pre', self.op_sp_end)
            case mido.Message(note=112) if is_noteon:
                return ('pre', self.op_tom, hydata.NoteColor.GREEN, hydata.NoteCymbalType.NORMAL)
            case mido.Message(note=112) if is_noteoff:
                return ('pre', self.op_tom, hydata.NoteColor.GREEN, hydata.NoteCymbalType.CYMBAL)
            case mido.Message(note=111) if is_noteon:
                return ('pre', self.op_tom, hydata.NoteColor.BLUE, hydata.NoteCymbalType.NORMAL)
            case mido.Message(note=111) if is_noteoff:
                return ('pre', self.op_tom, hydata.NoteColor.BLUE, hydata.NoteCymbalType.CYMBAL)
            case mido.Message(note=110) if is_noteon:
                return ('pre', self.op_tom, hydata.NoteColor.YELLOW, hydata.NoteCymbalType.NORMAL)
            case mido.Message(note=110) if is_noteoff:
                return ('pre', self.op_tom, hydata.NoteColor.YELLOW, hydata.NoteCymbalType.CYMBAL)
            case mido.Message(note=103) if is_noteon:
                return ('pre', self.op_solo, True)
            case mido.Message(note=103) if is_noteoff:
                return ('pre', self.op_solo, False)
            case mido.Message(note=100, velocity=127) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.GREEN, hydata.NoteDynamicType.ACCENT, False)
            case mido.Message(note=100, velocity=1) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.GREEN, hydata.NoteDynamicType.GHOST, False)
            case mido.Message(note=100) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.GREEN, hydata.NoteDynamicType.NORMAL, False)
            case mido.Message(note=99, velocity=127) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.BLUE, hydata.NoteDynamicType.ACCENT, False)
            case mido.Message(note=99, velocity=1) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.BLUE, hydata.NoteDynamicType.GHOST, False)
            case mido.Message(note=99) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.BLUE, hydata.NoteDynamicType.NORMAL, False)
            case mido.Message(note=98, velocity=127) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.YELLOW, hydata.NoteDynamicType.ACCENT, False)
            case mido.Message(note=98, velocity=1) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.YELLOW, hydata.NoteDynamicType.GHOST, False)
            case mido.Message(note=98) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.YELLOW, hydata.NoteDynamicType.NORMAL, False)
            case mido.Message(note=97, velocity=127) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.RED, hydata.NoteDynamicType.ACCENT, False)
            case mido.Message(note=97, velocity=1) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.RED, hydata.NoteDynamicType.GHOST, False)
            case mido.Message(note=97) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.RED, hydata.NoteDynamicType.NORMAL, False)
            case mido.Message(note=96) if is_noteon:
                return ('notes', self.op_note, hydata.NoteColor.KICK, hydata.NoteDynamicType.NORMAL, False)
            case mido.Message(note=95) if is_noteon and self.mode_bass2x:
                return ('notes', self.op_note, hydata.NoteColor.KICK, hydata.NoteDynamicType.NORMAL, True)
            case _:
                return (None, None)

    """Op functions: Each midi event results in one of these."""
    
    def op_enable_dynamics(self):
        self._dynamics_enabled = True
        
    def op_disco(self, is_on):
        self._flag_disco = is_on
    
    def op_tempo(self, tick, miditempo):
        self.song.bpm_changes[tick] = 60000000 / miditempo
    
    def op_timesig(self, tick, numerator, denominator):
        self.song.tpm_changes[tick] = self.song.tick_resolution * numerator * 4 // denominator
    
    def op_fillstart(self, tick):
        self._fill_start_tick = tick
        
        # A fill start can "interrupt" a previous fill that was waiting for a 
        # note in order to resolve. But since a new fill is starting, we can
        # conclude that previous fill is empty (grr)
        self._fill_end_tick = None
    
    def op_store_fillend(self, tick):
        self._fill_end_tick = tick
        
    def op_apply_fill(self, starttick):
        try:
            latest_note = self.song[-1]
        except IndexError:
            # Fill ended, but there hasn't been a single note yet.
            return
        
        # Double check that the latest note is recent enough to be in the fill
        if latest_note.timecode.ticks >= starttick:
            # Due to correction mechanics, end tick is not always based on the
            # authored phrase length
            endtick = latest_note.timecode.ticks
            latest_note.activation_length = endtick - starttick
    
    def op_sp_start(self, starttick):
        self._sp_start_tick = starttick
        
    def op_sp_end(self):
        try:
            latest_note = self.song[-1]
        except IndexError:
            # SP phrase, but there hasn't been a single note yet.
            self._sp_start_tick = None
            return
            
        if latest_note.timecode.ticks >= self._sp_start_tick:
            # Double check that latest note is recent enough to be in the SP
            latest_note.flag_sp = True
        self._sp_start_tick = None
    
    def op_tom(self, color, cymbal):
        self._flag_cymbals[color] = cymbal
    
    def op_solo(self, is_on):
        self._flag_solo = is_on
    
    def op_note(self, color, dynamic, is2x):
        note = self._chord.add_note(color)
        if self._dynamics_enabled:
            note.dynamictype = dynamic
        else:
            note.dynamictype = hydata.NoteDynamicType.NORMAL
        if color.allows_cymbals() and self.mode_pro:
            note.cymbaltype = self._flag_cymbals[color]
        note.is2x = is2x
    
    def push_timestamp(self, tick):
        """Process all the events that happened simultaneously on this tick.
        
        Because we've collected the events, we can easily do them in whichever
        order as configured in the optype function.
        
        """
        self._chord = hydata.Chord()
        
        ops = [self.optype(msg, tick) for msg in self._msg_buffer]
        
        # Prepare notes (not added yet)
        for phase in ['pre', 'pre-delayed', 'notes']:
            for op_phase, op, *op_args in ops:
                if op_phase == phase:
                    try:
                        op(*op_args)
                    except hymisc.ChartFileError:
                        pass
        
        # Phrase end: Activation (waits until a timestamp with a chord)
        if self._chord.count() and self._fill_end_tick is not None and tick >= self._fill_end_tick:
            # This chord is at or past the end of an activation marker
            try:
                prevchord_dist = self._fill_end_tick - self.song[-1].timecode.ticks
            except IndexError:
                prevchord_dist = None
            nextchord_dist = tick - self._fill_end_tick
            
            if (nextchord_dist <= self.song.tick_resolution // 32
                and (prevchord_dist is None or nextchord_dist <= prevchord_dist)
            ):
                # Let the activation apply to this chord if it's at most
                # a 1/128th note after AND the previous chord isn't closer
                order = 'post'
            else:
                # Let the activation fall back to the previous chord
                # by assigning the activation before adding this chord
                order = 'pre_timestamp'
            ops.append((order, self.op_apply_fill, self._fill_start_tick))
            self._fill_start_tick = None
            self._fill_end_tick = None
        
        # Parsed actions that apply before the timestamp
        for op_phase, op, *op_args in ops:
            if op_phase == 'pre_timestamp':
                try:
                    op(*op_args)
                except hymisc.ChartFileError:
                    pass
        
        # Add the timestamp to the song
        if self._chord.count():
            timestamp = SongTimestamp()
            timestamp.chord = self._chord
            timestamp.timecode = hymisc.Timecode(tick, self.song.tick_resolution, self.song.tpm_changes, self.song.bpm_changes)
            timestamp.flag_solo = self._flag_solo
            if self._flag_disco:
                timestamp.chord.apply_disco_flip()
            
            self.song.add_timestamp(timestamp)
            self._chord = None
            
        # Parsed actions that apply after the timestamp
        for phase in ['post', 'post-delayed']:
            for op_phase, op, *op_args in ops:
                    if op_phase == phase:
                        try:
                            op(*op_args)
                        except hymisc.ChartFileError:
                            pass
            
        self._msg_buffer = []
    
    def parsefile(self, filename, m_difficulty, m_pro, m_bass2x):
        with open(filename, 'rb') as file:
            self.parse(file, m_difficulty, m_pro, m_bass2x)
    
    def parsebytes(self, chartbytes, m_difficulty, m_pro, m_bass2x):
        print("Midi parsebytes :>")
        file = io.BytesIO(chartbytes)
        self.parse(file, m_difficulty, m_pro, m_bass2x)
    
    def parse(self, file, m_difficulty, m_pro, m_bass2x):
        """After calling this, self.song will reflect the input filename.
        Must be .mid.
        """
        # Load from MIDI
        mid = mido.MidiFile(file=file, clip=True)
        
        # Parser settings
        self.mode_difficulty = m_difficulty
        self.mode_pro = m_pro
        self.mode_bass2x = m_bass2x

        # Initialize Song
        self.song = Song(mid.ticks_per_beat)
        
        # Map tempo and time signatures
        elapsed_ticks = 0
        for msg in mid.tracks[0]:
            elapsed_ticks += msg.time
            op_phase, op, *op_args = self.optype(msg, elapsed_ticks)
            if op_phase == 'time':
                op(*op_args)
        
        # Add from the drum track to our Song
        for track in mid.tracks:
            if track.name == "PART DRUMS":
                elapsed_ticks = 0
                self._msg_buffer = []
                self._flag_solo = False
                self._flag_disco = False
                self._flag_cymbals = {
                    hydata.NoteColor.GREEN: hydata.NoteCymbalType.CYMBAL,
                    hydata.NoteColor.BLUE: hydata.NoteCymbalType.CYMBAL,
                    hydata.NoteColor.YELLOW: hydata.NoteCymbalType.CYMBAL
                }
                self._dynamics_enabled = False
                for msg in track:
                    if msg.time != 0:
                        # Process timestamp first
                        self.push_timestamp(elapsed_ticks)
                        elapsed_ticks += msg.time
                    
                    # Add message to group that will eventually be a timestamp
                    self._msg_buffer.append(msg)
                
                # Process a remaining timestamp if any
                self.push_timestamp(elapsed_ticks)
                break
        
        self.song.check_activations()


class ChartSection:
    """Much like a config, .chart data goes under a section name."""
    def __init__(self):
        self.name = None
        self.data = {}

class ChartDataEntry:
    """A bunch of values that are None, or set to a value if this entry in
    the .chart file was for that value.
    
    To do: clean how the key works
    
    """
    def __init__(self, keystr, valuestr):
        keystr = keystr.strip()
        valuestr = valuestr.strip()
        
        self.key_name = None
        self.key_tick = None
        
        self.property = None
        
        self.ts_numerator = None
        self.ts_denominator = None
        
        self.tempo_bpm = None
        
        self.textevent = None
        self.flagevent = None
        
        self.notevalue = None
        self.notelength = None
        
        self.phrasevalue = None
        self.phraselength = None
        
        self.solo_start = False
        self.solo_end = False
        
        self.discoflip_enable = False
        self.discoflip_disable = False
        self.discoflip_difficulty = None
        
        try:
            self.key_tick = int(keystr)
        except ValueError:
            self.key_name = keystr
        
        r_disco_on_x = r'\[?mix.3.drums\d?d\]?'
        r_disco_off_x = r'\[?mix.3.drums\d?(dnoflip)?\]?'
            
        match (valuestr, valuestr.split()):
            case v, _ if self.key_tick is None:
                try:
                    self.property = int(v)
                except ValueError:
                    self.property = v
            case _, ["TS", n]:
                self.ts_numerator = int(n)
                self.ts_denominator = 4
            case _, ["TS", n, d]:
                self.ts_numerator = int(n)
                self.ts_denominator = 2**int(d)
            case _, ["B", bpm]:
                self.tempo_bpm = int(bpm) / 1000.0
            case _, ["E", "solo"]:
                self.solo_start = True
            case _, ["E", "soloend"]:
                self.solo_end = True
            case _, ["E", event] if re.fullmatch(r_disco_off_x, event):
                self.discoflip_disable = True
            case _, ["E", event] if re.fullmatch(r_disco_on_x, event):
                self.discoflip_enable = True
            case _, ["E", *anywords]:
                self.textevent = ' '.join(anywords)
            case _, ["N", v, length]:
                self.notevalue = int(v)
                self.notelength = int(length)
            case _, ["S", v, length]:
                self.phrasevalue = int(v)
                self.phraselength = int(length)


    def is_property(self):
        return self.property != None

    def is_tick_data(self):
        return self.key_tick != None

    def key(self):
        return self.key_tick if self.is_tick_data() else self.key_name
        
class ChartParser:
    """Reads a .chart file to create a Song object."""
    def __init__(self):
        self.song = None
        self.sections = {}
        
        # Parsing mode
        self.mode_difficulty = None
        self.mode_pro = None
        self.mode_bass2x = None
        
        # Parsing state
        self._chord = None
        self._flag_solo = None
        self._flag_disco = None
        self._sp_end_tick = None
        self._fill_start_tick = None
        self._fill_end_tick = None
    
    def load_sections(self, file):
        """Loads the chartfile's sections from text form so they can be 
        accessed easily.
        
        To do: This can be a bit more robust (USE UNIT TESTS)
        """
        wip_section = None
        open_block = False
        for line_bytes in file:
            line = line_bytes.decode('utf-8').strip()
            if wip_section:
                if line.rstrip() == "{":
                    # Start a block
                    assert(not open_block)
                    open_block = True
                elif line.rstrip() == "}":
                    # End the block and assign the result
                    assert(open_block)
                    open_block = False
                    self.sections[wip_section.name] = wip_section
                    wip_section = None
                else:
                    # Continue the block and make an entry in it
                    assert(open_block)
                    lhs = line.split('=')[0].strip()
                    rhs = line.split('=')[1].strip()
                    
                    dataentry = ChartDataEntry(lhs, rhs)
                    
                    # Multiple entries on the same key can stack
                    if dataentry.key() in wip_section.data:
                        wip_section.data[dataentry.key()].append(dataentry)
                    else:
                        wip_section.data[dataentry.key()] = [dataentry]
            else:
                assert(not open_block)
                # start a new section
                wip_section = ChartSection()
                wip_section.name = re.findall(r'\[.*\]', line)[0][1:-1]
    
    def optype(self, entry, tick):
        match entry:
            case ChartDataEntry(discoflip_enable=True):
                return ('pre', self.op_disco, True)
            case ChartDataEntry(discoflip_disable=True):
                return ('pre', self.op_disco, False)
            case ChartDataEntry(tempo_bpm=bpm) if bpm is not None:
                return ('time', self.op_tempo, tick, bpm)
            case ChartDataEntry(ts_numerator=n, ts_denominator=d) if n:
                return ('time', self.op_timesig, tick, n, d)
            case ChartDataEntry(solo_start=True):
                return ('pre', self.op_solo, True)
            case ChartDataEntry(solo_end=True):
                return ('post', self.op_solo, False)
            case ChartDataEntry(notevalue=0):
                return ('notes', self.op_note, hydata.NoteColor.KICK)
            case ChartDataEntry(notevalue=1):
                return ('notes', self.op_note, hydata.NoteColor.RED)
            case ChartDataEntry(notevalue=2):
                return ('notes', self.op_note, hydata.NoteColor.YELLOW)
            case ChartDataEntry(notevalue=3):
                return ('notes', self.op_note, hydata.NoteColor.BLUE)
            case ChartDataEntry(notevalue=4):
                return ('notes', self.op_note, hydata.NoteColor.GREEN)
            case ChartDataEntry(notevalue=32) if self.mode_bass2x:
                return ('notes', self.op_2x)
            case ChartDataEntry(notevalue=34):
                return ('note_mods', self.op_accent, hydata.NoteColor.RED)
            case ChartDataEntry(notevalue=35):
                return ('note_mods', self.op_accent, hydata.NoteColor.YELLOW)
            case ChartDataEntry(notevalue=36):
                return ('note_mods', self.op_accent, hydata.NoteColor.BLUE)
            case ChartDataEntry(notevalue=37):
                return ('note_mods', self.op_accent, hydata.NoteColor.GREEN)
            case ChartDataEntry(notevalue=40):
                return ('note_mods', self.op_ghost, hydata.NoteColor.RED)
            case ChartDataEntry(notevalue=41):
                return ('note_mods', self.op_ghost, hydata.NoteColor.YELLOW)
            case ChartDataEntry(notevalue=42):
                return ('note_mods', self.op_ghost, hydata.NoteColor.BLUE)
            case ChartDataEntry(notevalue=43):
                return ('note_mods', self.op_ghost, hydata.NoteColor.GREEN)
            case ChartDataEntry(notevalue=66) if self.mode_pro:
                return ('note_mods', self.op_cymbal, hydata.NoteColor.YELLOW)
            case ChartDataEntry(notevalue=67) if self.mode_pro:
                return ('note_mods', self.op_cymbal, hydata.NoteColor.BLUE)
            case ChartDataEntry(notevalue=68) if self.mode_pro:
                return ('note_mods', self.op_cymbal, hydata.NoteColor.GREEN)
            case ChartDataEntry(phrasevalue=2, phraselength=length):
                return ('pre', self.op_sp_start, tick, tick + length)
            case ChartDataEntry(phrasevalue=64, phraselength=length):
                return ('post-delayed', self.op_fillstart, tick, tick + length)
            case _:
                return (None, None)
    
    def op_disco(self, is_on):
        self._flag_disco = is_on
    
    def op_tempo(self, tick, bpm):
        self.song.bpm_changes[tick] = bpm
    
    def op_timesig(self, tick, numerator, denominator):
        self.song.tpm_changes[tick] = self.song.tick_resolution * numerator * 4 // denominator
    
    def op_fillstart(self, starttick, endtick):
        self._fill_start_tick = starttick
        self._fill_end_tick = endtick
    
    def op_fillend(self, starttick):
        try:
            latest_note = self.song[-1]
        except IndexError:
            # Fill, but there hasn't been a single note yet.
            return
        
        # Double check that latest note is recent enough
        if latest_note.timecode.ticks >= starttick:
            # Due to correction mechanics, end tick is not always based on the
            # authored phrase length
            endtick = latest_note.timecode.ticks
            latest_note.activation_length = endtick - starttick
    
    def op_sp_start(self, starttick, endtick):
        self._sp_start_tick = starttick
        self._sp_end_tick = endtick
    
    def op_sp_end(self, starttick):
        try:
            latest_note = self.song[-1]
        except IndexError:
            # SP phrase, but there hasn't been a single note yet.
            self._sp_end_tick = None
            return
        
        if latest_note.timecode.ticks >= starttick:
            # Double check that latest note is recent enough to be in the SP
            latest_note.flag_sp = True
        self._sp_end_tick = None
    
    def op_solo(self, is_on):
        self._flag_solo = is_on
    
    def op_note(self, color):
        self._chord.add_note(color)
    
    def op_2x(self):
        self._chord.add_2x()
    
    def op_accent(self, color):
        self._chord.apply_accent(color)
    
    def op_ghost(self, color):
        self._chord.apply_ghost(color)
    
    def op_cymbal(self, color):
        self._chord.apply_cymbal(color)
    
    def push_timestamp(self, tick, entries):
        """Process all the events that happened simultaneously on this tick.
        
        Because we've collected the events, we can easily do them in whichever
        order as configured in the optype function.
        
        """
        self._chord = hydata.Chord()
        
        ops = [self.optype(entry, tick) for entry in entries]
        
        # Prepare notes (not added yet)
        for phase in ['notes', 'note_mods']:
            for op_phase, op, *op_args in ops:
                if op_phase == phase:
                    try:
                        op(*op_args)
                    except hymisc.ChartFileError:
                        pass
        
        # Phrase end: SP 
        if self._sp_end_tick is not None and tick >= self._sp_end_tick:
            ops.insert(0, ('pre', self.op_sp_end, self._sp_start_tick))
        
        # Phrase end: Activation (waits until a timestamp with a chord)
        if self._chord.count() and self._fill_end_tick is not None and tick >= self._fill_end_tick:
            # This chord is at or past the end of an activation marker
            try:
                prevchord_dist = self._fill_end_tick - self.song[-1].timecode.ticks
            except IndexError:
                prevchord_dist = None
            
            nextchord_dist = tick - self._fill_end_tick
            if (nextchord_dist <= self.song.tick_resolution // 32
                and (prevchord_dist is None or nextchord_dist <= prevchord_dist)
            ):
                # Let the activation apply to this chord if it's at most
                # a 1/128th note after AND the previous chord isn't closer
                order = 'post'
            else:
                # Let the activation fall back to the previous chord
                # by assigning the activation before adding this chord
                order = 'pre'
            ops.append((order, self.op_fillend, self._fill_start_tick))
            self._fill_start_tick = None
            self._fill_end_tick = None
        
        # Parsed actions that apply before the timestamp
        for op_phase, op, *op_args in ops:
            if op_phase == 'pre':
                try:
                    op(*op_args)
                except hymisc.ChartFileError:
                    pass
    
        # Add the timestamp to the song
        if self._chord.count():
            timestamp = SongTimestamp()
            timestamp.chord = self._chord
            timestamp.timecode = hymisc.Timecode(tick, self.song.tick_resolution, self.song.tpm_changes, self.song.bpm_changes)
            timestamp.flag_solo = self._flag_solo
            if self._flag_disco:
                timestamp.chord.apply_disco_flip()
                
            self.song.add_timestamp(timestamp)
            self._chord = None
            
        # Parsed actions that apply after the timestamp
        for phase in ['post', 'post-delayed']:
            for op_phase, op, *op_args in ops:
                if op_phase == phase:
                    try:
                        op(*op_args)
                    except hymisc.ChartFileError:
                        pass
    
    def parsefile(self, filename, m_difficulty, m_pro, m_bass2x):
        with open(filename, mode='rb') as file:
            self.parse(file, m_difficulty, m_pro, m_bass2x)
    
    def parsebytes(self, chartbytes, m_difficulty, m_pro, m_bass2x):
        print("Chart parsebytes :>")
        file = io.BytesIO(chartbytes)
        self.parse(file, m_difficulty, m_pro, m_bass2x)
    
    def parse(self, file, m_difficulty, m_pro, m_bass2x):
        """After this function, self.song will be ready.
        Must be .chart.
        """
        # Load from txt
        self.load_sections(file)
        
        # Parser settings
        self.mode_difficulty = m_difficulty
        self.mode_pro = m_pro
        self.mode_bass2x = m_bass2x
        
        # Initialize Song
        tick_resolution = int(self.sections["Song"].data["Resolution"][0].property)
        self.song = Song(tick_resolution)
        
        # Map tempo and time signatures
        for entry_tick, entries in self.sections["SyncTrack"].data.items():
            for entry in entries:
                op_phase, op, *op_args = self.optype(entry, entry_tick)
                if op_phase == 'time':
                    op(*op_args)
        
        self._flag_solo = False
        self._flag_disco = False
        
        # Add from the drum chart to our Song
        if 'ExpertDrums' in self.sections:
            for tick, tick_entries in self.sections['ExpertDrums'].data.items():
                self.push_timestamp(tick, tick_entries)
        
        self.song.check_activations()
