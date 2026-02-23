import json
import re
from enum import Enum
from abc import ABC, abstractmethod

from . import hymisc
from . import hyencode

def json_save(obj):
    """Object --> dict conversion."""
    if isinstance(obj, HydraRecord):
        return {
            '__obj__': 'record',
            
            'hyversion': obj.hyversion,
            'ms': obj.ms_limit,
            'paths': obj._paths,
        }
    
    if isinstance(obj, Path):
        return {
            '__obj__': 'path',
        
            'multsqueezes': obj.multsqueezes,
            'activations': obj._activations,
            
            'score_base': obj.score_base,
            'score_combo': obj.score_combo,
            'score_sp': obj.score_sp,
            'score_solo': obj.score_solo,
            'score_accents': obj.score_accents,
            'score_ghosts': obj.score_ghosts,
            
            'notecount': obj.notecount,
            
            'leftover_sp': obj.leftover_sp,
            'sk_gho': obj.skipped_ghosts,
            'sk_acc': obj.skipped_accents,
            
            'ref_totalscore': obj.totalscore(),
            
            'variants': obj.variants,            
            'var_point': obj.var_point,
        }
    
    if isinstance(obj, MultSqueeze):
        return {
            '__obj__': 'msq',
        
            'chord': obj.chord.code(),
            'combo': obj.combo,
        }
    
    if isinstance(obj, Activation):
        return {
            '__obj__': 'activation',
        
            'skips': obj.skips,
            'tc': obj.timecode.ticks,
            'chord': obj.chord.code(),
            'sp_meter': obj.sp_meter,
            
            'fe_pts': obj.frontend_points,
            'backends': obj.backends,
            
            'sqinouts': obj.sqinouts,
            
            'e_offset': obj.e_offset,
        }
    
    if isinstance(obj, FrontendSqueeze):
        return {
            '__obj__': 'fsq',
        
            'chord': obj.chord.code(),
            'points': obj.points,
        }
        
    if isinstance(obj, SqIn):
        return {
            '__obj__': 'sqin',
            
            'offset_ms': obj.offset
        }
        
    if isinstance(obj, SqOut):
        return {
            '__obj__': 'sqout',
            
            'offset_ms': obj.offset
        }
    
    if isinstance(obj, BackendSqueeze):
        return {
            '__obj__': 'bsq',
        
            'tc': obj.timecode.ticks,
            'chord': obj.chord.code(),
            'points': obj.points,
            'sqout_points': obj.sqout_points,
            'is_sp': obj.is_sp,
            'offset_ms': obj.offset_ms,
    }
    
    raise TypeError(f"Unhandled type: {type(obj)}")
    
