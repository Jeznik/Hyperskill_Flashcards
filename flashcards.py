import json
import sys
import io
from itertools import cycle

# class Flashcard:
#     def __init__(self, name, definition):
#         self.name = name
#         self.definition = definition

    # def check_definition(self, guess):
    #     return guess == self.definition

class Deck:
    def __init__(self):
        self.cards = {}

    def add_card(self, card, definition):
        self.cards[card] = {"definition": definition, "mistakes": 0}
        print(f'The pair ("{card}":"{definition}") has been added.')

    def term_exists(self, term):
        return term in self.cards

    def definition_exists(self, definition):
        for name, data in self.cards.items():
            if data["definition"] == definition:
                return name
        return None

    def remove_card(self, name):
        if name in self.cards:
            del self.cards[name]
            print("The card has been removed.")
        else:
            print(f'Can\'t remove "{name}": there is no such card.')

class Tee:
    """Duplicates writes to multiple streams."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


class SessionLogger:
    def __init__(self):
        # In‑memory transcript
        self.buffer = io.StringIO()

        # Keep a reference to the real console stdout
        self.console = sys.__stdout__

        # Create a Tee that writes to console AND buffer
        self.tee = Tee(self.console, self.buffer)

        # Redirect stdout globally
        sys.stdout = self.tee

    def input(self, prompt=None):
        """Capture user input, with or without a prompt."""
        if prompt is None:
            value = input()
        else:
            value = input(prompt)

        # Log what the user typed
        self.buffer.write(f"{value}\n")
        return value

    def save(self, filename="session.txt"):
        """Save the entire transcript to a file."""
        with open(filename, "w") as f:
            f.write(self.buffer.getvalue())
        print(f"Transcript saved to {filename}")

    def get_transcript(self):
        """Optional: return the transcript as a string."""
        return self.buffer.getvalue()


def main():
    logger = SessionLogger()
    deck = Deck()
    while True:
        print("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats)")
        action = logger.input()

        if action not in ("add", "remove", "import", "export", "ask", "exit", "log", "hardest card", "reset stats"):
            print("Unknown command")
            continue

        if action == "exit":
            print("Bye bye!")
            break

        if action == "add":
            print(f"The card:")
            while True:
                card = logger.input()
                if not deck.term_exists(card):
                    break
                else:
                    print(f'The card "{card}" already exists. Try again:')
            print("The definition of the card:")
            while True:
                definition = logger.input()
                if not deck.definition_exists(definition):
                    break
                else:
                    print(f'The definition "{definition}" already exists. Try again:')
            deck.add_card(card, definition)
            continue

        if action == "remove":
            print("Which card?")
            card_to_remove = logger.input()
            deck.remove_card(card_to_remove)
            continue

        if action == "ask":
            while True:
                print("How many times to ask?")
                try:
                    questions_number = int(logger.input())
                    break
                except ValueError:
                    print("Invalid input. Try again:")

            # Use .items() to get (key, value) pairs
            iter_deck = cycle(deck.cards.items())
            for i in range(questions_number):
                # card will now be a tuple: (name, definition)
                card_name, card_definition = next(iter_deck)
                #card = deck.cards[i]
                print(f'Print the definition of "{card_name}":')
                guess = logger.input()
                if guess == card_definition:
                    print('Correct!')
                else:
                    deck.cards[card_name]["mistakes"] += 1
                    existing_card = deck.definition_exists(guess)
                    if existing_card:
                        print(
                            f'Wrong. The right answer is "{card_definition}", but your definition is correct for "{existing_card}".')
                    else:
                        print(f'Wrong. The right answer is "{card_definition}".')
            continue

        if action == "export":
            print("File name:")
            file_name = logger.input()
            try:
                with open(file_name, "w") as file:
                    json.dump(deck.cards, file)
                print(f"{len(deck.cards)} cards have been saved.")
            except Exception as e:
                print(f"An error occurred while saving: {e}")
            continue

        if action == "import":
            print("File name:")
            file_name = logger.input()
            try:
                with open(file_name, "r") as file:
                    cards_to_import = json.load(file)
                    deck.cards.update(cards_to_import)
                    print(f"{len(cards_to_import)} cards have been loaded.")
            except FileNotFoundError:
                print("File not found.")
            except Exception as e:
                print(f"An error occurred while loading: {e}")
            continue

        if action == "log":
            print("File name:")
            file_name = logger.input()
            logger.save(filename=file_name)
            continue

        # TODO: Finish off these two options
        if action == "hardest card":
            # print(f"The hardest card is: {max(deck.cards.items(), key=lambda x: x[1]['mistakes'])[0]}")
            continue

        if action == "reset stats":
            for card in deck.cards.values():
                card["mistakes"] = 0
            continue


if __name__ == "__main__":
    main()