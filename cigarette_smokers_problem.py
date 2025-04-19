"""
Problem:

There are:
    - One agent
    - Three smokers
        - Each smoker has one of the three ingredients needed to roll a cigarette:
            - Smoker A has tobacco
            - Smoker B has paper
            - Smoker C has matches
    
The agent randomly places two of the three ingredients on the table.
Rules:
    - The smoker who has the third missing ingredient (the one not placed on the 
      table) picks up the two ingredients, makes a cigarette, and smokes.

Note: Agent doesn't wait for smokers to complete smoking. Add another condition variable to sync this as well later.
Approach
    - Agent Thread
    - Three Smoker threads:
        Smoker: (id, ingredient)
    - new_items_on_table: Condition Variable (notifies smokers if new ingredients added on table)

"""
from threading  import Thread, Condition, Lock
from enum       import Enum
import time
import random

class Ingredient(Enum):
    TOBACCO = 1
    PAPER = 2
    MATCHES = 3

class SmokingTable:
    def __init__(self):
        self.lock = Lock()
        self.new_items_on_table = Condition(self.lock)
        self.ingredients_on_table = []
    
    def put_ingredients(self, ingredient_1, ingredient_2):
        with self.new_items_on_table:
            self.ingredients_on_table = [ingredient_1, ingredient_2]
            self.new_items_on_table.notify_all()


class Smoker(Thread):
    def __init__(self, name, ingredient, smoking_table: SmokingTable):
        super().__init__()
        self.name = name
        self.ingredient = ingredient
        self.table = smoking_table
    
    def smoke(self):
        for _ in range(2):
            with self.table.new_items_on_table:
                while len(self.table.ingredients_on_table) < 2:
                    self.table.new_items_on_table.wait()

                while self.ingredient in self.table.ingredients_on_table:
                    self.table.new_items_on_table.wait()

                # Take all ingrdients and smoke
                print(f"Thread {self.name} is smoking with ingredient {self.ingredient}")
                time.sleep(random.uniform(0.5, 1))
    
    def run(self):
        self.smoke()

class Agent(Thread):
    def __init__(self, smoking_table:SmokingTable):
        super().__init__()
        self.smoking_table = smoking_table
    
    def put_ingredients(self):
        ingredient_1, ingredient_2 = random.sample(list(Ingredient), k=2)
        print(f"Placing {ingredient_1} and {ingredient_2} on table")
        self.smoking_table.put_ingredients(ingredient_1, ingredient_2)
    
    def run(self):
        for _ in range(5):
            time.sleep(2)
            self.put_ingredients()


smoking_tbl = SmokingTable()
agent = Agent(smoking_tbl)
smokers = [Smoker(name, ingredient, smoking_tbl)  for (name, ingredient) in [("A", Ingredient.TOBACCO), 
                                                                             ("B", Ingredient.MATCHES),
                                                                          ("C", Ingredient.PAPER)]]

for thread in smokers + [agent]:
    thread.start()

for thread in smokers + [agent]:
    thread.join()