def json_load(_dict):
    """JSON has loaded a dict; try to fit it to Hydra data types.
    
    Hydra data types are saved with an __obj__ value to facilitate this.
    
    The top level maps hyhash keys to a 'records' map with keys based on
    difficulty/pro/2x. Everything after that is a recursive hydata object
    or a stripped down representation of one.
    """
    try:
        obj_code = _dict['__obj__']
    except KeyError:
        # Not one of our objects, just a dict
        try:
            return {int(k):v for k,v in _dict.items()}
        except ValueError:
            return _dict
    
    if obj_code == 'record':
        o = HydraRecord()
        o.hyversion = tuple(_dict['hyversion'])
        
        if not o.is_version_compatible():
            return o
        
        o.ms_limit = _dict['ms']
        o._paths = _dict['paths']
        
        for p in o._paths:
            p.prepare_variants()
        
        return o
    
    try:
        if obj_code == 'path':
            o = Path()
            o.multsqueezes = _dict['multsqueezes']
            o._activations = _dict['activations']
            
            o.score_base = _dict['score_base']
            o.score_combo = _dict['score_combo']
            o.score_sp = _dict['score_sp']
            o.score_solo = _dict['score_solo']
            o.score_accents = _dict['score_accents']
            o.score_ghosts = _dict['score_ghosts']
            
            o.notecount = _dict['notecount']
            
            o.leftover_sp = _dict['leftover_sp']
            o.skipped_ghosts = _dict['sk_gho']
            o.skipped_accents = _dict['sk_acc']
            
            o.variants = _dict['variants']            
            o.var_point = _dict['var_point']
            
            return o
        
        if obj_code == 'msq':
            o = MultSqueeze(Chord.from_code(_dict['chord']), _dict['combo'])
            
            return o
        
        if obj_code == 'activation':
            o = Activation()
            o.skips = _dict['skips']
            o.timecode = _dict['tc']
            o.chord = Chord.from_code(_dict['chord'])
            o.sp_meter = _dict['sp_meter']
            
            o.frontend_points = _dict['fe_pts']
            o.backends = _dict['backends']
            
            o.sqinouts = _dict['sqinouts']
            
            o.e_offset = _dict['e_offset']
        
            return o
        
        if obj_code == 'fsq':
            o = FrontendSqueeze(Chord.from_code(_dict['chord']), _dict['points'])

            return o
        
        if obj_code == 'sqin':
            o = SqIn(_dict['offset_ms'])

            return o
            
        if obj_code == 'sqout':
            o = SqOut(_dict['offset_ms'])

            return o
            
        if obj_code == 'bsq':
            o = BackendSqueeze(
                _dict['tc'],
                Chord.from_code(_dict['chord']),
                _dict['points'],
                _dict['sqout_points'],
                _dict['is_sp'],
            )
            o.offset_ms = _dict['offset_ms']
            
            return o
    except KeyError:
        return "<Invalid object>"
        
    return "<Unrecognized object>"


class HydraRecord:
    """A "printout" representing one analyzed chart.
    
    Each unique chart file (hash) can have 1 unique HydraRecord per combination
    of difficulty, pro/non-pro, and 2x/1x bass (chartmode).
    
    Multiple paths for a given chart are grouped within the same hydata.
    
    A hydata stores the version of Hydra that created it.
    
    """
    def __init__(self):   
        # Made by this version of Hydra.
        self.hyversion = hymisc.HYDRA_VERSION
        
        self.ms_limit = None
        
        # Path results. Contains nested paths due to the variant system.
        self._paths = []

    def __eq__(self, other):
        # Not sure if deep equality is what we want here, leaving it for now
        raise NotImplementedError
    
    def is_version_compatible(self):
        return self.hyversion == hymisc.HYDRA_VERSION

    def best_path(self):
        return self._paths[0]
        
    def all_paths(self):
        """Generates all paths with tree traversal (so it visits all variants)."""
        pathstovisit = [p for p in self._paths]
        while pathstovisit:
            p = pathstovisit.pop(0)
            pathstovisit = p.variants + pathstovisit
            yield p
            

