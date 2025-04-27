"""
Problem Statement:
    - Design a memory allocator using the Buddy System technique.
    - Your allocator should support:
        - allocate(size: int) -> int
            - Allocate a block of at least size units.
            - Allocations must happen in blocks of size power of 2 (e.g., 2, 4, 8, 16, 32, 64...).
            - Find the smallest block of power 2 that fits the request.
            - If no suitable block is available, return -1.

        - free(ptr: int) -> bool
            - Free the block starting at address ptr.
            - After freeing, if the "buddy block" (adjacent block of same size) is also free, merge the two into a larger block automatically.
            - This merging continues recursively upwards if possible.

    - Constraints:
        - Total memory size is 1024 units (fixed).
        - All allocations must be in power of 2 sizes only.
        - Blocks are merged only if they are buddies (blocks of same size)
        - Memory is linear (simple 0 to 1023 address space).

Approach I: (Not using buddy to its full extent.) 
    - Initially memory space = 1024 i.e. 2^10
    - available_memory = {0: 1024}
    - allocate(500) [512 space min to be assigned i.e. 2^5] # Advantage of this ?? (This will cause internal fragmentation.)
        - {512: 512}
    - occupied_memory = {0: 512} # Used while freeing up memory.

    - Dry run:
        - A(500) -> Occupied({0: 512}), Available({512: 512})
        - A(200) -> Occupied({0: 512, 512: 206}), Available({718: 206})
        - F(0) -> Occupied({512: 206}), Available({0:512, 718: 206})
        - F(512) -> Occupied({}), Available({0: 512, 512: 206, 718: 206}) 
                                        --> coalese({0:1024})

    - Available memory should be stored in sorted order based on keys i.e. starting index of available memory 
      to easily perform coalesing between buddies by checking next and prev block of available and recursively 
      performing same merge operation until possible.

    - available_memory: SortedDict
    - occupied_memory: dict

Approach II: 
    - Initial memory space = 1024 (2^10)
    - allocate()
        - Assign memory in power of 2.
        - If available memory greater than required memory, preemptively split the memory space until no further
          split can take place.
        - Algo: Best fit. (Select the smallest possible memory that can be assigned.)
    - free()
        - Check if pointer belongs to starting pointer of memory clean up the space.
        - Else return error incorrect pointer.

    - Coalesce the buddies to store contiguos block of free space as 1 large free block.
    - Buddies can be found using starting address and block size.
        - buddy address = current address ^ block size
        - If buddy address present in free/available space, then merge (recursively perform same operation until all buddies are merged.)
    
"""
import math

class BuddyMemoryAllocator:
    def __init__(self, size):
        self.max_bit = self._get_next_exponent_power_of_two(size)
        self.size = pow(2, self.max_bit)
        self.available_spaces = self._initialize_available_space()
        self.occupied_spaces = {}

    def _initialize_available_space(self):        
        # Initially entire block is available starting from 0 index.
        available_spaces = [[] for _ in range(self.max_bit+1)]
        available_spaces[self.max_bit].append(0)

        return available_spaces

    def _get_next_exponent_power_of_two(self, val):
        return math.ceil(math.log(val, 2)) 

    def _merge_buddies(self, starting_index, exponent):
        block_size = pow(2, exponent)
        buddy_index = starting_index ^ block_size
        if buddy_index in self.available_spaces[exponent]:
            # Merge the 2 blocks.
            self.available_spaces[exponent].remove(starting_index)
            self.available_spaces[exponent].remove(buddy_index)

            # Insert in next block in power of 2s
            self.available_spaces[exponent+1].append(min(starting_index, buddy_index))

            # recursively check if any buddy exist for newly merged block of memory
            self._merge_buddies(min(starting_index, buddy_index), exponent+1)

    def allocate(self, size):
        desired_exponent = self._get_next_exponent_power_of_two(size)

        exponent = desired_exponent
        # Try assigning space starting from min space required to max available (best-fit)
        while exponent <= self.max_bit:
            if len(self.available_spaces[exponent]):
                break
            exponent += 1
        
        if exponent > self.max_bit:
            raise ValueError("No space left. Please cleanup some space.")
        
        # Split memory in power of 2s if space present greater than required size.
        while exponent > desired_exponent:
            starting_index = self.available_spaces[exponent].pop()
            self.available_spaces[exponent-1].append(starting_index)
            self.available_spaces[exponent-1].append(starting_index + pow(2,exponent-1))
            exponent -= 1
        
        starting_index = self.available_spaces[exponent].pop()
        self.occupied_spaces[starting_index] = pow(2, exponent)
        return starting_index

    def free(self, ptr):
        if ptr not in self.occupied_spaces:
            raise ValueError("Invalid ptr to free.")
    
        occupied_size = self.occupied_spaces[ptr]
        exponent = self._get_next_exponent_power_of_two(occupied_size)
        
        # Insert available space in available map and free up from occupied map.
        self.available_spaces[exponent].append(ptr)
        del self.occupied_spaces[ptr]

        # Coalesce the buddies. Perform merge to form 1 large block of available memory rather than 2 smaller contiguos blocks.
        self._merge_buddies(ptr, exponent)


######## TESTING #################
allocator = BuddyMemoryAllocator(1024)

# Allocate a block of 100 units
ptr1 = allocator.allocate(100)
print(f"Allocated 100 units at address: {ptr1}")

# Allocate another block of 200 units
ptr2 = allocator.allocate(200)
print(f"Allocated 200 units at address: {ptr2}")

# Free the first block
allocator.free(ptr1)
print(f"Freed block at address: {ptr1}")

# Free the second block
allocator.free(ptr2)
print(f"Freed block at address: {ptr2}")

# Now allocate 512 units
ptr3 = allocator.allocate(512)
print(f"Allocated 512 units at address: {ptr3}")

# Final: Free 512 units
allocator.free(ptr3)
print(f"Freed block at address: {ptr3}")
