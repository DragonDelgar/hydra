import shutil
import copy
import math
import json
from enum import Enum
from itertools import combinations

from . import hydata
from . import hymisc


class ScoreGraph:
    """Description of a song in terms of pathing choices and outcomes.
    
    Consists of nodes representing timecodes for the song and edges
    representing either getting further in the song (advancing) or
    switching between inactive and active SP (branching).
    
    To that end, the nodes form two tracks: the normal track and SP
    track. There are only branch edges between the tracks where it's
    possible to activate (with a fill) or deactivate (run out of) SP.
    
    Edges store information about what is gained (mainly points and SP)
    from taking that edge.
    
    Advancing down a track gets further in the song and accrues points.
    Branching does not advance time, but possibly accrues features like
    backends which are specific to the act of toggling SP.
    
    Because "your current SP" isn't encoded on the graph, not every path
    through it is a valid path for the song. However, the graph contains
    all the info needed to go from start to finish while tracking sp, in
    order to explore valid paths through the song.
    
    """
    def __init__(self, song):
        # Finished state
        self.song = song
        self.start = ScoreGraphNode(song.start_time(), False)
        self.length = 0
        
        # Processing state
        self._head_time = None
        self._base_track_head = self.start
        self._sp_track_head = ScoreGraphNode(song.start_time(), True)
        self._combo = 0
        self._pending_deacts = set([])
        self._recent_deact_edges = []       # Used for SqIn backend detection (notes after deacts are usually Out, but recent deacts can make it a SqIn)
        self._recent_backends = []          # Used for SqOut detection (notes before deacts are usually In, but recent notes can be SqOut)
        self._proto_base_edge = ScoreGraphEdge()
        self._proto_sp_edge = ScoreGraphEdge()
        
        for timestamp in song._sequence:
            # SP can fall off between timestamps, so handle those first if any.
            for pending_deact in sorted(list(self._pending_deacts)):
                if pending_deact >= timestamp.timecode:
                    break
                self.set_head_time(pending_deact)
                self.handle_deact(pending_deact, None)
                    
            self.set_head_time(timestamp.timecode)
            
            self.store_notecount(timestamp.chord.count())
            if timestamp.flag_solo:
                self.store_soloscore(100 * timestamp.chord.count())
            
            score_groups = category_scores(timestamp.chord, self._combo)
            
            try:
                msq = hydata.MultSqueeze(timestamp.chord, self._combo)
                self.store_multsqueeze(msq)
            except ValueError:
                pass
            
            self.store_basescore(score_groups['base'])
            self.store_comboscore(score_groups['combo'])
            self.store_spscore(score_groups['sp'])
            self.store_accentscore(score_groups['accent'])
            self.store_ghostscore(score_groups['ghost'])
            
            self._combo += timestamp.chord.count()
            
            self.store_new_backend(timestamp, score_groups['sp'], score_groups['sp'] - score_groups['sqout_reduction'])
            
            if timestamp.flag_sp:
                # If any deacts are only the squeeze window away (140ms), keep a non-extended copy of them (SqOut)
                sqout_deacts = set([tc for tc in self._pending_deacts if tc.ms - timestamp.timecode.ms < 140])
                
                # Deact timecodes that can be extended by this sp: current pending deacts as well as very recently handled deacts (SqIn)
                extendable_tcs = self._pending_deacts.union(set([e.dest.timecode for e in self._recent_deact_edges]))
                
                # Deact timecodes after extension: end time + 2 measures or capped at now + 8 measures
                extension_map = {tc: min(tc.plusmeasure(2, song), timestamp.timecode.plusmeasure(8, song)) for tc in extendable_tcs}
                
                # Update deacts
                self._pending_deacts = set(extension_map.values()).union(sqout_deacts)
                
                # Save info on the graph
                self._proto_base_edge.sp_times.append((timestamp.timecode, extension_map))
                self._proto_sp_edge.sp_times.append((timestamp.timecode, extension_map))
                
            # handle acts            
            if timestamp.has_activation():
                self.advance_tracks(timestamp.timecode, timestamp.chord)
                self.add_act_edge(timestamp.chord, score_groups['sp'], score_groups['skipped_dynamic_reduction'], timestamp.activation_length, song)
                
                self._pending_deacts.add(timestamp.timecode.plusmeasure(4, song))
                self._pending_deacts.add(timestamp.timecode.plusmeasure(6, song))
                self._pending_deacts.add(timestamp.timecode.plusmeasure(8, song))
                
            # handle deacts
            if timestamp.timecode in self._pending_deacts:
                self.handle_deact(timestamp.timecode, timestamp.chord)
            
        self.advance_tracks(song.last.timecode, song.last.chord)
    
    def store_notecount(self, count):
        self._proto_base_edge.notecount += count
        self._proto_sp_edge.notecount += count
        
    def store_soloscore(self, points):
        self._proto_base_edge.soloscore += points
        self._proto_sp_edge.soloscore += points
        
    def store_basescore(self, points):
        self._proto_base_edge.basescore += points
        self._proto_sp_edge.basescore += points
        
    def store_comboscore(self, points):
        self._proto_base_edge.comboscore += points
        self._proto_sp_edge.comboscore += points
        
    def store_spscore(self, points):
        self._proto_sp_edge.spscore += points
        
    def store_accentscore(self, points):
        self._proto_base_edge.accentscore += points
        self._proto_sp_edge.accentscore += points
        
    def store_ghostscore(self, points):
        self._proto_base_edge.ghostscore += points
        self._proto_sp_edge.ghostscore += points
        
    def store_multsqueeze(self, msq):
        self._proto_base_edge.multsqueezes.append(msq)
        self._proto_sp_edge.multsqueezes.append(msq)
    
    def store_new_backend(self, timestamp, sp_points, sqout_points):
        """Create a backend and apply it to recent deact edges.
        These backends are late, i.e. they have positive offsets.
        """
        backend = hydata.BackendSqueeze(
            timestamp.timecode, timestamp.chord,
            sp_points, sqout_points,
            timestamp.flag_sp
        )
        
        self._recent_backends.append(backend)
        
        for recent_edge in self._recent_deact_edges:
            offset_ms = timestamp.timecode.ms - recent_edge.dest.timecode.ms
            recent_edge.backends.append(copy.copy(backend))
            recent_edge.backends[-1].offset_ms = offset_ms
            
            if recent_edge.backends[-1].is_sp and not recent_edge.sqinout_time:
                # SqIn timing is only relevant for the 1st sp backend encountered
                # If there are more than 1, it's probably a charting error, but ya know
                recent_edge.sqinout_time = timestamp.timecode
                recent_edge.sqinout_timing = offset_ms
                recent_edge.late_sqin_count += 1
                recent_edge.sqin_time = recent_edge.sqin_time.plusmeasure(2, self.song)
        
    def head_time_offset(self, timecode):
        return self._head_time.ms - timecode.ms
        
    def is_recent_to_head(self, timecode):
        return self.head_time_offset(timecode) < 140
        
    def set_head_time(self, timecode):
        """ Update head time and any mechanics based on being 'recent'"""
        self._head_time = timecode
        self._recent_deact_edges = [edge for edge in self._recent_deact_edges if self.is_recent_to_head(edge.dest.timecode)]
        self._recent_backends = [be for be in self._recent_backends if self.is_recent_to_head(be.timecode)]

    def handle_deact(self, deact_tc, chord):
        if deact_tc not in self._pending_deacts:
            return
        self.advance_tracks(deact_tc, chord)
        self.add_deact_edge()
        self._pending_deacts.remove(deact_tc)
    
    def advance_tracks(self, timecode, chord):
        if self._base_track_head.timecode >= timecode: 
            return
        
        self.length += 1
        
        self._proto_base_edge.dest = ScoreGraphNode(timecode, False)
        self._proto_sp_edge.dest = ScoreGraphNode(timecode, True)
        self._proto_base_edge.dest.chord = chord
        self._proto_sp_edge.dest.chord = chord
            
        self._base_track_head.adv_edge = self._proto_base_edge
        self._sp_track_head.adv_edge = self._proto_sp_edge
        
        self._proto_base_edge = ScoreGraphEdge()
        self._proto_sp_edge = ScoreGraphEdge()
        
        self._base_track_head = self._base_track_head.adv_edge.dest
        self._sp_track_head = self._sp_track_head.adv_edge.dest
    
    def add_act_edge(self, frontend_chord, frontend_points, skipped_dynamic_reduction, fill_length_ticks, song):
        act_edge = ScoreGraphEdge()
        act_edge.dest = self._sp_track_head
        
        act_edge.notecount = 0
        act_edge.basescore = 0
        act_edge.comboscore = 0
        act_edge.spscore = 0
        act_edge.soloscore = 0
        act_edge.accentscore = 0
        act_edge.ghostscore = 0
        
        act_edge.frontend = hydata.FrontendSqueeze(frontend_chord, frontend_points)
        
        # Set E
        fillend = act_edge.dest.timecode
        fillstart = hymisc.Timecode(fillend.ticks - fill_length_ticks, song.tick_resolution, song.tpm_changes, song.bpm_changes)
        
        padding = fill_length_ticks + song.tick_resolution/16
        fillstart_padded = hymisc.Timecode(fillend.ticks - padding, song.tick_resolution, song.tpm_changes, song.bpm_changes)
        
        fill_length_ms = fillend.ms - fillstart.ms
        raw_preroll_ms = fillend.ms - fillstart_padded.ms
        preroll_ms = max(250, min(raw_preroll_ms, 10000))        
        act_edge.activation_fill_deadline_ms = fillend.ms - fill_length_ms - preroll_ms
        
        act_edge.activation_initial_end_times = {sp: fillend.plusmeasure(2 * sp, song) for sp in [2, 3, 4]}
        
        act_edge.skipped_dynamic_points = skipped_dynamic_reduction
        
        self._base_track_head.branch_edge = act_edge
    
    def add_deact_edge(self):
        deact_edge = ScoreGraphEdge()
        deact_edge.dest = self._base_track_head
        
        deact_edge.notecount = 0
        deact_edge.basescore = 0
        deact_edge.comboscore = 0
        deact_edge.spscore = 0
        deact_edge.soloscore = 0
        deact_edge.accentscore = 0
        deact_edge.ghostscore = 0
        
        deact_edge.sqout_time = deact_edge.dest.timecode
        deact_edge.sqin_time = deact_edge.dest.timecode
        
        # notes just prior to this deactivation, which are normally in sp but could be squeezed out
        for recent_backend in self._recent_backends:
            deact_edge.backends.append(copy.copy(recent_backend))
            offset_ms = recent_backend.timecode.ms - deact_edge.dest.timecode.ms
            deact_edge.backends[-1].offset_ms = offset_ms
            
            if recent_backend.is_sp and not deact_edge.sqinout_time:
                deact_edge.sqinout_time = recent_backend.timecode
                deact_edge.sqinout_timing = offset_ms
                deact_edge.sqout_time = deact_edge.sqout_time.plusmeasure(2, self.song)
                deact_edge.sqin_time = deact_edge.sqin_time.plusmeasure(2, self.song)
                
        self._recent_deact_edges.append(deact_edge)
        self._sp_track_head.branch_edge = deact_edge