class Path:
    """A particular combination of SP activations that was found during
    analysis as well as the simulated score for a run that does these
    activations.
    
    Mult squeezes are also stored here; their point values are technically
    path dependent.
    """
    def __init__(self):
        # Path characteristics
        self.multsqueezes = []
        self._activations = []
        self.notecount = 0
        self.leftover_sp = 0
        self.skipped_ghosts = 0
        self.skipped_accents = 0
        
        # Score breakdown categories from Clone Hero
        self.score_base = 0
        self.score_combo = 0
        self.score_sp = 0
        self.score_solo = 0 
        self.score_accents = 0
        self.score_ghosts = 0
        
        # List of paths that are tied with this path; these are stored as
        # nested paths that converge with this path at a certain point.
        self.variants = []
        
        self.var_point = None        
        # Activations that can just be copied from this variant's base path.
        # Not saved/loaded.
        self._variant_tail = []
   
    def __eq__(self, other):
        for listattr in ['multsqueezes', 'activations']:
            a = getattr(self, listattr)
            b = getattr(other, listattr)
            if len(a) != len(b):
                return False
            for i in range(len(a)):
                if a[i] != b[i]:
                    return False
        
        for attr in [
            'score_base', 'score_combo', 'score_sp', 'score_solo',
            'score_accents', 'score_ghosts', 'notecount', 'leftover_sp'
        ]:
            if getattr(self, attr) != getattr(other, attr):
                return False
                
        return True
    
    def __str__(self):
        return self.pathstring()
        
    def __len__(self):
        return len(list(self.all_activations()))
        
    def has_activations(self):
        return len(self) != 0
        
    def all_activations(self):
        for act in self._activations:
            yield act
        for act in self._variant_tail:
            yield act
    
    def get_activation(self, i):
        return list(self.all_activations())[i]
        
    def is_variant(self):
        return self.var_point is not None
        
    def prepare_variants(self):
        """Recursive preparation of variants (copying the shared info from the
        base path to its variants)."""
        for v in self.variants:
            v._variant_tail = list(self.all_activations())[v.var_point:]
            for attr in ['score_base', 'score_combo', 'score_sp', 'score_solo', 'score_accents', 'score_ghosts', 'notecount', 'leftover_sp']:
                setattr(v, attr, getattr(self, attr))
            v.prepare_variants()
    
    def totalscore(self):
        return (
            self.score_base + self.score_combo + self.score_sp
            + self.score_solo + self.score_accents + self.score_ghosts
        )
    
    def pathstring(self):
        if self.has_activations():
            return ' '.join((str(a.notationstr()) for a in self.all_activations()))
        else:
            return "(No activations.)"
            
    def pathstring_verbose(self):
        sections = []
        
        # Mult squeezes
        if self.multsqueezes:
            sections.append(", ".join([f"{multsq.multiplier}x" for multsq in self.multsqueezes]))
        else:
            sections.append("(No mult squeezes.)")
        
        # Activations
        if self.has_activations():
            sections.append(' '.join([a.notationstr_verbose() for a in self.all_activations()]))
        else:
            sections.append("(No activations.)")
            
        # Score
        sections.append(f"Score: {self.totalscore():,}")
        
        return " | ".join(sections)

    def avg_mult(self):
        multscore = self.totalscore() - self.score_solo
        basescore = self.score_base + self.score_ghosts + self.score_accents
        return float(multscore / basescore)

    def copy(self):
        c = Path()
        
        # New list moving forward, shared previous activations
        c._activations = [a for a in self._activations]
        
        # Except for the latest activation 
        if c._activations:
            c._activations[-1] = c._activations[-1].copy()
        
        c.multsqueezes = self.multsqueezes
        
        c.score_base = self.score_base
        c.score_combo = self.score_combo
        c.score_sp = self.score_sp
        c.score_solo = self.score_solo
        c.score_accents = self.score_accents
        c.score_ghosts = self.score_ghosts
        
        c.notecount = self.notecount
        
        c.leftover_sp = self.leftover_sp
        c.skipped_ghosts = self.skipped_ghosts
        c.skipped_accents = self.skipped_accents
        
        c.variants = [v.copy() for v in self.variants]
        c.var_point = self.var_point
        
        return c
        
    def difficulty(self):
        d_gen = (act.difficulty() for act in self.all_activations())
        diffs = [d for d in d_gen if d is not None]
        
        return max(diffs) if diffs else None
        
    def is_difficult(self):
        return any(act.is_difficult() for act in self.all_activations())
    
    def passes_ms_filter(self, ms_filter):
        return (d := self.difficulty()) is None or d < ms_filter

