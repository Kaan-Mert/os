# core/process.py

class Process:
    """Represents a Process Control Block (PCB) in the Game Console OS simulator."""
    
    def __init__(self, pid, name, arrival_time, burst_time, priority, memory_required):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority             # 1: High (Game Engine), 2: Medium (Audio/UI), 3: Low (Background Download)
        self.original_priority = priority    # For Priority Inheritance Protocol (PIP)
        self.memory_required = memory_required  # Memory required in MB
        
        # Address Space
        self.page_table = {}                 # Page Table (virtual page -> physical frame)
        self.segment_table = {}              # Segment Table (segment_id -> (base, limit, type))
        self.file_handles = []               # List of currently open files
        
        self.reset()

    def reset(self):
        self.remaining_time = self.burst_time
        self.state = "READY"                 # READY, RUNNING, BLOCKED, COMPLETED
        self.queue_level = 0                 # For MLFQ (0, 1, 2)
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.end_time = None
        self.execution_intervals = []        # Track execution intervals for Gantt charts: [[start, end], ...]
        self.blocked_reason = None           # Tracks resource name or disk operation blocking the process
        self.page_faults_count = 0

    def transition_to(self, new_state, reason=None):
        """Manages state transitions and sets blocked reason if applicable."""
        valid_states = {"READY", "RUNNING", "BLOCKED", "COMPLETED"}
        if new_state not in valid_states:
            raise ValueError(f"Invalid process state: {new_state}")
        self.state = new_state
        self.blocked_reason = reason if new_state == "BLOCKED" else None

    def add_execution_interval(self, start, end):
        """Helper to append or update execution intervals for plotting."""
        if self.execution_intervals and self.execution_intervals[-1][1] == start:
            self.execution_intervals[-1][1] = end
        else:
            self.execution_intervals.append([start, end])

    def __repr__(self):
        return f"Process(PID={self.pid}, Name='{self.name}', State={self.state}, Prio={self.priority}, Remaining={self.remaining_time})"
