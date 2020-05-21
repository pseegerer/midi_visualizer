import logging
import sys

import click
import mido
import pygame

from pianoroll import Keyboard


@click.command()
@click.option("-s", "--size", default=(2400, 1200), help="Window size")
@click.option("-i", "--input_port",
              default="USB MIDI Interface:USB MIDI Interface MIDI 1 20:0",
              help="Name of the MIDI input port. Get available ports with "
                   "`mido.get_input_names()`.")
@click.option("--background", default=(255, 255, 255),
              help="Background color in RGB.")
@click.option("--sleep_after", default=30,
              help="Time steps without input after which the roll is stopped.")
@click.option("--caption", default="MIDI Visualizer", help="Window title")
@click.option("--debug", is_flag=True, help="Print debugging info.")
def main(size, input_port, background, sleep_after, caption, debug):
    if debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        inport = mido.open_input(input_port)
    except OSError:
        raise OSError(
            f"Unknown port '{input_port}'. Available ports are {mido.get_input_names()}")

    # ** PyGame config
    width, height = size
    # Time increment
    delta_t = 1

    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()

    keyboard = Keyboard()
    time = 0
    time_since_last = 0
    while True:
        clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(background)

        curr_message = inport.receive(block=False)

        if curr_message is not None:
            logging.debug(f"Received {curr_message}")

            if time_since_last >= curr_message.time:
                if not curr_message.is_meta:
                    if hasattr(curr_message, "note"):
                        keyboard.play_note(curr_message.note,
                                           velocity=curr_message.velocity)

                time_since_last = 0

                # Continue without time increment because there might be more
                # messages at the same time
                continue

        # Stop rolling if no input for a while and no note is pressed
        if time_since_last < sleep_after or any(
                (note.pressed for _, note in keyboard.notes.items())):
            time += delta_t
            time_since_last += delta_t
            keyboard.tick(delta_t, screen, height)
            pygame.display.flip()


if __name__ == '__main__':
    main()