class Activation:
    
    def __init__(self):
        self.skips = None
        self.timecode = None
        self.chord = None
        self.sp_meter = None
        
        self.frontend_points = None
        self.backends = []
        
        self.sqinouts = []
        
        self.e_offset = None
    
    def __eq__(self, other):
        for listattr in ['backends', 'sqinouts']:
            a = getattr(self, listattr)
            b = getattr(other, listattr)
            if len(a) != len(b):
                return False
            for i in range(len(a)):
                if a[i] != b[i]:
                    return False
        
        for attr in ['skips', 'timecode', 'chord', 'sp_meter', 'frontend', 'e_offset']:
            if getattr(self, attr) != getattr(other, attr):
                return False
                
        return True
    
    def __str__(self):
        return self.notationstr()
    
    def notationstr(self):
        e = 'E' if self.is_e_critical() else ''
        return f"{e}{self.skips}{''.join(sq.symbol for sq in self.sqinouts)}"
        
    def notationstr_verbose(self):
        ms = f" ({int(self.difficulty())} ms)" if self.difficulty() is not None else ""
        return f"{self.notationstr()}{ms}"
    
    def is_e_critical(self):
        return self.e_offset < 70
        
    def is_E0(self):
        return self.is_e_critical() and self.skips == 0
        
    def copy(self):
        c = Activation()
        
        c.skips = self.skips
        c.timecode = self.timecode
        c.chord = self.chord
        c.sp_meter = self.sp_meter
        
        c.frontend_points = self.frontend_points
        c.backends = self.backends
        
        c.sqinouts = [s for s in self.sqinouts]
        
        c.e_offset = self.e_offset
        
        return c

    def e_difficulty(self):
        if self.is_E0():
            return -self.e_offset + 0.0
        return None
        
    def difficulty(self):
        diffs = [sq.difficulty for sq in self.sqinouts]
        if (e_diff := self.e_difficulty()) is not None:
            diffs.append(e_diff)
        return max(diffs) if diffs else None

    def is_difficult(self):
        if (e_diff := self.e_difficulty()) is not None and e_diff > 2.0:
            return True
        
        return any(sq.is_difficult for sq in self.sqinouts)

class MultSqueeze:
    """Multiplier squeeze: When the combo multiplier goes up partway through a
    chord, and that chord has notes with different values, the higher-value
    notes should be hit on the higher combo multiplier.
    
    This usually results in +15s for cymbal squeezes or +50s for dynamic
    squeezes.
    """
    def __init__(self, chord, combo):
        """Raises ValueError if the given chord + combo is not a situation
        where a multiplier squeeze is possible."""
        self.chord = chord
        self.combo = combo

        self._validate()

    def _validate(self):
        if self.combo not in [7, 8, 17, 18, 27, 28]:
            raise ValueError(f"Invalid MultSqueeze combo: {self.combo}")
        
        if (self.chord.count() + self.combo) % 10 not in [0, 1]:
            raise ValueError(f"Invalid MultSqueeze chord length {self.chord.count()} at combo={self.combo}")
        
        notes = self.chord.notes()
        if all(n.basescore() == notes[0].basescore() for n in notes):
            raise ValueError(f"MultSqueeze chord has no squeezable note values: {self.chord}")
    
    @property
    def multiplier(self):
        return hymisc.to_multiplier(self.combo) + 1
    
    @property
    def direction(self):
        """Depending on combo, mult squeezes are either best described as
        "hit X note first" or "hit X note last", i.e. focusing on a single 
        note.
        """
        if self.combo % 10 == 7:
            # One note is high
            return 'high'
        else:
            # One note is low
            return 'low'
    
    @property
    def points(self):
        noteorder = self.chord.notes(basesorted=True)
            
        return noteorder[-1].basescore() - noteorder[0].basescore()
    
    def __eq__(self, other):
        return self.chord == other.chord and self.combo == other.combo
    
    def notationstr(self):
        return f"{self.multiplier}x"

    @property
    def guide_chords(self):
        """Every pair of chords that add up to this squeeze's chord,
        where hitting the chords separately in that order results in executing
        the squeeze.
        
        For 2-note chords the guide chords are simply one note then the other.
        For 3-note chords the guide chords depend on note values and there may
        be two options.
        """
        notes = self.chord.notes(basesorted=True)
        if self.direction == 'high':
            edge_score = notes[-1].basescore() 
        else:
            edge_score = notes[0].basescore()
        edge_options = (note for note in notes if note.basescore() == edge_score)
        pairs = []
        for chosen_edge in edge_options:
            edge = Chord()
            edge[chosen_edge.colortype] = chosen_edge
            
            nonedge = Chord()
            for note in notes:
                if note != chosen_edge:
                    nonedge[note.colortype] = note
                
            if self.direction == 'high':
                pairs.append((nonedge, edge))
            else:
                pairs.append((edge, nonedge))
        
        return pairs

    @property
    def howto(self):
        i = 1 if self.direction == 'high' else 0
        when = "last" if self.direction == 'high' else "first"
        
        return f"Hit {' or '.join(c[i].rowstr() for c in self.guide_chords)} {when}."


