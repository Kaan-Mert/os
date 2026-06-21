# memory/paging.py

class PagingSystem:
    """Simulates a Paging memory system (Module 5) with page lookup and translation."""
    
    def __init__(self, page_size_kb=4):
        self.page_size = page_size_kb * 1024  # Size in bytes
        
    def initialize_page_table(self, process):
        """Initializes an empty page table mapping for a process."""
        process.page_table = {}  # page_number -> frame_number

    def map_page(self, process, page_number, frame_number):
        """Maps a process's virtual page number to a physical frame number."""
        process.page_table[page_number] = frame_number

    def lookup(self, process, page_number):
        """Checks if a page number is currently present in the process's page table.
        Returns the frame number if found (Hit), or None (Page Fault/Miss).
        """
        if page_number in process.page_table:
            return process.page_table[page_number]
        return None

    def translate(self, process, logical_address):
        """Translates a logical address into page number, offset, and looks up the frame."""
        page_number = logical_address // self.page_size
        offset = logical_address % self.page_size
        
        frame_number = self.lookup(process, page_number)
        
        if frame_number is not None:
            physical_address = (frame_number * self.page_size) + offset
            return {
                "success": True,
                "page_number": page_number,
                "frame_number": frame_number,
                "offset": offset,
                "physical_address": physical_address
            }
        else:
            return {
                "success": False,
                "page_number": page_number,
                "offset": offset,
                "reason": "PAGE FAULT (Page not in memory)"
            }
