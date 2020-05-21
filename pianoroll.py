import logging
from typing import Tuple

import pygame
from matplotlib import pyplot as plt


class Note:
    # Thickness of the rect
    thickness = 1920 // 88
    # Height of the rect per time step
    height = 5
    offset = 21

    def __init__(self, note_val: int):
        self.note_val = note_val
        self.pressed = False
        self.time = 0
        self.rects = list()

    def press(self, velocity=None):
        logging.debug(f">>> Pressed note {self.note_val}")
        self.pressed = True
        self.rects.append(Rect(self, velocity=velocity))

    def release(self):
        self.rects[-1].stop()
        logging.debug(
            f"<<< Released note {self.note_val} after {self.rects[-1].duration()}")
        self.pressed = False

    def toggle(self, velocity=None):
        if self.pressed:
            self.release()
        else:
            self.press(velocity=velocity)

    def tick(self, time: int, surface: pygame.Surface, height: int):
        self.time += time

        for rect_id, rect in enumerate(self.rects):
            if rect.stop_time is not None and (
                    Note.height * (self.time - rect.stop_time) > height):
                # Drop a rect if it is out of bounds
                popped = self.rects.pop(rect_id)
                logging.debug(f"Dropped rectangle {popped} at {self.time}")
            rect.draw(surface)


class Keyboard:

    def __init__(self):
        # Notes go from 21 (A at the left) to 108 (C at the right)
        self.notes = {i: Note(i) for i in range(Note.offset, Note.offset + 88)}
        self.fmtstr = len(self.notes) * "{}"

        self.control_keys = {
            # Speed of the piano roll
            "slower": 21,
            "faster": 22,
            "reset": 23
        }

    def __str__(self):
        return self.fmtstr.format(
            *["X" if note.pressed else "O" for note_val, note in
              self.notes.items()])

    def play_note(self, note_val: int, velocity=None):
        if note_val == self.control_keys["slower"]:
            if Note.height >= 1:
                Note.height -= 0.5
                logging.debug(f"Slower -> {Note.height}")
            else:
                logging.debug(f"Already at slowest speed -> {Note.height}")

        elif note_val == self.control_keys["faster"]:
            Note.height += 0.5
            logging.debug(f"Faster -> {Note.height}")
        elif note_val == self.control_keys["reset"]:
            Note.height = 5
            logging.debug(f"Reset -> {Note.height}")
        else:
            self.notes[note_val].toggle(velocity=velocity)
            logging.debug(f"Showing {len(self.get_rects())} rects.")

    def tick(self, time: int, surface: pygame.Surface, height: int):
        for note_val, note in self.notes.items():
            note.tick(time, surface, height)

    def get_rects(self):
        rects = list()
        for note_val, note in self.notes.items():
            rects.extend(note.rects)
        return rects


class Rect:
    def __init__(self, note: Note, velocity: int = None):
        self.note = note
        self.start_time = note.time
        self.stop_time = None
        self.left = None
        self.top = None
        self.width = None
        self.height = None
        self.velocity = velocity

    def stop(self):
        self.stop_time = self.note.time

    def duration(self):
        if self.stop_time is None:
            return self.note.time - self.start_time
        else:
            return self.stop_time - self.start_time

    def draw(self, surface: pygame.Surface):
        self.width = Note.thickness
        self.height = Note.height * self.duration()

        if self.stop_time is None:
            self.top = 0
        else:
            # TODO is it more fluent with move instead of redraw?
            self.top = Note.height * (self.note.time - self.stop_time)

        self.left = (self.note.note_val - Note.offset) * Note.thickness

        # Add some offset to not have the left most note at the border
        self.left += 50

        rect = pygame.Rect((self.left, self.top), (self.width, self.height))
        color = Rect.velocity_to_color(self.velocity)
        pygame.draw.rect(surface, color, rect)

    @staticmethod
    def velocity_to_color(velocity: int) -> Tuple[int, int, int]:
        if velocity is None:
            return (0, 0, 0)
        cm = plt.get_cmap("hot")
        color = cm(velocity / 127)[:-1]  # drop last channel (alpha)
        # Map to range 0-255
        color = tuple(int(255 * i) for i in color)
        return color

    def __str__(self):
        return f"Note: {self.note.note_val}, start: {self.start_time}, stop: {self.stop_time}, duration: {self.duration()}" \
               f"{(self.left, self.top), (self.width, self.height)}"

    def __repr__(self):
        return str(self)
