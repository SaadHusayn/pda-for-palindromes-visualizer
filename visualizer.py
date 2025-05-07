import tkinter as tk
from tkinter import ttk, messagebox
import math

class PDAVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NPDA Palindrome Visualizer")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0")
        self.style.configure("Result.TLabel", font=("Arial", 14), background="#f0f0f0")
        
        # Animation speed
        self.animation_speed = 1.0  # seconds between transitions
        
        # Create UI components
        self.create_ui()
        
        # Initialize NPDA components
        self.stack = []
        self.current_state = "q0"
        self.input_position = 0
        self.input_string = ""
        self.processing = False
        self.non_deterministic_paths = []
        self.current_path_index = 0
        self.chosen_path = None
        self.nondeterministic_choice_made = False
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Non-Deterministic PDA (NPDA) for Palindromes", 
                               style="Header.TLabel")
        title_label.pack(pady=10)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Enter a string over {a, b}:").pack(side=tk.LEFT, padx=5)
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 12), width=30)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = ttk.Frame(input_frame)
        speed_frame.pack(side=tk.RIGHT, padx=20)
        ttk.Label(speed_frame, text="Animation Speed:Fast").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.2, to=2.0, length=100, 
                                    orient=tk.HORIZONTAL, value=1.0,
                                    command=self.update_speed)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        ttk.Label(speed_frame, text="Slow").pack(side=tk.LEFT)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", 
                                      command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Button frames for different states
        self.q0_frame = ttk.Frame(button_frame)
        self.q0_frame.pack(side=tk.LEFT, padx=5)
        
        self.continue_push_button = ttk.Button(self.q0_frame, text="Continue Pushing", 
                                             command=lambda: self.make_choice(False), state=tk.DISABLED)
        self.continue_push_button.pack(side=tk.LEFT, padx=5)
        
        self.start_matching_button = ttk.Button(self.q0_frame, text="Select Center", 
                                              command=lambda: self.make_choice(True), state=tk.DISABLED)
        self.start_matching_button.pack(side=tk.LEFT, padx=5)
        
        self.q1_frame = ttk.Frame(button_frame)
        self.q1_frame.pack(side=tk.LEFT, padx=5)
        
        self.step_button = ttk.Button(self.q1_frame, text="Continue Popping", 
                                     command=self.step_forward, state=tk.DISABLED)
        self.step_button.pack(side=tk.LEFT, padx=5)
        
        # Canvas for PDA visualization
        self.canvas_frame = ttk.Frame(main_frame, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status and result frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.current_input_label = ttk.Label(status_frame, text="Current Input: ")
        self.current_input_label.pack(anchor=tk.W, pady=2)
        
        self.current_state_label = ttk.Label(status_frame, text="Current State: q0")
        self.current_state_label.pack(anchor=tk.W, pady=2)
        
        self.stack_label = ttk.Label(status_frame, text="Stack: []")
        self.stack_label.pack(anchor=tk.W, pady=2)
        
        self.result_label = ttk.Label(status_frame, text="Result: ", style="Result.TLabel")
        self.result_label.pack(anchor=tk.W, pady=5)
        
        # Description of PDA
        desc_frame = ttk.Frame(main_frame, borderwidth=2, relief=tk.GROOVE)
        desc_frame.pack(fill=tk.X, pady=10)
        
        description = (
            "Non-Deterministic Push Down Automata for Palindromes over L = {a, b}\n"
            "States: q0 (pushing), q1 (matching), q2 (accepting)\n"
            "Transitions:\n"
            "• In q0: (a, ε | a) - Read 'a', push 'a' to stack\n"
            "• In q0: (b, ε | b) - Read 'b', push 'b' to stack\n"
            "• From q0 to q1: (ε, ε | ε) - Non-deterministically guess the middle\n"
            "• In q1: (a, a | ε) - Read 'a', match 'a' on stack top, pop it\n"
            "• In q1: (b, b | ε) - Read 'b', match 'b' on stack top, pop it\n"
            "• From q1 to q2: (ε, Z₀ | Z₀) - If end of input and stack has only Z₀ → Accept"
        )
        
        ttk.Label(desc_frame, text=description, justify=tk.LEFT, 
                 padding=10).pack(fill=tk.X)
        
        # Draw initial PDA state
        self.draw_pda()
    
    def update_speed(self, value):
        self.animation_speed = float(value)
    
    def draw_pda(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 50 or height < 50:  # Canvas not properly initialized yet
            self.root.after(100, self.draw_pda)
            return
        
        # Draw states - using only 60% of width for PDA machine
        state_radius = 30
        q0_x, q0_y = width * 0.15, height * 0.5
        q1_x, q1_y = width * 0.35, height * 0.5
        q2_x, q2_y = width * 0.55, height * 0.5
        
        # State colors based on current state
        q0_color = "#ff9999" if self.current_state == "q0" else "white"
        q1_color = "#ff9999" if self.current_state == "q1" else "white"
        q2_color = "#ff9999" if self.current_state == "q2" else "white"
        
        # Draw PDA title
        self.canvas.create_text(width * 0.35, height * 0.25, text="NPDA States and Transitions",
                               font=("Arial", 12, "bold"))
        
        # Draw states
        self.canvas.create_oval(q0_x-state_radius, q0_y-state_radius, 
                               q0_x+state_radius, q0_y+state_radius, 
                               fill=q0_color, outline="black", width=2)
        self.canvas.create_text(q0_x, q0_y, text="q0\n(push)", font=("Arial", 12, "bold"))
        
        self.canvas.create_oval(q1_x-state_radius, q1_y-state_radius, 
                               q1_x+state_radius, q1_y+state_radius,
                               fill=q1_color, outline="black", width=2)
        self.canvas.create_text(q1_x, q1_y, text="q1\n(match)", font=("Arial", 12, "bold"))
        
        # Double circle for accepting state
        self.canvas.create_oval(q2_x-state_radius, q2_y-state_radius, 
                               q2_x+state_radius, q2_y+state_radius,
                               fill=q2_color, outline="black", width=2)
        self.canvas.create_oval(q2_x-state_radius+5, q2_y-state_radius+5, 
                               q2_x+state_radius-5, q2_y+state_radius-5,
                               outline="black", width=2)
        self.canvas.create_text(q2_x, q2_y, text="q2\n(accept)", font=("Arial", 12, "bold"))
        
        # Draw transitions
        # q0 to q0 self loop (for pushing characters) - improved curved arrow above the state
        self.draw_self_loop(q0_x, q0_y, state_radius, 90, 135, 45, 
                           "(a, ε | a)\n(b, ε | b)")
        
        # q0 to q1 (nondeterministic transition - guess middle)
        self.canvas.create_line(q0_x+state_radius, q0_y, q1_x-state_radius, q1_y,
                               arrow=tk.LAST, width=2)
        self.canvas.create_text((q0_x+q1_x)/2, q0_y-20, 
                               text="(ε, ε | ε)", 
                               font=("Arial", 10))
        
        # q1 self loop (matching and popping) - improved curved arrow above the state
        self.draw_self_loop(q1_x, q1_y, state_radius, 90, 135, 45, 
                           "(a, a | ε)\n(b, b | ε)")
        
        # q1 to q2 (acceptance when stack is empty or just Z₀)
        self.canvas.create_line(q1_x+state_radius, q1_y, q2_x-state_radius, q2_y,
                               arrow=tk.LAST, width=2)
        self.canvas.create_text((q1_x+q2_x)/2, q1_y-20, 
                               text="(ε, Z₀ | Z₀)", 
                               font=("Arial", 10))
        
        # Draw a vertical separator
        self.canvas.create_line(width * 0.7, height * 0.15, 
                               width * 0.7, height * 0.85, 
                               dash=(10, 5), fill="gray")
        
        # Draw the stack - moved further to the right
        stack_width = 100
        stack_x = width * 0.85
        stack_base_y = height * 0.85
        
        # Stack frame
        self.canvas.create_rectangle(stack_x - stack_width/2, height * 0.3,
                                    stack_x + stack_width/2, stack_base_y,
                                    outline="black", width=2)
        self.canvas.create_text(stack_x, height * 0.25, text="Stack",
                               font=("Arial", 12, "bold"))
        
        # Draw stack contents - FIXED: Display stack in correct order
        if not self.stack:
            self.canvas.create_text(stack_x, stack_base_y - 20, 
                                   text="Z₀ (Bottom)", font=("Arial", 10))
        else:
            stack_height = 25
            # Draw Z₀ at bottom
            self.canvas.create_rectangle(stack_x - 20, stack_base_y - stack_height,
                                       stack_x + 20, stack_base_y,
                                       fill="#dddddd", outline="black")
            self.canvas.create_text(stack_x, stack_base_y - stack_height/2,
                                   text="Z₀", font=("Arial", 10, "bold"))
            
            # Draw actual stack contents above Z₀ - in correct order (first pushed at bottom)
            for i, symbol in enumerate(self.stack): # Removed reversed() to display in correct order
                y_pos = stack_base_y - (i+2) * stack_height  # +2 to leave room for Z₀
                self.canvas.create_rectangle(stack_x - 20, y_pos,
                                           stack_x + 20, y_pos + stack_height,
                                           fill="#aaddff", outline="black")
                self.canvas.create_text(stack_x, y_pos + stack_height/2,
                                       text=symbol, font=("Arial", 12, "bold"))
        
        # Draw input string with current position
        if self.input_string:
            tape_y = height * 0.15
            cell_width = 30
            tape_start_x = (width - len(self.input_string) * cell_width) / 2
            
            # Draw the tape
            self.canvas.create_rectangle(tape_start_x - 10, tape_y - 20,
                                        tape_start_x + len(self.input_string) * cell_width + 10,
                                        tape_y + 20, outline="black", width=2)
            
            # Draw each cell
            for i, char in enumerate(self.input_string):
                cell_x = tape_start_x + i * cell_width
                cell_color = "#aaffaa" if i < self.input_position else "white"
                if i == self.input_position and self.current_state != "q2":
                    cell_color = "#ffaaaa"  # Current position
                
                self.canvas.create_rectangle(cell_x, tape_y - 20,
                                           cell_x + cell_width, tape_y + 20,
                                           fill=cell_color, outline="black")
                self.canvas.create_text(cell_x + cell_width/2, tape_y,
                                       text=char, font=("Arial", 12, "bold"))
            
            # Draw read head
            if self.input_position < len(self.input_string) and self.current_state != "q2":
                head_x = tape_start_x + self.input_position * cell_width + cell_width/2
                self.canvas.create_line(head_x, tape_y + 25, head_x, tape_y + 40,
                                      width=2, arrow=tk.LAST)
                self.canvas.create_text(head_x, tape_y + 50,
                                       text="Read Head", font=("Arial", 10))
                                       
        # Draw state-specific information
        info_x = width * 0.35
        info_y = height * 0.85
        
        if self.current_state == "q0":
            # Display information about state q0 actions
            self.canvas.create_rectangle(info_x - 180, info_y - 40,
                                       info_x + 180, info_y + 40,
                                       fill="#ffffcc", outline="black")
            
            self.canvas.create_text(info_x, info_y - 20,
                             text="State q0 (Pushing Phase)",
                             font=("Arial", 10, "bold"))
            
            self.canvas.create_text(info_x, info_y,
                             text="• Continue pushing symbols to stack",
                             font=("Arial", 10))
                             
            self.canvas.create_text(info_x, info_y + 20,
                             text="• Or select center and transition to q1",
                             font=("Arial", 10))
        
        elif self.current_state == "q1":
            # Display information about state q1 actions
            self.canvas.create_rectangle(info_x - 180, info_y - 40,
                                       info_x + 180, info_y + 40,
                                       fill="#ffffcc", outline="black")
            
            self.canvas.create_text(info_x, info_y - 20,
                             text="State q1 (Matching Phase)",
                             font=("Arial", 10, "bold"))
            
            self.canvas.create_text(info_x, info_y,
                             text="• Read input and compare with stack top",
                             font=("Arial", 10))
                             
            self.canvas.create_text(info_x, info_y + 20,
                             text="• Pop matching symbols from stack",
                             font=("Arial", 10))
    
    def draw_self_loop(self, x, y, radius, start_angle, arc_angle, end_angle, label_text):
        """Draw a self loop as a curved arrow pointing back to the same state"""
        # Calculate control points for the curved arrow
        start_angle_rad = math.radians(start_angle)
        arc_angle_rad = math.radians(arc_angle)
        end_angle_rad = math.radians(end_angle)
        
        # Start and end points of the arrow (on the state circle)
        start_x = x + radius * math.cos(start_angle_rad)
        start_y = y - radius * math.sin(start_angle_rad)  # Negative because y increases downward
        end_x = x + radius * math.cos(end_angle_rad)
        end_y = y - radius * math.sin(end_angle_rad)
        
        # Control point for the curve (above the state)
        control_x = x + radius * math.cos(arc_angle_rad) * 1.5
        control_y = y - radius * math.sin(arc_angle_rad) * 2  # Higher above state
        
        # Draw the curved arrow
        arrow_points = [start_x, start_y,
                       control_x, control_y,
                       end_x, end_y]
        
        self.canvas.create_line(arrow_points, smooth=True, arrow=tk.LAST, width=2)
        
        # Draw the label
        label_x = control_x
        label_y = control_y - 15  # Position label slightly above the curve
        self.canvas.create_text(label_x, label_y, text=label_text, font=("Arial", 10))

    def start_processing(self):
        self.input_string = self.input_entry.get().strip()
        
        # Validate input
        if not self.input_string:
            messagebox.showwarning("Invalid Input", "Please enter a string.")
            return
        
        if not all(c in 'ab' for c in self.input_string):
            messagebox.showwarning("Invalid Input", "Input must only contain 'a' and 'b'.")
            return
        
        # Handle empty string special case
        if not self.input_string:
            # Empty string is a palindrome
            self.result_label.configure(text="Result: Accepted (Empty palindrome)")
            messagebox.showinfo("PDA Result", "The empty string is a valid palindrome!")
            return
        
        # Initialize PDA
        self.reset()
        self.processing = True
        self.start_button.configure(state=tk.DISABLED)
        
        # Update UI
        self.current_input_label.configure(text=f"Current Input: {self.input_string}")
        self.result_label.configure(text="Result: Processing...")
        
        # In q0 initially, enable only push and select center buttons
        self.continue_push_button.configure(state=tk.NORMAL)
        self.start_matching_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)  # Disable popping in q0
        
        # Start automatic processing if not in step mode
        self.draw_pda()
    
    def reset(self):
        # Reset PDA state
        self.stack = []
        self.current_state = "q0"
        self.input_position = 0
        self.processing = False
        self.nondeterministic_choice_made = False
        
        # Reset UI
        self.result_label.configure(text="Result: ")
        self.current_state_label.configure(text="Current State: q0")
        self.stack_label.configure(text="Stack: []")
        self.current_input_label.configure(text="Current Input: ")
        
        # Reset button states
        self.start_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)
        self.continue_push_button.configure(state=tk.DISABLED)
        self.start_matching_button.configure(state=tk.DISABLED)
        
        # Redraw PDA
        self.draw_pda()
    
    def make_choice(self, start_matching):
        """Handle the non-deterministic choice at state q0"""
        self.nondeterministic_choice_made = True
        
        if start_matching:
            # Transition to matching state q1
            self.current_state = "q1"
            # Update UI to reflect state change
            self.current_state_label.configure(text=f"Current State: {self.current_state}")
            # Enable only the pop button when in q1
            self.continue_push_button.configure(state=tk.DISABLED)
            self.start_matching_button.configure(state=tk.DISABLED)
            self.step_button.configure(state=tk.NORMAL)
            # Redraw to show the state transition
            self.draw_pda()
            return
        
        # else: stay in q0 and continue pushing (already the default)
        # Process the next push step automatically
        self.process_step()
    
    def process_automatically(self):
        if not self.processing:
            return
            
        # Process a step if not at non-deterministic choice point
        if self.current_state != "q0" or self.nondeterministic_choice_made:
            result = self.process_step()
            
            # Continue processing if not done and not at choice point
            if result == "continue" and (self.current_state != "q0" or self.nondeterministic_choice_made):
                self.root.after(int(self.animation_speed * 1000), self.process_automatically)
    
    def step_forward(self):
        if not self.processing:
            return
            
        # Process just one step
        if self.current_state != "q0" or self.nondeterministic_choice_made:
            self.process_step()
    
    def process_step(self):
        # Update UI to show current state
        self.current_state_label.configure(text=f"Current State: {self.current_state}")
        self.stack_label.configure(text=f"Stack: {self.stack}")
        
        # State transitions logic
        if self.current_state == "q0":
            # First phase: reading input and pushing to stack
            if self.input_position < len(self.input_string):
                # Read character and push to stack
                current_char = self.input_string[self.input_position]
                self.stack.append(current_char)
                self.input_position += 1
                self.draw_pda()
                
                # Reset the choice flag after each push operation
                self.nondeterministic_choice_made = False
                
                # Enable choice buttons again
                if self.input_position < len(self.input_string):
                    self.continue_push_button.configure(state=tk.NORMAL)
                    self.start_matching_button.configure(state=tk.NORMAL)
                    self.step_button.configure(state=tk.DISABLED)  # Disable popping in q0
                else:
                    # If we've reached the end of input in state q0,
                    # we need to transition to state q1 automatically
                    self.current_state = "q1"
                    # Enable only popping in q1
                    self.continue_push_button.configure(state=tk.DISABLED)
                    self.start_matching_button.configure(state=tk.DISABLED)
                    self.step_button.configure(state=tk.NORMAL)
                    self.draw_pda()
                return "continue"
            else:
                # End of input in q0, transition to q1 for matching
                self.current_state = "q1"
                # Enable only popping in q1
                self.continue_push_button.configure(state=tk.DISABLED)
                self.start_matching_button.configure(state=tk.DISABLED)
                self.step_button.configure(state=tk.NORMAL)
                self.draw_pda()
                return "continue"
        
        elif self.current_state == "q1":
            # Second phase: comparing input with stack (from current position)
            if self.input_position < len(self.input_string):
                if not self.stack:  # Stack is empty but still have input to process
                    self.result_label.configure(text="Result: Rejected (Stack empty before end of input)")
                    self.processing = False
                    self.step_button.configure(state=tk.DISABLED)
                    self.draw_pda()
                    # Show rejection popup
                    messagebox.showerror("PDA Result", 
                        f"The string '{self.input_string}' is NOT a valid palindrome!\n\n"
                        f"Stack became empty before finishing the input processing.")
                    return "rejected"
                
                current_char = self.input_string[self.input_position]
                if not self.stack:  # Extra check to avoid pop from empty stack
                    self.result_label.configure(text="Result: Rejected (Stack empty but input remains)")
                    self.processing = False
                    self.step_button.configure(state=tk.DISABLED)
                    self.draw_pda()
                    return "rejected"
                    
                stack_top = self.stack.pop()

                
                if current_char != stack_top:
                    self.stack.append(stack_top) #this character can not be removed from the stack as there is mismatch
                    # Not a palindrome
                    self.result_label.configure(
                        text=f"Result: Rejected (Mismatch at position {self.input_position}, "
                             f"expected '{stack_top}' but got '{current_char}')")
                    self.processing = False
                    self.step_button.configure(state=tk.DISABLED)
                    self.draw_pda()
                    # Show rejection popup with detailed reason
                    messagebox.showerror("PDA Result", 
                        f"The string '{self.input_string}' is NOT a valid palindrome!\n\n"
                        f"Mismatch at position {self.input_position}: expected '{stack_top}' but got '{current_char}'")
                    return "rejected"
                
                self.input_position += 1
                self.draw_pda()
                return "continue"
            else:
                # End of input, check if stack is empty
                if not self.stack:
                    # Stack is empty, string is a palindrome
                    self.current_state = "q2"
                    self.result_label.configure(text="Result: Accepted (Palindrome)")
                    self.processing = False
                    self.step_button.configure(state=tk.DISABLED)
                    self.draw_pda()
                    # Show acceptance popup
                    messagebox.showinfo("PDA Result", f"The string '{self.input_string}' is a valid palindrome!")
                    return "accepted"
                else:
                    # Stack still has symbols, not a palindrome
                    self.result_label.configure(
                        text="Result: Rejected (Stack not empty after input processed)")
                    self.processing = False
                    self.step_button.configure(state=tk.DISABLED)
                    self.draw_pda()
                    # Show rejection popup
                    messagebox.showerror("PDA Result", f"The string '{self.input_string}' is NOT a valid palindrome! (Stack not empty after input processed)")
                    return "rejected"

if __name__ == "__main__":
    root = tk.Tk()
    app = PDAVisualizerApp(root)
    
    # Configure window resize behavior
    def on_resize(event):
        app.draw_pda()
    
    root.bind("<Configure>", on_resize)
    root.mainloop()