class FrontendSqueeze:
    
    def __init__(self, chord, points):
        self.chord = chord
        self.points = points
        
    def __eq__(self, other):
        for attr in ['chord', 'points']:
            if getattr(self, attr) != getattr(other, attr):
                return False
                
        return True
        


class SPSqueeze(ABC):
    """Star Power squeeze, i.e. a SqIn (+) or SqOut (-).
    
    This is mainly a container for the squeeze's notation and the
    different ways to interpret its millisecond value.
    
    """
    def __init__(self, offset_ms):
        self._offset_ms = offset_ms
    
    def __eq__(self, other):
        return self.offset == other.offset
    
    @property
    def offset(self):
        """Offset from the end of SP to the note, in milliseconds.
        
        Negative offsets are before the end of SP and easy to SqIn.
        Positive offsets are after the end of SP and easy to SqOut.
        """
        return self._offset_ms

    @property
    def timing(self):
        """The timing threshold for the note, equal to -offset.
        
        Hitting earlier than this timing results in a SqIn,
        hitting later results in a SqOut.
        """
        return -self.offset + 0.0
        
    @property
    @abstractmethod
    def difficulty(self):
        """The millisecond value, with sign flipped to ensure that larger
        values mean the squeeze is harder to pull off.
        
        Positive values mean the note's timing has to be pushed that far
        early/late to get the squeeze.
        
        Negative values mean the note's timing would have to be that far
        in the wrong direction to miss the squeeze.
        """
        pass
        
    @property
    @abstractmethod
    def symbol(self):
        """The symbol for this squeeze."""
        pass
        
    @property
    @abstractmethod
    def description(self):
        pass
        
    @property
    def is_difficult(self):
        return self.difficulty > 2.0
    
class SqIn(SPSqueeze):
    @property
    def difficulty(self):
        return self.offset
    
    @property
    def symbol(self):
        return '+'
        
    @property
    def description(self):
        return f"SqIn: Note timing must be earlier than {self.timing:.1f}ms."
    
class SqOut(SPSqueeze):
    @property
    def difficulty(self):
        return -self.offset + 0.0
        
    @property
    def symbol(self):
        return '-'
        
    @property
    def description(self):
        return f"SqOut: Note timing must be later than {self.timing:.1f}ms."
    

class BackendSqueeze:
    def __init__(self, timecode, chord, points, sqout_points, is_sp):
        self.timecode = timecode
        self.chord = chord
        self.points = points
        self.sqout_points = sqout_points
        self.is_sp = is_sp

        self.offset_ms = None
        
    def __eq__(self, other):
        for attr in ['timecode', 'chord', 'points', 'sqout_points', 'is_sp', 'offset_ms']:
            if getattr(self, attr) != getattr(other, attr):
                return False
                
        return True
    
    def summarystr(self):
        if self.is_sp:
            if self.offset_ms < -70:
                return "Insane SqOut"
            elif self.offset_ms < -10:
                return "Hard SqOut"
            elif self.offset_ms < 10:
                return "Standard SqOut"
            elif self.offset_ms < 70:
                return "Easy SqOut"
            else:
                return "Free SqOut"
        else:
            if self.offset_ms < -70:
                return "Free"
            elif self.offset_ms < -10:
                return "Easy"
            elif self.offset_ms < 3:
                return "Standard"
            elif self.offset_ms < 70:
                return "Hard (uncounted)"
            else:
                return "Insane (uncounted)"
    
    def ratingstr(self):
        """Hydra ratings for how hard the squeeze's timing is."""
        thresholds = [
            (-140, "Free"),
            (-105, "Free"),
            (-70, "Free"),
            (-35, "Trivial"),
            (-2, "Easy"),
            (2, "Normal"),
            (35, "Hard"),
            (70, "Extreme"),
            (105, "Insane"),
            (140, "Insane+"),
        ]
        max_rating = "Impossible"
        
        for threshold, rating in thresholds:
            if self.offset_ms < threshold:
                return rating
        
        return max_rating


