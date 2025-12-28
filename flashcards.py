import json
import io
from itertools import cycle

class Deck:
    def __init__(self):
        self.cards = {}

    def add_card(self, card, definition, logger):
        self.cards[card] = {"definition": definition, "mistakes": 0}
        logger.log_print(f'The pair ("{card}":"{definition}") has been added.')

    def term_exists(self, term):
        return term in self.cards

    def definition_exists(self, definition):
        for name, data in self.cards.items():
            if data["definition"] == definition:
                return name
        return None

    def remove_card(self, name, logger):
        if name in self.cards:
            del self.cards[name]
            logger.log_print("The card has been removed.")
        else:
            logger.log_print(f'Can\'t remove "{name}": there is no such card.')

class SessionLogger:
    def __init__(self):
        self.buffer = io.StringIO()

    def log_print(self, message, end='\n'):
        """Prints to console and saves to buffer."""
        print(message, end=end)
        self.buffer.write(f"{message}{end}")

    def log_input(self, prompt=None):
        """Prints prompt (if any), takes input, and logs both."""
        if prompt:
            self.log_print(prompt)
        
        value = input()
        self.buffer.write(f"{value}\n")
        return value

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.buffer.getvalue())
        self.log_print("The log has been saved.")

def main():
    logger = SessionLogger()
    deck = Deck()
    while True:
        action = logger.log_input("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")

        if action == "exit":
            logger.log_print("Bye bye!")
            break

        if action == "add":
            logger.log_print("The card:")
            while True:
                card = logger.log_input()
                if not deck.term_exists(card):
                    break
                else:
                    logger.log_print(f'The card "{card}" already exists. Try again:')
            
            logger.log_print("The definition of the card:")
            while True:
                definition = logger.log_input()
                if not deck.definition_exists(definition):
                    break
                else:
                    logger.log_print(f'The definition "{definition}" already exists. Try again:')
            deck.add_card(card, definition, logger)

        elif action == "remove":
            logger.log_print("Which card?")
            card_to_remove = logger.log_input()
            deck.remove_card(card_to_remove, logger)

        elif action == "ask":
            logger.log_print("How many times to ask?")
            try:
                line = logger.log_input()
                questions_number = int(line)
            except ValueError:
                continue

            iter_deck = cycle(deck.cards.items())
            for _ in range(questions_number):
                card_name, card_data = next(iter_deck)
                card_definition = card_data["definition"]
                
                logger.log_print(f'Print the definition of "{card_name}":')
                guess = logger.log_input()
                
                if guess == card_definition:
                    logger.log_print('Correct!')
                else:
                    deck.cards[card_name]["mistakes"] += 1
                    existing_card = deck.definition_exists(guess)
                    if existing_card:
                        logger.log_print(f'Wrong. The right answer is "{card_definition}", but your definition is correct for "{existing_card}".')
                    else:
                        logger.log_print(f'Wrong. The right answer is "{card_definition}".')

        elif action == "export":
            logger.log_print("File name:")
            file_name = logger.log_input()
            with open(file_name, "w") as file:
                json.dump(deck.cards, file)
            logger.log_print(f"{len(deck.cards)} cards have been saved.")

        elif action == "import":
            logger.log_print("File name:")
            file_name = logger.log_input()
            try:
                with open(file_name, "r") as file:
                    cards_to_import = json.load(file)
                    deck.cards.update(cards_to_import)
                    logger.log_print(f"{len(cards_to_import)} cards have been loaded.")
            except FileNotFoundError:
                logger.log_print("File not found.")

        elif action == "log":
            logger.log_print("File name:")
            file_name = logger.log_input()
            logger.save(file_name)

        elif action == "hardest card":
            if not deck.cards:
                logger.log_print("There are no cards with errors.")
                continue

            max_mistakes = max(card_data['mistakes'] for card_data in deck.cards.values())
            if max_mistakes == 0:
                logger.log_print("There are no cards with errors.")
            else:
                hardest_cards = [term for term, data in deck.cards.items() if data['mistakes'] == max_mistakes]
                if len(hardest_cards) == 1:
                    logger.log_print(f'The hardest card is "{hardest_cards[0]}". You have {max_mistakes} errors answering it.')
                else:
                    cards_str = ", ".join(f'"{c}"' for c in hardest_cards)
                    logger.log_print(f'The hardest cards are {cards_str}. You have {max_mistakes} errors answering them.')

        elif action == "reset stats":
            for card in deck.cards.values():
                card["mistakes"] = 0
            logger.log_print("Card statistics have been reset.")

if __name__ == "__main__":
    main()