class ScoreGraphNode:
    """Represents a point in the song and whether SP is active or not.
    
    The only possible edges are 1 advancing edge leading farther into the song 
    and 1 branch node that does not move forward but toggles SP.
    """
    def __init__(self, timecode, is_sp):
        self.timecode = timecode

        self.adv_edge = None
        self.branch_edge = None
        self.is_sp = is_sp
        self.chord = None
    
    def __repr__(self):
        lines = [self.name()]
        if self.adv_edge:
            lines.append(self.adv_edge.__repr__())
        if self.branch_edge:
            lines.append(self.branch_edge.__repr__())
        
        return '\n'.join(lines)
    
    def name(self):
        return f"{self.timecode.measurestr()}{' SP' if self.is_sp else ''}"


class ScoreGraphEdge:
    """Represents a movement from one node in the graph to another.
    
    Edges store information so that when a path uses an edge, the path
    simply adds to itself whatever is stored on that edge.
    
    The three possible movements:
    - Advancing further into the song
    - Activating SP (branch)
    - Deactivating SP (branch)
    
    The graph is created such that every possible place where it's possible
    to activate or run out of SP has a branch edge there.
    
    """
    def __init__(self):
        self.dest = None
        
        self.notecount = 0
        
        self.basescore = 0
        self.comboscore = 0
        self.spscore = 0
        self.soloscore = 0
        self.accentscore = 0
        self.ghostscore = 0
        
        self.sp_times = []
        
        self.frontend = None
        self.backends = []
        
        self.multsqueezes = []
        
        # SP must become ready by this time in order for the fill to show.
        self.activation_fill_deadline_ms = None
        
        self.sqinout_time = None
        self.sqinout_timing = None
        
        self.late_sqin_count = 0
        self.sqout_time = None
        self.sqin_time = None
    
    def __repr__(self):
        return f" --> {self.dest.name()}, frontend = {self.frontend}"
        
    def deactivation_type(self, sp_end_time):
        """Which kind of deactivation is possible if this deact edge is reached
        by a GraphPath object with the given sp end time.
        
        This result is a function of the sp end time, the edge's time,
        the edge's early SP backends (already applied to the incoming sp end
        time), and the edge's late SP backends.
        
        'none': It's not possible to deactivate here.
        'normal': SP runs out here and the path is forced to deactivate.
        'sqinout': 
        """
        if self.sqinout_time:
            # This deact has SP on it, so if valid, the deact path will be a
            # SqOut and the continuing path will be a SqIn.
            if sp_end_time == self.sqout_time:
                # end time + early SP backends == edge time + early SP backends
                return 'sqinout'
            else:
                return 'none'
        else:
            # Normal backend, no sqin/sqouts
            assert(sp_end_time >= self.dest.timecode)
            if sp_end_time == self.dest.timecode:
                # SP ends here
                return 'normal'
            else:
                # SP ends later
                return 'none'