class NoteColor(Enum):
    """Representation of a note color.
    
    Note colors actually determine what types of notes are possible.
    Kick notes only have normal notes and the special 2x kick note.
    Red notes don't have cymbals.
    
    """
    KICK = 1
    RED = 2
    YELLOW = 3
    BLUE = 4
    GREEN = 5
    
    def allows_cymbals(self):
        return self in [
            NoteColor.YELLOW,
            NoteColor.BLUE,
            NoteColor.GREEN
        ]
            
    
    def allows_dynamics(self):
        return self in [
            NoteColor.RED,
            NoteColor.YELLOW,
            NoteColor.BLUE,
            NoteColor.GREEN
        ]
    
    def __str__(self):
        match self:
            case NoteColor.KICK:
                return "Kick"
            case NoteColor.RED:
                return "Red"
            case NoteColor.YELLOW:
                return "Yellow"
            case NoteColor.BLUE:
                return "Blue"
            case NoteColor.GREEN:
                return "Green"
    
    def notationstr(self):
        match self:
            case NoteColor.KICK:
                return "K"
            case NoteColor.RED:
                return "R"
            case NoteColor.YELLOW:
                return "Y"
            case NoteColor.BLUE:
                return "B"
            case NoteColor.GREEN:
                return "G"


class NoteDynamicType(Enum):
    """Representation of a note's dynamic type."""
    NORMAL = 1
    GHOST = 2
    ACCENT = 3


class NoteCymbalType(Enum):
    """Representation of a note's dynamic type.
    
    Normal = Toms / Snare / Kick.
    
    """
    NORMAL = 1
    CYMBAL = 2

    def flip(self):
        if self == NoteCymbalType.CYMBAL:
            return NoteCymbalType.NORMAL
        else:
            return NoteCymbalType.CYMBAL

class ChordNote:
    """Representation of a note from a chart."""

    def __init__(
        self,
        colortype, 
        dynamictype=NoteDynamicType.NORMAL, 
        cymbaltype=NoteCymbalType.NORMAL, 
        is2x=False
    ):
        assert(colortype is not None)
        self.colortype = colortype
        self.dynamictype = dynamictype
        self.cymbaltype = cymbaltype
        self.is2x = is2x
    
    def __hash__(self):
        return 1000 * self.colortype.value + 100 * self.dynamictype.value + 10 * self.cymbaltype.value + (1 if self.is2x else 0)
    
    def __eq__(self, other):
        if other is None:
            return False
                
        for attr in ['colortype', 'dynamictype', 'cymbaltype', 'is2x']:
            if getattr(self, attr) != getattr(other, attr):
                return False
                
        return True
    
    def __str__(self):
        if self.colortype.allows_cymbals():
            cym = "Cym" if self.cymbaltype == NoteCymbalType.CYMBAL else "Tom"
        else:
            cym = ""
            
        if self.colortype.allows_dynamics():
            match self.dynamictype:
                case NoteDynamicType.NORMAL:
                    mod = ""
                case NoteDynamicType.GHOST:
                    mod = " (Ghost)"
                case NoteDynamicType.ACCENT:
                    mod = " (Accent)"
        elif self.is2x:
            mod = " (2x)"
        else:
            mod = ""
            
        return f"{self.colortype}{cym}{mod}"
    
    def basescore(self):
        points = 65 if self.is_cymbal() else 50

        if self.is_dynamic():
            points *= 2
        
        return points
    
    def is_dynamic(self):
        return self.dynamictype != NoteDynamicType.NORMAL
    
    def is_accent(self):
        return self.dynamictype == NoteDynamicType.ACCENT
    
    def is_ghost(self):
        return self.dynamictype == NoteDynamicType.GHOST
    
    def is_cymbal(self):
        return self.cymbaltype == NoteCymbalType.CYMBAL


