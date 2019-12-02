#!/usr/bin/env python3
"""
A back-to-front snakey toy

Copyright (C) 2019, https://github.com/4gra/launchpad.py
Based entirely on lovely work of https://github.com/FMMT666/launchpad.py

This program comes with ABSOLUTELY NO WARRANTY; for details see included LICENCE.
This is free software, and you are welcome to redistribute it under certain
conditions; view the included file LICENCE for details.
"""
from launchpad_py.utils import *
import random
from time import sleep
from collections import deque


def neighbours(x, y):
    """
    within 0 <= x <= 7 and 1 <= y <= 8 return neighbouring squares
    [x-1, y-1] [x, y-1] [x+1, y-1]
    [x-1, y]   [x, y]   [x+1, y]
    [x-1, y+1] [x, y+1] [x+1, y+1]
    """
    neigh = []
    for (nx, ny) in [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]:
        if 0 <= nx <= 7 and 1 <= ny <= 8:
            neigh += [(nx, ny)]
    return neigh


class Snake:
    """
    This is a game for ����
    love from �����
    """
    field_colour = 0, 1
    food_colour = 2, 2
    head_colour = 3, 0
    tail_colour = 2, 0

    def __init__(self, lp):
        #self.head = 4, 2  # position of the head of the snake
        #self.tail = deque([(3, 2), (2, 2), (1, 2), (0, 2)])
        self.head = random.choice(
            [(x, y) for x in range(0, 7) for y in range(1, 8)]
        )
        self.prev = []
        self.tail = deque()
        self.starting_length = 6
        self.food = []
        self.lp = lp

    def __len__(self):
        return len(self.tail) + 1

    def pixels(self):
        return [self.head] + list(self.tail)

    def paint(self):
        for pos in self.food:
            self.lp.LedCtrlXY(*pos, *self.food_colour)
        for pos in [p for p in self.prev if p not in self.tail]:
            self.lp.LedCtrlXY(*pos, *self.field_colour)
        for pos in self.tail:
            self.lp.LedCtrlXY(*pos, *self.tail_colour)
        for pos in [self.head]:
            self.lp.LedCtrlXY(*pos, *self.head_colour)

    def place_food(self, x, y):
        if (x, y) not in self.pixels():
            self.food += [(x, y)]

    def eat(self):
        """
        eat food under the snake's head
        """
        self.food.pop(
            self.food.index(self.head)
        )

    def move(self, x, y):
        """
        moves the snake's head to a new location
        this will teleport a 1-length snake to (x,y) if the move is infeasible
        """
        self.prev = self.pixels()
        self.tail.append(self.head)
        if len(self) > self.starting_length:
            self.tail.popleft()
        # moved
        self.head = x, y
        if self.head in self.food:
            self.eat()

    def possible_moves(self, x, y):
        return [pos for pos in neighbours(x,y) if pos not in self.pixels()[1:]]

    def random_move(self):
        """
        Move randomly.  The minimal lookahead will work indefinitely for a
        snake of length <= 6
        """
        self.prev = self.pixels()
        self.tail.append(self.head)
        if len(self) > self.starting_length:
            self.tail.popleft()
        # generate new head position choices TODO: do this first and have 'stay still' as a choice
        new_heads = [pos for pos in neighbours(*self.head) if pos not in self.tail]
        # lookahead one move, that's really all that's required
        # we should just special-case the corners but this worked in a pinch
        if len(new_heads) == 2:
            new_heads = [h for h in new_heads if len(neighbours(*h)) != 2]
        #print("Choices are {}, having excluded {}".format(new_heads, self.tail))
        self.head = random.choice(list(new_heads))
        if self.head in self.food:
            self.eat()


def game_loop():
    with LaunchpadPlease(emulate=None) as lp:
        snake = Snake(lp)
        fill(lp, *snake.field_colour)
        while True:
            snake.random_move()
            snake.paint()
            sleep(0.09)

            # process all buttons in one go
            if lp.ButtonChanged():
                while True:
                    try:
                        (x, y, pressed) = lp.ButtonStateXY()  # raises ValueError when state is None
                        print("+" if pressed else "-", x, y)
                        if pressed:
                            snake.place_food(x, y)
                    except ValueError:  # when state == None
                        break


if __name__ == '__main__':
    game_loop()