class GraphPather:
    """Responsible for creating multiple paths and for creating records.
    
    Reads ScoreGraphs; stores a record for the latest graph that was read.
    
    """
    def __init__(self):
        self.record = hydata.HydraRecord()
        
    def read(self, graph, depth_mode, depth_value, ms_filter, cb_pathsprogress=None):
        self.record.ms_limit = ms_filter
        paths = [GraphPath()]
        paths[0].currentnode = graph.start
        length = 0
        
        # to do: paths should complete at the same time, might improve performance
        while any([not p.is_complete() for p in paths]):
            new_paths = []
            for p in paths:
                assert(not p.is_complete())
                p.advance()
                    
                if p.is_complete():
                    new_paths.append(p)
                    continue
                
                if p.is_active_sp():
                    can_extend, branchpath = p.branch_deactivate()
                    if can_extend:
                        new_paths.append(p)
                else:
                    branchpath = p.branch_activate()
                    new_paths.append(p)
                    
                if branchpath:
                    new_paths.append(branchpath)
                
            # Update the path list with branching results
            paths = self.reduced_paths(new_paths, depth_mode, depth_value, ms_filter)
        
            length += 1
            if cb_pathsprogress:
                tc = paths[0].currentnode.timecode if paths[0].currentnode else None
                cb_pathsprogress(tc, length / graph.length)
        
        # Order the completed paths by score
        paths.sort(key=lambda p: p.data.totalscore(), reverse=True)
        
        # Finalize paths and copy from processing objects to hydata
        for path in paths:
            path.data.leftover_sp = path.sp
            path.data.prepare_variants()
            self.record._paths.append(path.data)    
    
    def reduced_paths(self, paths, depth_mode, depth_value, ms_filter):
        """Reduce the number of paths along the way by eliminating paths
        that are definitely not as good as another path.
        
        While partway through the song, sometimes paths aren't comparable
        because their SP situations are different, but a lot of the time they
        *are* comparable.
        
        Depth parameters allow extra paths to be held, to end up with the
        optimal path(s) plus some extra runner-up paths.
        
        depth_mode:
            'points': Keep paths within {depth_value} points of optimal.
            'scores': Keep paths for {depth_value} scores below optimal.
        
        ms_filter: Remove paths that have timing requirements more difficult
        than this millisecond value.
        """
        # Since all the paths are at the same point in the song, the only
        # thing that can make 2 paths not comparable is SP: SP represents
        # an unknown amount of points that has yet to be realized. If a path
        # has less points but more SP, it's unclear if the path is better or
        # worse at this time.
        # 
        # At the end of the song, all paths of course become comparable
        # by their final scores.
        #
        # Both Active SP: Only comparable if same sp value.
        # Both Inactive SP: Score and SP value comparisons must not contradict.
        # Different SP Active: Not comparable

        filtered_paths = set()
        paths_to_remove = set()
        
        if ms_filter is not None:
            for p in paths:
                if not p.data.passes_ms_filter(ms_filter):
                    filtered_paths.add(p)
        
        # Separate active SP and inactive SP paths
        # Reduces amount of obviously ineffective comparisons in a sec
        pathgroups = {
            True: [],
            False: []
        }
        for p in paths:
            # Don't consider paths that recently SqIn/SqOuted as they have
            # interacted with an SP phrase earlier than other paths.
            if p.buffered_sqinout_sp == 0 and p not in paths_to_remove:
                pathgroups[p.is_active_sp()].append(p)                
        
        worsethan_scores = {p: set() for p in paths}
        
        for p, q in combinations(pathgroups[True], 2):
            # Active SP paths: Compare score only if SP is the same
            if p.sp_end_time != q.sp_end_time:
                continue
               
            score_diff = q.data.totalscore() - p.data.totalscore()
            if score_diff < 0:
                better, worse = (p, q)
            elif score_diff > 0:
                better, worse = (q, p)
            else:
                continue
                
            if worse in filtered_paths:
                paths_to_remove.add(worse)
                continue
                
            if depth_mode == 'points':
                if better not in filtered_paths and worse.data.totalscore() + depth_value < better.data.totalscore():
                    paths_to_remove.add(worse)
            elif depth_mode == 'scores':
                if better not in filtered_paths:
                    worsethan_scores[worse].add(better.data.totalscore())
                    if len(worsethan_scores[worse]) > depth_value:
                        paths_to_remove.add(worse)
            
        marked_variants = set()
        for p, q in combinations(pathgroups[False], 2):
            # Inactive SP paths: Compare both SP meter and score.
            # A path must be either better in both or better in one and 
            # tied in the other
            if p in marked_variants or q in marked_variants:
                continue
            
            cmp = 0
            p_sp = 0 if p.is_complete() else p.sp
            q_sp = 0 if q.is_complete() else q.sp
            
            sp_diff = q_sp - p_sp
            if sp_diff > 0:
                cmp += 1
            elif sp_diff < 0:
                cmp -= 1
            
            score_diff = q.data.totalscore() - p.data.totalscore()
            if score_diff > 0:
                cmp += 1
            elif score_diff < 0:
                cmp -= 1
            
            if sp_diff == score_diff == 0:
                # The two paths have converged at this point and any further
                # pathing will affect them identically
                if (p in filtered_paths) == (q in filtered_paths):
                    # Variants - p will continue analysis and q will become a variant
                    p.data.variants.append(q.data)
                    q.data.var_point = len(p.data)
                    marked_variants.add(q)
                    paths_to_remove.add(q)                
            
            if cmp < 0:
                better, worse = (p, q)
            elif cmp > 0:
                better, worse = (q, p)
            else:
                continue
                
            if worse in filtered_paths:
                paths_to_remove.add(worse)
                continue
                
            if depth_mode == 'points':
                if better not in filtered_paths and worse.data.totalscore() + depth_value < better.data.totalscore():
                    paths_to_remove.add(worse)   
            elif depth_mode == 'scores':
                if better not in filtered_paths:
                    worsethan_scores[worse].add(better.data.totalscore())
                    if len(worsethan_scores[worse]) > depth_value:
                        paths_to_remove.add(worse)
            
        return [p for p in paths if p not in paths_to_remove]
        