class Chord:
    """Representation of a chord which has 1 note (or None) for each color."""
    
    def __init__(self):
        self.notemap = {
            NoteColor.KICK: None,
            NoteColor.RED: None,
            NoteColor.YELLOW: None,
            NoteColor.BLUE: None,
            NoteColor.GREEN: None
        }
    
    def __hash__(self):
        h = [-1, -1, -1, -1, -1]
        for i, note in enumerate(self.notemap.values()):
            if note is not None:
                h[i] = hash(note)
        return hash(tuple(h))
    
    @staticmethod
    def from_code(code):
        notes_raw = hyencode.CHORD_DECODE[code]
        
        chord = Chord()
        for notefields in notes_raw:
            note = ChordNote(
                NoteColor(notefields['color']), 
                dynamictype=NoteDynamicType(notefields['dyn']), 
                cymbaltype=NoteCymbalType(notefields['cym']), 
                is2x=notefields['2x']
            )
            
            chord[note.colortype] = note
        
        return chord
        
    def code(self):
        return hyencode.CHORD_ENCODE[hash(self)]
        
    def __repr__(self):
        return self.rowstr()
        
    def __eq__(self, other):
        for color in self.notemap.keys():
            if self[color] != other[color]:
                return False
        return True
                
    def __getitem__(self, c, objtype=None):
        return self.notemap[c]
    
    def __setitem__(self, c, value):
        self.notemap[c] = value
    
    def notes(self, basesorted=False):
        """Gets the notes that aren't empty."""
        notelist = [n for n in self.notemap.values() if n is not None]
        if basesorted:
            notelist.sort(key=lambda n: n.basescore())
        return notelist
    
    def count(self):
        return len(self.notes())
    
    def ghost_count(self):
        return len([n for n in self.notes() if n.is_ghost()])
    
    def accent_count(self):
        return len([n for n in self.notes() if n.is_accent()])
    
    def rowstr(self):
        return f"[{" - ".join([str(n) for n in self.notes()])}]"
    
    def notationstr(self):
        krybg = "["
        for color, note in self.notemap.items():
            krybg += color.notationstr() if note else ' '
        return krybg + "]"
    
    def apply_disco_flip(self):
        """Utility to edit notes based on a disco flip flag."""
        red = self[NoteColor.RED]
        yellow = self[NoteColor.YELLOW]
        
        if red:
            # Red -> Yellow cymbal
            red.cymbaltype = NoteCymbalType.CYMBAL
            red.colortype = NoteColor.YELLOW
        if yellow:
            # Yellow -> Red
            yellow.cymbaltype = NoteCymbalType.NORMAL
            yellow.colortype = NoteColor.RED
        
        # Color swap
        self[NoteColor.RED] = yellow
        self[NoteColor.YELLOW] = red
    
    def add_note(self, color):
        if self[color] is not None:
            raise hymisc.ChartFileError("Duplicate note.")
        note = ChordNote(color)
        self[color] = note
        return note
    
    def add_2x(self):
        self.add_note(NoteColor.KICK)
        self[NoteColor.KICK].is2x = True
    
    def apply_cymbal(self, color):
        assert(self[color] is not None)
        self[color].cymbaltype = NoteCymbalType.CYMBAL
    
    def apply_ghost(self, color):
        assert(self[color] is not None)
        self[color].dynamictype = NoteDynamicType.GHOST
    
    def apply_accent(self, color):
        assert(self[color] is not None)
        self[color].dynamictype = NoteDynamicType.ACCENT

    def activation_note(self):
        for c in [
            NoteColor.GREEN,
            NoteColor.BLUE,
            NoteColor.YELLOW,
            NoteColor.RED,
            NoteColor.KICK,
        ]:
            if (note := self[c]) is not None:
                return note
        raise ValueError
