import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os
import time
from pygame import mixer
from datetime import datetime

class Game2048Tkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("2048 Game")
        
        # Game configuration with fixed 4x4 grid
        self.grid_size = 4  # Fixed size
        self.cell_size = 100
        self.padding = 10
        self.score = 0
        self.high_score = self.load_high_score()
        self.moves_count = 0
        self.start_time = time.time()
        self.game_active = True
        self.tutorial_mode = False
        self.tutorial_step = 0
        self.tutorial_instructions = [
            "Welcome to 2048! The goal is to combine tiles to reach 2048.",
            "Use arrow keys to move tiles. Try moving RIGHT now.",
            "Good! When two tiles with the same number collide, they merge!",
            "Now try moving UP to combine the tiles.",
            "Excellent! Keep combining tiles to reach higher numbers.",
            "Tutorial complete! Try to reach 2048 on your own now."
        ]
        
        # Initialize sound mixer
        mixer.init()
        self.load_sounds()
        
        # Color scheme
        self.setup_colors()
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        self.root.minsize(400, 500)
        self.setup_menu()
        
        # Initialize game
        self.initialize_game()
        
        # Key bindings
        self.setup_key_bindings()
    
    def setup_colors(self):
        """Configure the color scheme for the game"""
        self.bg_color = "#121212"  # Dark background
        self.frame_bg = "#1E1E1E"  # Slightly lighter than background
        self.text_color = "#FFFFFF"  # White text
        self.empty_color = "#2D2D2D"  # Dark gray for empty cells
        self.tutorial_highlight = "#FFD700"  # Gold for tutorial highlights
        
        # Different colors for different tile values
        self.tile_colors = {
            0: self.empty_color, 
            2: "#A5CA6B", 4: "#7A9D4F", 8: "#EE6B6E", 
            16: "#F7B801", 32: "#96CDFA", 64: "#588B8B", 
            128: "#FF9F1C", 256: "#E71D36", 512: "#2EC4B6", 
            1024: "#011627", 2048: "#FF3366", 4096: "#9B59B6",
            8192: "#1ABC9C", 16384: "#D35400", 32768: "#34495E"
        }
        
        # Text colors that contrast with tile colors
        self.text_colors = {
            2: "#FFFFFF", 4: "#FFFFFF", 8: "#FFFFFF", 
            16: "#FFFFFF", 32: "#FFFFFF", 64: "#FFFFFF", 
            128: "#FFFFFF", 256: "#FFFFFF", 512: "#FFFFFF", 
            1024: "#FFFFFF", 2048: "#FFFFFF", 4096: "#FFFFFF",
            8192: "#FFFFFF", 16384: "#FFFFFF", 32768: "#FFFFFF"
        }
    
    def setup_menu(self):
        """Create the game menu"""
        menubar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Tutorial Mode", command=self.start_tutorial)
        game_menu.add_separator()
        game_menu.add_command(label="Save Game", command=self.save_game)
        game_menu.add_command(label="Load Game", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Statistics", command=self.show_statistics)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.exit_game)
        menubar.add_cascade(label="Game", menu=game_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Controls", command=self.show_controls)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def initialize_game(self):
        """Initialize or reinitialize the game board"""
        # Clear existing widgets if they exist
        if hasattr(self, 'score_frame'):
            self.score_frame.destroy()
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()
        if hasattr(self, 'instructions'):
            self.instructions.destroy()
        if hasattr(self, 'tutorial_label'):
            self.tutorial_label.destroy()
        
        # Reset game state
        self.grid = [[0]*self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.moves_count = 0
        self.start_time = time.time()
        self.game_active = True
        self.tutorial_mode = False
        self.tutorial_step = 0
        
        # Create widgets
        self.create_widgets()
        
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
        self.update_ui()
    
    def create_widgets(self):
        """Create all the game widgets"""
        # Score display
        self.score_frame = tk.Frame(self.root, bg=self.frame_bg)
        self.score_frame.pack(pady=10)
        
        self.score_label = tk.Label(
            self.score_frame, 
            text=f"Score: {self.score}", 
            font=("Arial", 14), 
            bg=self.frame_bg, 
            fg=self.text_color
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.high_score_label = tk.Label(
            self.score_frame, 
            text=f"High Score: {self.high_score}", 
            font=("Arial", 14), 
            bg=self.frame_bg, 
            fg=self.text_color
        )
        self.high_score_label.pack(side=tk.LEFT, padx=20)
        
        # Moves counter
        self.moves_label = tk.Label(
            self.score_frame,
            text=f"Moves: {self.moves_count}",
            font=("Arial", 14),
            bg=self.frame_bg,
            fg=self.text_color
        )
        self.moves_label.pack(side=tk.LEFT, padx=20)
        
        # Game grid
        self.grid_frame = tk.Frame(self.root, bg=self.frame_bg)
        self.grid_frame.pack(padx=10, pady=10)
        
        self.cells = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                cell = tk.Label(
                    self.grid_frame, 
                    text="", 
                    width=4, 
                    height=2, 
                    font=("Arial", 24, "bold"), 
                    relief="raised",
                    bg=self.empty_color,
                    fg=self.text_color
                )
                cell.grid(row=i, column=j, padx=self.padding, pady=self.padding)
                row.append(cell)
            self.cells.append(row)
        
        # Tutorial label (initially hidden)
        self.tutorial_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.tutorial_highlight,
            wraplength=400
        )
        
        # Instructions
        self.instructions = tk.Label(
            self.root, 
            text="Controls: Arrow keys, WASD, or 2/4/6/8 to move. R=Restart", 
            font=("Arial", 10), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        self.instructions.pack(pady=10)
    
    def setup_key_bindings(self):
        """Set up all keyboard bindings"""
        # Movement keys
        movement_bindings = [
            ("<Up>", 0), ("<Right>", 1), ("<Down>", 2), ("<Left>", 3),
            ("w", 0), ("d", 1), ("s", 2), ("a", 3),
            ("8", 0), ("6", 1), ("2", 2), ("4", 3)
        ]
        
        for key, direction in movement_bindings:
            self.root.bind(key, lambda e, d=direction: self.move(d))
        
        # Function keys
        self.root.bind("r", lambda e: self.reset_game())
        self.root.bind("0", lambda e: self.exit_game())
    
    def start_tutorial(self):
        """Start the tutorial mode"""
        self.reset_game()
        self.tutorial_mode = True
        self.tutorial_step = 0
        
        # Set up initial tutorial grid
        self.grid = [[0]*self.grid_size for _ in range(self.grid_size)]
        self.grid[0][0] = 2
        self.grid[0][1] = 2
        self.grid[1][0] = 4
        self.update_ui()
        
        # Show tutorial label
        self.tutorial_label.pack(pady=10)
        self.update_tutorial_instruction()
        
        # Highlight relevant tiles
        self.highlight_tutorial_tiles()
    
    def update_tutorial_instruction(self):
        """Update the tutorial instruction text"""
        if self.tutorial_step < len(self.tutorial_instructions):
            self.tutorial_label.config(text=self.tutorial_instructions[self.tutorial_step])
        else:
            self.tutorial_label.pack_forget()
    
    def highlight_tutorial_tiles(self):
        """Highlight tiles relevant to the current tutorial step"""
        # Reset all highlights first
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                self.cells[i][j].config(bg=self.tile_colors.get(value, self.empty_color))
        
        if self.tutorial_step == 1:  # Right move
            for j in range(self.grid_size):
                if self.grid[0][j] != 0:
                    self.cells[0][j].config(bg=self.tutorial_highlight)
        elif self.tutorial_step == 3:  # Up move
            for i in range(self.grid_size):
                if self.grid[i][0] != 0:
                    self.cells[i][0].config(bg=self.tutorial_highlight)
    
    def load_sounds(self):
        """Initialize sound effects"""
        self.sound_enabled = True
        try:
            # Try to load sounds, use silent mode if files not found
            self.move_sound = mixer.Sound("sounds/move.wav") if os.path.exists("sounds/move.wav") else None
            self.merge_sound = mixer.Sound("sounds/merge.wav") if os.path.exists("sounds/merge.wav") else None
            self.game_over_sound = mixer.Sound("sounds/game_over.wav") if os.path.exists("sounds/game_over.wav") else None
            self.win_sound = mixer.Sound("sounds/win.wav") if os.path.exists("sounds/win.wav") else None
            self.tutorial_sound = mixer.Sound("sounds/tutorial.wav") if os.path.exists("sounds/tutorial.wav") else None
        except:
            self.sound_enabled = False
    
    def play_sound(self, sound_type):
        """Play the specified sound effect"""
        if not self.sound_enabled or not self.game_active:
            return
            
        try:
            if sound_type == "move" and self.move_sound:
                self.move_sound.play()
            elif sound_type == "merge" and self.merge_sound:
                self.merge_sound.play()
            elif sound_type == "game_over" and self.game_over_sound:
                self.game_over_sound.play()
            elif sound_type == "win" and self.win_sound:
                self.win_sound.play()
            elif sound_type == "tutorial" and self.tutorial_sound:
                self.tutorial_sound.play()
        except:
            pass
    
    def load_high_score(self):
        """Load the high score from file"""
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except:
            return 0
        return 0
    
    def save_high_score(self):
        """Save the high score to file"""
        try:
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
    
    def save_game(self):
        """Save the current game state to a file with player-chosen name"""
        if self.tutorial_mode:
            messagebox.showinfo("Cannot Save", "Cannot save game during tutorial mode.")
            return
            
        game_state = {
            "grid": self.grid,
            "score": self.score,
            "high_score": self.high_score,
            "moves_count": self.moves_count,
            "start_time": self.start_time,
            "elapsed_time": time.time() - self.start_time
        }
        
        try:
            # Ask player for save file name
            save_name = simpledialog.askstring(
                "Save Game",
                "Enter a name for your saved game:",
                parent=self.root
            )
            
            if not save_name:
                return  # User cancelled
            
            # Ensure the name ends with .json
            if not save_name.lower().endswith('.json'):
                save_name += '.json'
            
            # Create the save directory if it doesn't exist
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),  "saved")
            os.makedirs(save_dir, exist_ok=True)
            
            # Save to the new directory
            filename = os.path.join(save_dir, save_name)
            
            with open(filename, "w") as f:
                json.dump(game_state, f)
            messagebox.showinfo("Game Saved", f"Game successfully saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save game: {str(e)}")
    
    def load_game(self):
        """Load a game state from a file"""
        try:
            # Create the save directory if it doesn't exist
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2048", "saved")
            os.makedirs(save_dir, exist_ok=True)
            
            # Get list of save files in the directory
            save_files = [f for f in os.listdir(save_dir) if f.endswith(".json")]
            
            if not save_files:
                messagebox.showinfo("No Saved Games", "No saved games found.")
                return
            
            # Let user select a file
            selected_file = simpledialog.askstring(
                "Load Game",
                "Enter save file name:\n\n" + "\n".join(save_files),
                parent=self.root
            )
            
            if not selected_file:
                return
                
            # Construct full path
            full_path = os.path.join(save_dir, selected_file)
            
            if not os.path.exists(full_path):
                messagebox.showerror("Load Error", "File not found.")
                return
            
            with open(full_path, "r") as f:
                game_state = json.load(f)
            
            # Validate the loaded game state
            if not all(key in game_state for key in ["grid", "score", "moves_count"]):
                messagebox.showerror("Load Error", "Invalid save file format.")
                return
            
            # Clear existing widgets
            if hasattr(self, 'score_frame'):
                self.score_frame.destroy()
            if hasattr(self, 'grid_frame'):
                self.grid_frame.destroy()
            if hasattr(self, 'instructions'):
                self.instructions.destroy()
            if hasattr(self, 'tutorial_label'):
                self.tutorial_label.destroy()
            
            # Set the game state
            self.grid = game_state["grid"]
            self.score = game_state["score"]
            self.high_score = game_state.get("high_score", self.load_high_score())
            self.moves_count = game_state["moves_count"]
            self.tutorial_mode = False
            
            # Adjust start time based on elapsed time
            elapsed = game_state.get("elapsed_time", 0)
            self.start_time = time.time() - elapsed
            self.game_active = True
            
            # Create widgets
            self.create_widgets()
            self.update_ui()
            
            messagebox.showinfo("Game Loaded", "Game successfully loaded.")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load game: {str(e)}")
    
    def add_random_tile(self):
        """Add a random tile (2 or 4) to an empty cell"""
        if self.tutorial_mode and self.tutorial_step < 5:
            return  # Don't add random tiles during tutorial
            
        empty_cells = [(i, j) for i in range(self.grid_size) 
                      for j in range(self.grid_size) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 4 if random.random() < 0.3 else 2
    
    def update_ui(self):
        """Update the game interface"""
        # Update grid cells
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                font_size = self.calculate_font_size(value)
                self.cells[i][j].config(
                    text=str(value) if value else "",
                    bg=self.tile_colors.get(value, self.empty_color),
                    fg=self.text_colors.get(value, self.text_color),
                    font=("Arial", font_size, "bold")
                )
        
        # Update score and moves
        self.score_label.config(text=f"Score: {self.score}")
        self.high_score_label.config(text=f"High Score: {self.high_score}")
        self.moves_label.config(text=f"Moves: {self.moves_count}")
        
        # Update tutorial highlights if in tutorial mode
        if self.tutorial_mode:
            self.highlight_tutorial_tiles()
    
    def calculate_font_size(self, value):
        """Calculate appropriate font size based on tile value"""
        if value == 0:
            return 24
        
        digits = len(str(value))
        
        if digits <= 2:
            return 24
        elif digits == 3:
            return 20
        elif digits == 4:
            return 16
        else:
            return 12
    
    def move(self, direction):
        """Handle a move in the specified direction"""
        if not self.game_active:
            return
            
        moved = False
        merge_positions = set()
        
        # Process the move based on direction
        if direction == 0:  # Up
            moved = self.process_move_up(merge_positions)
        elif direction == 1:  # Right
            moved = self.process_move_right(merge_positions)
        elif direction == 2:  # Down
            moved = self.process_move_down(merge_positions)
        elif direction == 3:  # Left
            moved = self.process_move_left(merge_positions)
        
        if moved:
            self.moves_count += 1
            self.play_sound("move")
            
            if self.tutorial_mode:
                self.handle_tutorial_progress(direction)
            else:
                self.add_random_tile()
                
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            
            self.update_ui()
            
            # Highlight merged tiles briefly
            for i, j in merge_positions:
                self.cells[i][j].config(bg="#FFD700")
                self.root.after(100, lambda i=i, j=j: self.update_ui())
            
            if not self.tutorial_mode:
                if self.is_game_over():
                    self.game_over()
                elif self.has_won():
                    self.player_wins()
    
    def handle_tutorial_progress(self, direction):
        """Handle tutorial progress after a move"""
        if self.tutorial_step == 1 and direction == 1:  # Right move
            self.tutorial_step += 1
            self.play_sound("tutorial")
            self.update_tutorial_instruction()
        elif self.tutorial_step == 3 and direction == 0:  # Up move
            self.tutorial_step += 1
            self.play_sound("tutorial")
            self.update_tutorial_instruction()
        elif self.tutorial_step >= 5:  # Tutorial complete
            self.tutorial_mode = False
            self.tutorial_label.pack_forget()
            self.add_random_tile()
    
    def process_move_up(self, merge_positions):
        """Process upward move and return if any tiles moved"""
        moved = False
        for j in range(self.grid_size):
            column = [self.grid[i][j] for i in range(self.grid_size) if self.grid[i][j] != 0]
            merged = []
            i = 0
            while i < len(column):
                if i + 1 < len(column) and column[i] == column[i + 1]:
                    merged_value = column[i] * 2
                    merged.append(merged_value)
                    merge_positions.add((len(merged)-1, j))
                    self.score += merged_value
                    i += 2
                    self.play_sound("merge")
                else:
                    merged.append(column[i])
                    i += 1
            merged += [0] * (self.grid_size - len(merged))
            for i in range(self.grid_size):
                if self.grid[i][j] != merged[i]:
                    moved = True
                self.grid[i][j] = merged[i]
        return moved
    
    def process_move_right(self, merge_positions):
        """Process right move and return if any tiles moved"""
        moved = False
        for i in range(self.grid_size):
            row = [self.grid[i][j] for j in range(self.grid_size-1, -1, -1) if self.grid[i][j] != 0]
            merged = []
            j = 0
            while j < len(row):
                if j + 1 < len(row) and row[j] == row[j + 1]:
                    merged_value = row[j] * 2
                    merged.append(merged_value)
                    merge_positions.add((i, self.grid_size-1-(len(merged)-1)))
                    self.score += merged_value
                    j += 2
                    self.play_sound("merge")
                else:
                    merged.append(row[j])
                    j += 1
            merged += [0] * (self.grid_size - len(merged))
            for j in range(self.grid_size):
                if self.grid[i][self.grid_size-1-j] != merged[j]:
                    moved = True
                self.grid[i][self.grid_size-1-j] = merged[j]
        return moved
    
    def process_move_down(self, merge_positions):
        """Process downward move and return if any tiles moved"""
        moved = False
        for j in range(self.grid_size):
            column = [self.grid[i][j] for i in range(self.grid_size-1, -1, -1) if self.grid[i][j] != 0]
            merged = []
            i = 0
            while i < len(column):
                if i + 1 < len(column) and column[i] == column[i + 1]:
                    merged_value = column[i] * 2
                    merged.append(merged_value)
                    merge_positions.add((self.grid_size-1-(len(merged)-1), j))
                    self.score += merged_value
                    i += 2
                    self.play_sound("merge")
                else:
                    merged.append(column[i])
                    i += 1
            merged += [0] * (self.grid_size - len(merged))
            for i in range(self.grid_size):
                if self.grid[self.grid_size-1-i][j] != merged[i]:
                    moved = True
                self.grid[self.grid_size-1-i][j] = merged[i]
        return moved
    
    def process_move_left(self, merge_positions):
        """Process left move and return if any tiles moved"""
        moved = False
        for i in range(self.grid_size):
            row = [self.grid[i][j] for j in range(self.grid_size) if self.grid[i][j] != 0]
            merged = []
            j = 0
            while j < len(row):
                if j + 1 < len(row) and row[j] == row[j + 1]:
                    merged_value = row[j] * 2
                    merged.append(merged_value)
                    merge_positions.add((i, len(merged)-1))
                    self.score += merged_value
                    j += 2
                    self.play_sound("merge")
                else:
                    merged.append(row[j])
                    j += 1
            merged += [0] * (self.grid_size - len(merged))
            for j in range(self.grid_size):
                if self.grid[i][j] != merged[j]:
                    moved = True
                self.grid[i][j] = merged[j]
        return moved
    
    def has_won(self):
        """Check if the player has reached the 2048 tile"""
        return any(2048 in row for row in self.grid)
    
    def is_game_over(self):
        """Check if the game is over (no more valid moves)"""
        if self.tutorial_mode:
            return False
            
        # Check if there are empty cells
        if any(0 in row for row in self.grid):
            return False
        
        # Check for possible merges
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if j + 1 < self.grid_size and self.grid[i][j] == self.grid[i][j + 1]:
                    return False
                if i + 1 < self.grid_size and self.grid[i][j] == self.grid[i + 1][j]:
                    return False
        
        return True
    
    def game_over(self):
        """Handle game over condition"""
        self.game_active = False
        self.play_sound("game_over")
        elapsed_time = time.time() - self.start_time
        time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        
        stats = (
            f"Game Over!\n\n"
            f"Final Score: {self.score}\n"
            f"Moves: {self.moves_count}\n"
            f"Time Played: {time_str}\n\n"
            f"Click OK to restart."
        )
        
        if messagebox.showinfo("Game Over", stats):
            self.reset_game()
    
    def player_wins(self):
        """Handle winning condition"""
        self.play_sound("win")
        elapsed_time = time.time() - self.start_time
        time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        
        stats = (
            f"Congratulations! You reached 2048!\n\n"
            f"Score: {self.score}\n"
            f"Moves: {self.moves_count}\n"
            f"Time Played: {time_str}\n\n"
            f"Click OK to continue playing."
        )
        
        messagebox.showinfo("You Win!", stats)
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.initialize_game()
    
    def show_statistics(self):
        """Show game statistics"""
        elapsed_time = time.time() - self.start_time
        time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        
        stats = (
            f"Current Game Statistics:\n\n"
            f"Score: {self.score}\n"
            f"Moves: {self.moves_count}\n"
            f"Time Played: {time_str}\n\n"
            f"High Score: {self.high_score}"
        )
        
        messagebox.showinfo("Game Statistics", stats)
    
    def show_controls(self):
        """Show game controls information"""
        controls = (
            "Game Controls:\n\n"
            "Movement:\n"
            "• Arrow keys (↑ → ↓ ←)\n"
            "• WASD (W=Up, A=Left, S=Down, D=Right)\n"
            "• Numpad (8=Up, 4=Left, 2=Down, 6=Right)\n\n"
            "Actions:\n"
            "• R - Restart game\n"
            "• 0 - Exit game\n\n"
            "Menu Options:\n"
            "• Tutorial Mode\n"
            "• View statistics\n"
        )
        messagebox.showinfo("Game Controls", controls)
    
    def show_about(self):
        """Show about information"""
        about = (
            "2048 Game\n\n"
            "A Python implementation of the popular 2048 puzzle game\n"
            "using Tkinter for the GUI.\n\n"
            "Features:\n"
            "- Basic animations\n"
            "- Sound effects\n"
            "- Game statistics\n"
            "- Tutorial mode\n"
            "- Fixed 4x4 grid"
        )
        messagebox.showinfo("About 2048", about)
    
    def exit_game(self):
        """Exit the game after confirmation"""
        if messagebox.askokcancel("Exit Game", "Do you really want to exit the game?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048Tkinter(root)
    root.mainloop()