class GraphPath:
    """Quick early note:
    
    This class should do as little work as possible as it navigates the
    score graph. Any time that a GraphPath is *building* something, move
    it to ScoreGraph if at all possible.
    
    """
    def __init__(self, parent_path=None):
        if parent_path:
            self.data = parent_path.data.copy()
            
            self.currentnode = parent_path.currentnode
            self.sp = parent_path.sp
            self.currentskips = parent_path.currentskips
            self.buffered_sqinout_sp = parent_path.buffered_sqinout_sp
            self.sp_end_time = parent_path.sp_end_time
            self.sp_ready_time = parent_path.sp_ready_time
            self.skipped_e_offset = parent_path.skipped_e_offset
        else:
            self.data = hydata.Path()
            
            self.currentnode = None
            self.sp = 0
            self.currentskips = 0
            self.buffered_sqinout_sp = 0 # sp that was handled during a recent sqin/sqout, and needs to not be double counted
            self.sp_end_time = None
            self.sp_ready_time = None
            self.skipped_e_offset = None
    
    # Develop along the edge that leads farther into the song.
    # Always moves a path closer to being complete, unless it's already complete.
    def advance(self):
        #print("Path advancing:")
        
        if self.is_complete():
            #print("\tOops, I was already done.")
            return
        
        adv_edge = self.currentnode.adv_edge
        if adv_edge:
            self.data.score_base += adv_edge.basescore
            self.data.score_combo += adv_edge.comboscore
            self.data.score_sp += adv_edge.spscore
            self.data.score_solo += adv_edge.soloscore
            self.data.score_accents += adv_edge.accentscore
            self.data.score_ghosts += adv_edge.ghostscore
            
            self.data.notecount += adv_edge.notecount
            
            #print(f"\tGoing to {adv_edge.dest.timecode.measurestr()}.")
            # Applying SP on this edge
            if self.currentnode.is_sp:
                # Path is in SP: Immediately "spend" SP bars and adjust the sp end time
                #print(f"\tSP: {self.sp} + {len(adv_edge.sp_times)} = {min(max(0, self.sp + len(adv_edge.sp_times)), 4)}.")
                
                # Handling each sp individually since SP capping is based on each one's particular time
                # To do: Find a way to store the plusmeasures on the graph
                # The sp_times can be a tuple with the sp time and the sp time + 8 measures
                # The sp extension is actually the same as the pending_deact extensions in ScoreGraph so let's use those
                for sptc, extension_map in adv_edge.sp_times:
                    if self.buffered_sqinout_sp > 0:
                        self.buffered_sqinout_sp -= 1
                    else:
                        self.sp_end_time = extension_map[self.sp_end_time]
                
            else:
                # Path isn't in SP: Add SP bars
                old_sp = self.sp
                self.sp = min(self.sp + len(adv_edge.sp_times) - self.buffered_sqinout_sp, 4)

                if old_sp < 2 and self.sp >= 2:
                    self.sp_ready_time = adv_edge.sp_times[1 - old_sp + self.buffered_sqinout_sp][0]
                    
                self.buffered_sqinout_sp = 0
 
            self.data.multsqueezes += adv_edge.multsqueezes
                        
            self.currentnode = adv_edge.dest
                    
            
        else:
            #print("\tReached the end actually, achieving enlightenment.")
            self.currentnode = None
   
    def branch_activate(self):
        """If valid, create a new path that is a clone of this path
        except that it has used the current branch edge on the graph
        to go from inactive to active sp.
        """
        assert(not self.is_complete())
        if not (br_edge := self.currentnode.branch_edge):
            return None
            
        # Must have enough SP
        if self.sp < 2:
            return None
            
        # sp ready time must be before this activation fill's deadline
        e_offset = br_edge.activation_fill_deadline_ms - self.sp_ready_time.ms
        
        # Thanks to the timing window, the cutoff is -70ms not 0ms
        if e_offset < -70:
            return None
                    
        new_path = GraphPath(parent_path=self)
        new_path.currentnode = br_edge.dest
        new_path.currentskips = 0
        
        # Activated paths immediately "spend" the sp and just know what time the sp ends.
        new_path.sp = 0
        
        new_act = hydata.Activation()
        new_act.skips = self.currentskips
        new_act.timecode = self.currentnode.timecode
        new_act.chord = self.currentnode.chord
        new_act.sp_meter = self.sp
        new_act.frontend_points = br_edge.frontend.points
        new_act.e_offset = self.skipped_e_offset if self.skipped_e_offset is not None else e_offset
        
        new_path.data._activations.append(new_act)
        new_path.data.score_sp += br_edge.frontend.points
        new_path.skipped_e_offset = None
        new_path.sp_ready_time = None
        new_path.sp_end_time = br_edge.activation_initial_end_times[self.sp]
        
        self.currentskips += 1
        
        if hymisc.FLAG_SKIPPED_DYNAMICS:
            if br_edge.frontend.chord.activation_note().is_accent():
                self.data.score_accents -= br_edge.skipped_dynamic_points
                self.data.skipped_accents += 1
                
            if br_edge.frontend.chord.activation_note().is_ghost():
                self.data.score_ghosts -= br_edge.skipped_dynamic_points
                self.data.skipped_ghosts += 1
            
        # Even if the E fill is skipped, the eventual activation should know about it
        if self.skipped_e_offset is None:
            self.skipped_e_offset = e_offset
    
        return new_path
        
    def create_deactivated_path(self, is_sq_out):
        new_path = GraphPath(parent_path=self)
        new_path.currentnode = self.currentnode.branch_edge.dest
        new_path.sp = 1 if is_sq_out else 0
        
        new_path.sp_end_time = None
        
        new_path.data._activations[-1].backends = self.currentnode.branch_edge.backends
        
        if is_sq_out:
            new_path.data._activations[-1].sqinouts.append(hydata.SqOut(self.currentnode.branch_edge.sqinout_timing))
        
        # Backend scoring adjustments.
        for be in self.currentnode.branch_edge.backends:
            is_already_counted = be.offset_ms <= 0
            is_leeway = be.offset_ms > 0 and be.offset_ms < 3
            
            if is_sq_out:
                is_before_sqout = be.timecode < self.currentnode.branch_edge.sqinout_time
                is_exact_sqout = be.timecode == self.currentnode.branch_edge.sqinout_time
                is_after_sqout = be.timecode > self.currentnode.branch_edge.sqinout_time
                
                if is_already_counted:
                    if is_exact_sqout:
                        # Replace already-counted SP points with reduced sqout points.
                        new_path.data.score_sp += -be.points + be.sqout_points
                    elif is_after_sqout:
                        # Remove aready-counted SP points, since in this path
                        # this backend was forced out of SP even though it's early.
                        new_path.data.score_sp += -be.points
                elif is_leeway:
                    if is_before_sqout:
                        # Leeway squeeze (counted even though it's late).
                        new_path.data.score_sp += be.points
                    elif is_exact_sqout:
                        # Leeway squeeze, but with the reduced sqout points.
                        new_path.data.score_sp += be.sqout_points
            else:
                if is_leeway:
                    # Leeway squeeze (counted even though it's late)
                    new_path.data.score_sp += be.points
        
        return new_path
        
    def branch_deactivate(self):
        """If valid, create a new path that is a clone of this path
        except that it has used the current branch edge on the graph
        to go from active to inactive sp.
        
        Also returns whether the path can be extended OR deactivated,
        which is not usually the case but can happen with sp phrase squeezes.
        """
        if not (br_edge := self.currentnode.branch_edge):
            return True, None
        
        deact_type = br_edge.deactivation_type(self.sp_end_time)
        match deact_type:
            case 'none':
                return True, None
            case 'normal':
                normal_deact = self.create_deactivated_path(False)
                return False, normal_deact
            case 'sqinout':
                sqout_deact = self.create_deactivated_path(True)
                self.data._activations[-1].sqinouts.append(hydata.SqIn(br_edge.sqinout_timing))
                self.sp_end_time = br_edge.sqin_time
                # Avoid double-counting this SP when the path advances.
                self.buffered_sqinout_sp = br_edge.late_sqin_count
                sqout_deact.buffered_sqinout_sp = br_edge.late_sqin_count
                return True, sqout_deact
            case _:
                raise Exception(f"Unexpected deactivation type: {deact_type}")
    
    def is_complete(self):
        return self.currentnode == None
    
    def is_active_sp(self):
        if self.is_complete():
            return False
        return self.currentnode.is_sp


