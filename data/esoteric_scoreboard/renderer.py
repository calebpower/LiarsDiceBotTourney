import random
from PIL import Image, ImageDraw

class ScoreboardRenderer:
    """
    Graphics processing core. Implements a comprehensive ASCII pixel sheet,
    pulsing panel logic, and the Cascading Dice Spill kinetic animation engine.
    """
    def __init__(self):
        self.width = 30
        self.height = 10
        
        # 1. Thin 4x7 font reserved strictly for numbers and countdown formatting
        self.FONT_NUMERIC = {
            '0': [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
            '1': ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
            '2': [" ### ", "#   #", "    #", " ### ", "#    ", "#    ", "#####"],
            '3': ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
            '4': ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
            '5': ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
            '6': [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
            '7': ["#####", "    #", "   # ", "  #  ", "  #  ", " #   ", " #   "],
            '8': [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
            '9': [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
            ' ': ["     ", "     ", "     ", "     ", "     ", "     ", "     "]
        }

        # 2. Premium 5x7 Heavy Bold font covering the entire printable ASCII spectrum (32-126)
        self.FONT_MARQUEE = {
            'A': [" ### ", "#####", "## ##", "#####", "## ##", "## ##", "## ##"],
            'B': ["#### ", "##  #", "##  #", "#### ", "##  #", "##  #", "#### "],
            'C': [" ####", "##   ", "##   ", "##   ", "##   ", "##   ", " ####"],
            'D': ["###  ", "## ##", "##  ##", "##  ##", "##  ##", "## ##", "###  "],
            'E': ["#####", "##   ", "##   ", "#### ", "##   ", "##   ", "#####"],
            'F': ["#####", "##   ", "##   ", "#### ", "##   ", "##   ", "##   "],
            'G': [" ####", "##   ", "##   ", "## ##", "##  #", "##  #", " ####"],
            'H': ["## ##", "## ##", "## ##", "#####", "## ##", "## ##", "## ##"],
            'I': ["#####", "  ## ", "  ## ", "  ## ", "  ## ", "  ## ", "#####"],
            'J': ["  ###", "   ##", "   ##", "   ##", "   ##", "## ##", " ### "],
            'K': ["##  #", "## # ", "###  ", "#### ", "## ##", "##  #", "##  #"],
            'L': ["##   ", "##   ", "##   ", "##   ", "##   ", "##   ", "#####"],
            'M': ["## ##", "#####", "# # #", "# # #", "## ##", "## ##", "## ##"],
            'N': ["##  #", "### #", "#####", "# ###", "#  ##", "#  ##", "#  ##"],
            'O': [" ### ", "#####", "## ##", "## ##", "## ##", "#####", " ### "],
            'P': ["#### ", "##  #", "##  #", "#### ", "##   ", "##   ", "##   "],
            'Q': [" ### ", "#####", "## ##", "## ##", "#####", " ### ", "    #"],
            'R': ["#### ", "##  #", "##  #", "#### ", "## ##", "##  #", "##  #"],
            'S': [" ####", "##  #", "###  ", " ####", "  ###", "##  #", "#### "],
            'T': ["#####", "  ## ", "  ## ", "  ## ", "  ## ", "  ## ", "  ## "],
            'U': ["## ##", "## ##", "## ##", "## ##", "## ##", "#####", " ### "],
            'V': ["## ##", "## ##", "## ##", "## ##", " ### ", " ### ", "  #  "],
            'W': ["## ##", "## ##", "## ##", "#####", " ### ", " ### ", "## ##"],
            'X': ["## ##", "## ##", " ### ", "  #  ", " ### ", "## ##", "## ##"],
            'Y': ["## ##", "## ##", " ### ", "  #  ", "  #  ", "  #  ", "  #  "],
            'Z': ["#####", "   ##", "  ## ", " ##  ", "##   ", "##   ", "#####"],
            '0': [" ### ", "#####", "## ##", "## ##", "## ##", "#####", " ### "],
            '1': ["  ## ", " ### ", "  ## ", "  ## ", "  ## ", "  ## ", "#####"],
            '2': [" ####", "##  #", "   ##", "  ## ", " ##  ", "##   ", "#####"],
            '3': ["#####", "   ##", "  ## ", " ####", "   ##", "   ##", "#####"],
            '4': ["   ##", "  ###", " ## ##", "#####", "   ##", "   ##", "   ##"],
            '5': ["#####", "##   ", "#### ", "   ##", "   ##", "##  #", " ####"],
            '6': [" ####", "##   ", "#### ", "#####", "##  #", "##  #", " ####"],
            '7': ["#####", "   ##", "  ## ", "  ## ", " ##  ", " ##  ", " ##  "],
            '8': [" ### ", "#####", "## ##", " ### ", "## ##", "#####", " ### "],
            '9': [" ####", "##  #", "##  #", "#####", "   ##", "   ##", "#### "],
            ' ': ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
            '.': ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
            ',': ["     ", "     ", "     ", "     ", "  ## ", "  ## ", " #   "],
            '!': [" ##  ", " ##  ", " ##  ", " ##  ", "     ", " ##  ", " ##  "],
            '?': [" ### ", "##  #", "   ##", "  ## ", "  ## ", "     ", "  ## "],
            '|': ["  ## ", "  ## ", "  ## ", "  ## ", "  ## ", "  ## ", "  ## "],
            "'": ["  ## ", "  ## ", "  #  ", "     ", "     ", "     ", "     "],
            '*': ["  #  ", "## ##", " ### ", "#####", " ### ", "## ##", "  #  "],
            ':': ["     ", "  ## ", "  ## ", "     ", "     ", "  ## ", "  ## "],
            '(': ["  ## ", " ##  ", " ##  ", " ##  ", " ##  ", " ##  ", "  ## "],
            ')': ["  ## ", "   ##", "   ##", "   ##", "   ##", "   ##", "  ## "],
            '-': ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
            '_': ["     ", "     ", "     ", "     ", "     ", "     ", "#####"],
            '"': [" # # ", " # # ", "     ", "     ", "     ", "     ", "     "],
            '`': [" ##  ", "  #  ", "     ", "     ", "     ", "     ", "     "],
            '/': ["    #", "   # ", "  #  ", "  #  ", " #   ", "#    ", "     "],
            '\\':["#    ", " #   ", "  #  ", "  #  ", "   # ", "    #", "     "],
            '[': [" ####", " ##  ", " ##  ", " ##  ", " ##  ", " ##  ", " ####"],
            ']': ["#### ", "  ## ", "  ## ", "  ## ", "  ## ", "  ## ", "#### "],
            '{': ["  ## ", "  #  ", " #   ", "##   ", " #   ", "  #  ", "  ## "],
            '}': [" ##  ", "  #  ", "   # ", "   ##", "   # ", "  #  ", " ##  "],
            '<': ["   ##", " ##  ", "##   ", " ##  ", "   ##", "     ", "     "],
            '>': ["##   ", "  ## ", "    ##", "  ## ", "##   ", "     ", "     "],
            '=': ["     ", "#####", "     ", "#####", "     ", "     ", "     "],
            '+': ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
            '%': ["##  #", "## # ", "  #  ", " # ##", "#  ##", "     ", "     "],
            '#': [" # # ", "#####", " # # ", "#####", " # # ", " # # ", "     "],
            '@': [" ### ", "#  ##", "# # #", "# ###", "#    ", " ### ", "     "],
            '$': ["  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "],
            '&': [" ### ", "#   #", " ### ", "# #  ", "#  # ", "#   #", " ####"],
            '^': ["  #  ", " # # ", "#   #", "     ", "     ", "     ", "     "],
            '~': [" # # ", "##  ", "     ", "     ", "     ", "     ", "     "]
        }

    def _create_blank_frame(self):
        """Initializes a clean black canvas frame workspace."""
        return Image.new('L', (self.width, self.height), color=0)

    def calculate_text_width(self, text):
        """Calculates exact text widths assuming marquee mode spacing variables."""
        if not text:
            return 0
        return len(text) * (5 + 3) - 3

    def _draw_bitmap_text(self, draw, text, start_x, y_pos, font_dict, char_width, char_spacing, fill_value=255):
        """Iterates text, substituting unprintable and unknown symbols safely based on font capabilities."""
        current_x = start_x
        for char in text.upper():
            ascii_val = ord(char)
            fallback_char = '_' if '_' in font_dict else ' '
            
            if ascii_val < 32 or ascii_val > 126:
                glyph_char = fallback_char
            else:
                glyph_char = char if char in font_dict else fallback_char
                
            glyph = font_dict[glyph_char]
            
            for row_idx, row_str in enumerate(glyph):
                for col_idx, pixel_char in enumerate(row_str):
                    if pixel_char == '#':
                        draw.point((current_x + col_idx, y_pos + row_idx), fill=int(fill_value))
                        
            current_x += char_width + char_spacing

    def render_marquee(self, text, x_pos):
        """Renders wide, chunkier bold text using our 3-pixel breathing space configuration."""
        frame = self._create_blank_frame()
        draw = ImageDraw.Draw(frame)
        y_pos = (self.height - 7) // 2
        
        self._draw_bitmap_text(
            draw=draw, 
            text=text, 
            start_x=x_pos, 
            y_pos=y_pos, 
            font_dict=self.FONT_MARQUEE, 
            char_width=5, 
            char_spacing=3, 
            fill_value=255
        )
        return bytearray(frame.getdata())

    def render_spill(self, frame_num):
        """
        Executes 'The Cascading Dice Spill' animation. Drops scrambling 3x3 dice
        from rotating dynamic columns in the yellow, filling the red and blue completely solid
        exactly at frame 600 right when the countdown sequence triggers.
        """
        frame = self._create_blank_frame()
        draw = ImageDraw.Draw(frame)
        
        # 1. Scale heap limits to 100 cells per wing (entirely fills panels 0-9 and 20-29)
        progress = min(1.0, frame_num / 600.0)
        max_piled_pixels = 100
        current_pile_count = int(progress * max_piled_pixels)
        
        pile_rng = random.Random(80085) # Fixed seed ensures non-flickering cell accumulation
        
        # Compiles full coordinate layouts mapping all 100 pixels per side panel
        left_pile_coords = [(x, y) for y in range(9, -1, -1) for x in range(10)]
        right_pile_coords = [(x, y) for y in range(9, -1, -1) for x in range(20, 30)]
        pile_rng.shuffle(left_pile_coords)
        pile_rng.shuffle(right_pile_coords)
        
        # Paint the static accumulated block layers at a dim, ambient baseline index (40)
        for i in range(min(current_pile_count, 100)):
            draw.point(left_pile_coords[i], fill=40)
            draw.point(right_pile_coords[i], fill=40)

        # 2. Cycle drop locations dynamically inside the yellow panel (columns 10 to 19)
        cycle_frame = frame_num % 40
        cycle_index = frame_num // 40
        
        # Calculate changing offset column across columns 10 to 17 (3x3 die fits perfectly)
        x_start = 10 + ((cycle_index * 3) % 8)
        
        if cycle_frame < 20:
            # --- PHASE A: THE POUR ---
            y_top = int(cycle_frame * 10 / 20) - 3
            
            for dy in range(3):
                y_coord = y_top + dy
                if 0 <= y_coord < 10:
                    for dx in range(3):
                        x_coord = x_start + dx
                        if random.choice([True, False]):
                            draw.point((x_coord, y_coord), fill=255)
                            
        elif cycle_frame < 32:
            # --- PHASE B: THE SPLASH ---
            splash_ticks = cycle_frame - 20
            
            # Left shard bursts out from x_start toward the Red panel
            lx = x_start - int(splash_ticks * 1.2)
            ly = 8 + (splash_ticks % 2)
            if 0 <= lx < 30:
                draw.point((lx, ly), fill=180)
                draw.point((lx + 1, min(9, ly + 1)), fill=100)
                
            # Right shard bursts out from the right edge (x_start + 2) toward the Blue panel
            rx = (x_start + 2) + int(splash_ticks * 1.2)
            ry = 8 + ((splash_ticks + 1) % 2)
            if 0 <= rx < 30:
                draw.point((rx, ry), fill=180)
                draw.point((rx - 1, min(9, ry + 1)), fill=100)

        return bytearray(frame.getdata())

    def render_countdown(self, number_str, flash_intensity):
        """Paints crisp numeric digits in the center while executing ambient side panel pulses."""
        frame = self._create_blank_frame()
        draw = ImageDraw.Draw(frame)
        
        # 1. Soft side panel pulse translation mapping (Red left 0-9, Blue right 20-29)
        side_intensity = int(flash_intensity * 0.45)
        for y in range(self.height):
            for x in range(10):
                draw.point((x, y), fill=side_intensity)
            for x in range(20, 30):
                draw.point((x, y), fill=side_intensity)
                
        # 2. Render center countdown text asset
        y_pos = (self.height - 7) // 2
        text_width = len(number_str) * (5 + 1) - 1
        start_x = 10 + (10 - text_width) // 2
        
        self._draw_bitmap_text(
            draw=draw, 
            text=number_str, 
            start_x=start_x, 
            y_pos=y_pos, 
            font_dict=self.FONT_NUMERIC, 
            char_width=5, 
            char_spacing=1, 
            fill_value=flash_intensity
        )
        return bytearray(frame.getdata())
