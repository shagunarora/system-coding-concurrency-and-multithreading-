"""
Prompt: Implement a class MemoryAllocator which supports the following operations:
    - allocate(size: int) -> int: Allocate a contiguous memory block of size units 
                                  and return the starting index. If memory is full, 
                                  return -1.

    - free(ptr: int): Free the memory block starting at index ptr.

Constraints:
    - The memory is a linear array of size N (you can assume N=1000 for simplicity).
    - allocate should always allocate the first-fit block (i.e., leftmost available space).
    - All memory blocks are non-overlapping.
    - Freeing a block makes that part of memory available again.

Approach:
    - [ _ _ x x x _ _ _ _ x x]
    - {0: 2, 5: 4} [Map of starting index to available space --> This will help in allocation]

    - free up memory  (index --> starting index)
        - map of occupied memory:
            - {2: 3, 9: 2} --> {9:2}
            - Update available space map --> {0:2, 2: 3, 5: 4} --> {0: 9}

    
    - Maintain 2 maps:
        - Map of index to available spaces
        - Map of index to occupied spaces.
    
        - Allocate:
            - Traverse in available spaces (since need to assign using first fit memory space)
                - Check if memory available >= required memory
                - If yes, then remove the available space from the map and return starting index.
                    - Remove the avialable space: 
                        {starting_index: space_available} --> {starting_index + required_space: space_available - required_space} 
                    
                    - Add this new to-be allocated memory in occupied spaces:
                        - {starting_index: required_space}
                    
                    - return starting index

        - Free (index):
            - Check if index present in occupied memory, if yes then remove it from occupied memory
            - Insert the index: space_value in available spaces.
                - Since multiple small intervals can join to form one free block of memory, perform
                  a merge operation to ensure there are no multiple indexes belonging to same block of memory.

            - return acknowledgement (True/False)

    - (Note: Available spaces should be sorted based on key)

"""

from sortedcontainers import SortedDict

class MemoryAllocator:
    def __init__(self, memory_size):
        self.available_memory = SortedDict({0: memory_size})
        self.occupied_memory = {}
    
    def _merge_available_spaces(self):
        if len(self.available_memory) <= 1:
            return

        curr_index = 0
        next_index = 1

        while curr_index < (len(self.available_memory)-1):
            starting_memory_index, memory_available = self.available_memory.peekitem(curr_index)
            next_starting_memory_index, next_memory_available_size = self.available_memory.peekitem(next_index)
            if starting_memory_index + memory_available == next_starting_memory_index:
                # Since these are continuos block of memory, we should have only one item in available memory dict.
                self.available_memory[starting_memory_index] = memory_available + next_memory_available_size
                self.available_memory.pop(next_starting_memory_index)
                continue
        
            curr_index += 1
            next_index += 1

    def allocate(self, size):
        """
        Allocate memory of size "size" if available based on first-fit
        algo.
        """
        for starting_index, space in self.available_memory.items():
            if space >= size:
                # Remove the space from available spaces, this required space will be allocated to 
                # the user.
                self.available_memory.pop(starting_index)
                if space - size > 0:
                    # insert remiaing available space in the map
                    self.available_memory[starting_index + size] = space - size
                
                # Add the allocated memory index and space in occupied memory
                self.occupied_memory[starting_index] = size
            
                return starting_index
            
        print("No space(memory) available. Please free up some memory.")
        return -1
    
    def free(self, ptr):
        if ptr not in self.occupied_memory:
            raise ValueError(f"Invalid free pointer: {ptr}")

        occupied_space = self.occupied_memory.pop(ptr)

        # Insert the now available space in availble space map.
        self.available_memory[ptr] = occupied_space
        self._merge_available_spaces()

        return True