def category_scores(chord, combo):
    """Calculates the score for hitting this chord with the current combo.
    
    Builds a complete score breakdown for base score, SP, combo, cymbals, and
    dynamics, then returns the combinations that Clone Hero uses.
    
    Some mechanics can result in a lower score for the chord.
    For sanity reasons these lower scores don't have their own complete
    score breakdowns, but for multiplier squeezes the point difference is just
    nice to know, its breakdown is not as important; and for SqOuts the points
    are all SP points despite the lack of complete detail.
    
    Some mechanics (multiplier squeezes and SP squeezes) can overlap in a way
    that makes the optimal strategy more complicated. This is super rare, so
    for now we're ignoring this possibility.
    
    """
    # Full optimal score is the sum of these values.
    # Every possible cross-multiplication of the score multipliers.*
    # *Technically every dynamic category could be split into accent/ghost,
    # but let's not get too crazy
    points_by_source = {
        'base_note': 0,             'base_cymbal': 0,
        'combo_note': 0,            'combo_cymbal': 0,
        'sp_note': 0,               'sp_cymbal': 0,
        'combosp_note': 0,          'combosp_cymbal': 0,
        'dynamic_note_accent': 0,   'dynamic_cymbal': 0,
        'dynamic_note_ghost': 0,
        'combodynamic_note': 0,     'combodynamic_cymbal': 0,
        'spdynamic_note': 0,        'spdynamic_cymbal': 0,
        'combospdynamic_note': 0,   'combospdynamic_cymbal': 0,
    }
    
    # How many points to subtract if this chord is a SqOut
    sqout_reduction = 0
    
    # How many points to subtract if this chord is an activation chord
    # that gets skipped (the activation note cannot get its dynamic points)
    skipped_dynamic_reduction = 0
    
    ordering = chord.notes(basesorted=True)
    initial_combo_mult = hymisc.to_multiplier(combo)
    
    for i,note in enumerate(ordering):
        combo += 1
        combo_multiplier = hymisc.to_multiplier(combo)
        
        basevalue = 50
        cymbvalue = 15

        points_by_source['base_note'] += basevalue
        points_by_source['base_cymbal'] += cymbvalue if note.is_cymbal() else 0
        points_by_source['combo_note'] += basevalue * (combo_multiplier - 1)
        points_by_source['combo_cymbal'] += cymbvalue * (combo_multiplier - 1) if note.is_cymbal() else 0
        points_by_source['sp_note'] += basevalue
        points_by_source['sp_cymbal'] += cymbvalue if note.is_cymbal() else 0
        points_by_source['combosp_note'] += basevalue * (combo_multiplier - 1)
        points_by_source['combosp_cymbal'] += cymbvalue * (combo_multiplier - 1) if note.is_cymbal() else 0
        points_by_source['dynamic_note_accent'] += basevalue if note.is_accent() else 0
        points_by_source['dynamic_note_ghost'] += basevalue if note.is_ghost() else 0
        points_by_source['dynamic_cymbal'] += cymbvalue if note.is_cymbal() and note.is_dynamic() else 0
        points_by_source['combodynamic_note'] += basevalue * (combo_multiplier - 1) if note.is_dynamic() else 0
        points_by_source['combodynamic_cymbal'] += cymbvalue * (combo_multiplier - 1) if note.is_cymbal() and note.is_dynamic() else 0
        points_by_source['spdynamic_note'] += basevalue if note.is_dynamic() else 0
        points_by_source['spdynamic_cymbal'] += cymbvalue if note.is_cymbal() and note.is_dynamic() else 0
        points_by_source['combospdynamic_note'] += basevalue * (combo_multiplier - 1) if note.is_dynamic() else 0
        points_by_source['combospdynamic_cymbal'] += cymbvalue * (combo_multiplier - 1) if note.is_cymbal() and note.is_dynamic() else 0
        
        # Quick and dirty SqOut calculation
        if i == 0:
            sqout_reduction = (basevalue + (cymbvalue if note.is_cymbal() else 0)) * combo_multiplier * (2 if note.is_dynamic() else 1)
        
        if hymisc.FLAG_SKIPPED_DYNAMICS:
            if note == chord.activation_note() and note.is_dynamic():
                skipped_dynamic_reduction = (                
                    basevalue
                    + (cymbvalue if note.is_cymbal() else 0)
                    + basevalue * (combo_multiplier - 1)
                    + (cymbvalue * (combo_multiplier - 1) if note.is_cymbal() else 0)
                )
        
    return {
        'base': points_by_source['base_note'] + points_by_source['base_cymbal'] + points_by_source['dynamic_cymbal'],    
        'combo': points_by_source['combo_note'] + points_by_source['combo_cymbal'] + points_by_source['combodynamic_note'] + points_by_source['combodynamic_cymbal'],
        'sp': points_by_source['sp_note'] + points_by_source['sp_cymbal'] + points_by_source['combosp_note'] + points_by_source['combosp_cymbal'] + points_by_source['spdynamic_note'] + points_by_source['spdynamic_cymbal'] + points_by_source['combospdynamic_note'] + points_by_source['combospdynamic_cymbal'],
        'accent': points_by_source['dynamic_note_accent'],
        'ghost': points_by_source['dynamic_note_ghost'],
        'sqout_reduction': sqout_reduction,
        'skipped_dynamic_reduction': skipped_dynamic_reduction
    }
    
