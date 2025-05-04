import tkinter as tk
from tkinter import ttk, messagebox
import time

class PDAVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDA Palindrome Visualizer")
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
        
        # Initialize PDA components
        self.stack = []
        self.current_state = "q0"
        self.input_position = 0
        self.input_string = ""
        self.processing = False
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Push Down Automata (PDA) for Palindromes", 
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
        ttk.Label(speed_frame, text="Animation Speed:").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.2, to=2.0, length=100, 
                                    orient=tk.HORIZONTAL, value=1.0,
                                    command=self.update_speed)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        ttk.Label(speed_frame, text="Slow").pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="Fast").pack(side=tk.RIGHT)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", 
                                      command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.step_button = ttk.Button(button_frame, text="Step Forward", 
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
            "Push Down Automata for Palindromes over L = {a, b}\n"
            "States: q0 (initial), q1 (middle), q2 (accepting)\n"
            "Transitions:\n"
            "• In q0: Read 'a'/'b' → Push to stack → Stay in q0\n"
            "• From q0 to q1: Read ε (empty) → No stack change → Move to q1 (now checking palindrome)\n"
            "• In q1: Read 'a'/'b' → Pop from stack and compare → Stay in q1 if matching\n"
            "• From q1 to q2: If stack is empty → Accept the string"
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
        self.canvas.create_text(width * 0.35, height * 0.25, text="PDA States and Transitions",
                               font=("Arial", 12, "bold"))
        
        # Draw states
        self.canvas.create_oval(q0_x-state_radius, q0_y-state_radius, 
                               q0_x+state_radius, q0_y+state_radius, 
                               fill=q0_color, outline="black", width=2)
        self.canvas.create_text(q0_x, q0_y, text="q0\n(start)", font=("Arial", 12, "bold"))
        
        self.canvas.create_oval(q1_x-state_radius, q1_y-state_radius, 
                               q1_x+state_radius, q1_y+state_radius,
                               fill=q1_color, outline="black", width=2)
        self.canvas.create_text(q1_x, q1_y, text="q1\n(middle)", font=("Arial", 12, "bold"))
        
        # Double circle for accepting state
        self.canvas.create_oval(q2_x-state_radius, q2_y-state_radius, 
                               q2_x+state_radius, q2_y+state_radius,
                               fill=q2_color, outline="black", width=2)
        self.canvas.create_oval(q2_x-state_radius+5, q2_y-state_radius+5, 
                               q2_x+state_radius-5, q2_y+state_radius-5,
                               outline="black", width=2)
        self.canvas.create_text(q2_x, q2_y, text="q2\n(accept)", font=("Arial", 12, "bold"))
        
        # Draw transitions
        # q0 to q0 (self loop)
        self.canvas.create_arc(q0_x-40, q0_y-80, q0_x+40, q0_y-20,
                              start=30, extent=120, style=tk.ARC, width=2)
        self.canvas.create_text(q0_x, q0_y-60, 
                               text="a → push a\nb → push b", 
                               font=("Arial", 10))
        
        # q0 to q1
        self.canvas.create_line(q0_x+state_radius, q0_y, q1_x-state_radius, q1_y,
                               arrow=tk.LAST, width=2)
        self.canvas.create_text((q0_x+q1_x)/2, q0_y-20, 
                               text="ε, ε → ε", 
                               font=("Arial", 10))
        
        # q1 to q1 (self loop)
        self.canvas.create_arc(q1_x-40, q1_y-80, q1_x+40, q1_y-20,
                              start=30, extent=120, style=tk.ARC, width=2)
        self.canvas.create_text(q1_x, q1_y-60, 
                               text="a, a → ε\nb, b → ε", 
                               font=("Arial", 10))
        
        # q1 to q2
        self.canvas.create_line(q1_x+state_radius, q1_y, q2_x-state_radius, q2_y,
                               arrow=tk.LAST, width=2)
        self.canvas.create_text((q1_x+q2_x)/2, q1_y-20, 
                               text="ε, Z₀ → Z₀", 
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
        
        # Draw stack contents
        if not self.stack:
            self.canvas.create_text(stack_x, stack_base_y - 20, 
                                   text="Empty", font=("Arial", 10))
        else:
            stack_height = 25
            for i, symbol in enumerate(reversed(self.stack)):
                y_pos = stack_base_y - (i+1) * stack_height
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
    
    def start_processing(self):
        self.input_string = self.input_entry.get().strip()
        
        # Validate input
        if not self.input_string:
            messagebox.showwarning("Invalid Input", "Please enter a string.")
            return
        
        if not all(c in 'ab' for c in self.input_string):
            messagebox.showwarning("Invalid Input", "Input must only contain 'a' and 'b'.")
            return
        
        # Initialize PDA
        self.reset()
        self.processing = True
        self.step_button.configure(state=tk.NORMAL)
        self.start_button.configure(state=tk.DISABLED)
        
        # Update UI
        self.current_input_label.configure(text=f"Current Input: {self.input_string}")
        self.result_label.configure(text="Result: Processing...")
        
        # Start automatic processing if not in step mode
        self.process_automatically()
    
    def reset(self):
        # Reset PDA state
        self.stack = []
        self.current_state = "q0"
        self.input_position = 0
        self.processing = False
        
        # Reset UI
        self.result_label.configure(text="Result: ")
        self.current_state_label.configure(text="Current State: q0")
        self.stack_label.configure(text="Stack: []")
        self.current_input_label.configure(text="Current Input: ")
        self.start_button.configure(state=tk.NORMAL)
        self.step_button.configure(state=tk.DISABLED)
        
        # Redraw PDA
        self.draw_pda()
    
    def process_automatically(self):
        if not self.processing:
            return
            
        # Process a step
        result = self.process_step()
        
        # Continue processing if not done
        if result == "continue":
            self.root.after(int(self.animation_speed * 1000), self.process_automatically)
    
    def step_forward(self):
        if not self.processing:
            return
            
        # Process just one step
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
                return "continue"
            else:
                # End of first phase, transition to q1
                self.current_state = "q1"
                self.input_position = 0  # Reset position to start checking palindrome
                self.draw_pda()
                return "continue"
        
        elif self.current_state == "q1":
            # Second phase: comparing input with stack (in reverse)
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
                stack_top = self.stack.pop()
                
                if current_char != stack_top:
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
                # End of second phase, check if stack is empty
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