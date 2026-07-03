import math
import time

class ScoreboardStateMachine:
    """
    The executive director of the display. Tracks absolute clock boundaries to sequence:
    Tournament Log Received -> Marquee Scroll -> Intermission Dice Spill -> Countdown Pulse -> Reset.
    """
    def __init__(self, renderer):
        self.renderer = renderer
        
        # Operational States: "MARQUEE", "INTERMISSION_IDLE", "COUNTDOWN", "IDLE"
        self.state = "MARQUEE"
        
        # Global frame tick accumulator for animation math
        self.frame_count = 0
        self.intermission_frame_count = 0
        
        # Chronological dynamic interval tracking structures
        self.last_blast_timestamp = None
        self.historical_intervals = [60.0, 60.0, 60.0]  # Seed with three 60-second default markers
        self.target_delay = 60.0                         # Extrapolated rolling average calculation
        
        self.blast_timestamp = time.time()
        self.countdown_end_timestamp = time.time()
        
        # Marquee typography configurations (No leading pipe to avoid letter 'I' confusion)
        self.marquee_text = "LIAR'S DICE TOURNAMENT - CONNECTED AND WAITING FOR LOGS..."
        self.marquee_x = 30 
        self.is_real_match_data = False

    def set_leaderboard_text(self, standings_list):
        """Compiles raw ranking data, rounding scores to the nearest tenth."""
        if not standings_list:
            return
        
        fragments = []
        for i, entry in enumerate(standings_list[:3]):
            rank_suffix = ["st", "nd", "rd"][i] if i < 3 else "th"
            score_float = float(entry.get('score', 0.0))
            fragments.append(f"{i+1}{rank_suffix}: {entry.get('name', 'UNKNOWN')} ({score_float:.1f}pts)")
            
        # Clean string layout without any ambiguous leading/trailing structural bars
        self.marquee_text = "STANDINGS: " + " * ".join(fragments) + "   "

    def handle_tournament_completion(self, log_data):
        """
        Intercepts incoming server data blasts. Dynamically tracks loop intervals
        and immediately interrupts the current phase state to force a timeline reset.
        """
        now = time.time()
        
        if self.last_blast_timestamp is not None:
            measured_interval = now - self.last_blast_timestamp
            
            # Defensive check: Ignore accidental duplicate data logs fired under 5 seconds
            if measured_interval > 5.0:
                self.historical_intervals.append(measured_interval)
                if len(self.historical_intervals) > 3:
                    self.historical_intervals.pop(0)
                
                self.target_delay = sum(self.historical_intervals) / len(self.historical_intervals)
                print(f"\n> Dynamic Interval Recalculated: {self.target_delay:.2f}s rolling average (Last run: {measured_interval:.2f}s)")

        self.last_blast_timestamp = now
        self.blast_timestamp = now
        
        bot_fullnames = log_data.get("bot_fullnames", [])
        scores = log_data.get("bot_scores", [])
        
        if bot_fullnames and scores:
            mock_standings = [{"name": name.split("_")[0], "score": score} for name, score in zip(bot_fullnames, scores)]
            mock_standings.sort(key=lambda x: x["score"], reverse=True)
            self.set_leaderboard_text(mock_standings)

        self.state = "MARQUEE"
        self.marquee_x = 30
        self.is_real_match_data = True

    def update(self):
        """Main ticking loop logic driven by absolute clock boundaries."""
        now = time.time()
        self.frame_count += 1

        # === STATE 1: SINGLE-SCROLL SCOREBOARD MARQUEE ===
        if self.state == "MARQUEE":
            self.marquee_x -= 1
            text_pixel_width = self.renderer.calculate_text_width(self.marquee_text)
            
            if self.marquee_x < -text_pixel_width:
                if self.is_real_match_data:
                    self.state = "INTERMISSION_IDLE"
                    self.intermission_frame_count = 0
                else:
                    self.state = "IDLE"
                    
            return self.renderer.render_marquee(self.marquee_text, self.marquee_x)

        # === STATE 2: CHRONOLOGICAL INTERMISSION BUFFER (THE CASCADING DICE POUR) ===
        elif self.state == "INTERMISSION_IDLE":
            self.intermission_frame_count += 1
            
            # Countdown must engage exactly 10 seconds before the extrapolated game target time
            countdown_start_trigger = self.blast_timestamp + self.target_delay - 10.0
            
            if now >= countdown_start_trigger:
                self.state = "COUNTDOWN"
                self.countdown_end_timestamp = self.blast_timestamp + self.target_delay
                return bytearray([0] * 300)
                
            return self.renderer.render_spill(self.intermission_frame_count)

        # === STATE 3: PERFECTLY SYNCED 10s COUNTDOWN CLOCK ===
        elif self.state == "COUNTDOWN":
            remaining_seconds = self.countdown_end_timestamp - now
            
            if remaining_seconds <= 0:
                self.state = "IDLE"
                self.is_real_match_data = False
                return bytearray([0] * 300)
            
            seconds_left = int(math.ceil(remaining_seconds))
            seconds_left = max(1, min(10, seconds_left))
            
            fractional_part = remaining_seconds - int(remaining_seconds)
            flash_intensity = 50 + (205 * fractional_part)
            
            return self.renderer.render_countdown(str(seconds_left), flash_intensity)

        # === STATE 4: THE IDLE INTERMISSION BUFFER (PANELS DARK) ===
        elif self.state == "IDLE":
            return bytearray([0] * 300)

        return bytearray([0] * 300)
