import json
import io
import random

class Deck:
    def __init__(self):
        self.cards = {}

    def add_card(self, term, definition):
        self.cards[term] = {"definition": definition, "mistakes": 0}

    def remove_card(self, term):
        if term in self.cards:
            del self.cards[term]
            return True
        return False

    def get_hardest_cards(self):
        if not self.cards:
            return [], 0
        max_mistakes = max(data['mistakes'] for data in self.cards.values())
        if max_mistakes == 0:
            return [], 0
        hardest = [term for term, data in self.cards.items() if data['mistakes'] == max_mistakes]
        return hardest, max_mistakes

class SessionLogger:
    def __init__(self):
        self.buffer = io.StringIO()

    def log_print(self, message="", end='\n'):
        print(message, end=end)
        self.buffer.write(f"{message}{end}")

    def log_input(self, prompt=None):
        if prompt:
            self.log_print(prompt)
        value = input()
        self.buffer.write(f"{value}\n")
        return value

    def save(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.buffer.getvalue())

class FlashcardApp:
    def __init__(self):
        self.deck = Deck()
        self.logger = SessionLogger()

    def run(self):
        while True:
            action = self.logger.log_input("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
            
            if action == "exit":
                self.logger.log_print("Bye bye!")
                break
            elif action == "add":
                self.add_action()
            elif action == "remove":
                self.remove_action()
            elif action == "import":
                self.import_action()
            elif action == "export":
                self.export_action()
            elif action == "ask":
                self.ask_action()
            elif action == "log":
                self.log_action()
            elif action == "hardest card":
                self.hardest_card_action()
            elif action == "reset stats":
                self.reset_stats_action()

    def add_action(self):
        self.logger.log_print("The card:")
        while True:
            term = self.logger.log_input()
            if term not in self.deck.cards:
                break
            self.logger.log_print(f'The card "{term}" already exists. Try again:')
        
        self.logger.log_print("The definition of the card:")
        while True:
            definition = self.logger.log_input()
            if all(d["definition"] != definition for d in self.deck.cards.values()):
                break
            self.logger.log_print(f'The definition "{definition}" already exists. Try again:')
        
        self.deck.add_card(term, definition)
        self.logger.log_print(f'The pair ("{term}":"{definition}") has been added.')

    def remove_action(self):
        self.logger.log_print("Which card?")
        term = self.logger.log_input()
        if self.deck.remove_card(term):
            self.logger.log_print("The card has been removed.")
        else:
            self.logger.log_print(f'Can\'t remove "{term}": there is no such card.')

    def ask_action(self):
        self.logger.log_print("How many times to ask?")
        try:
            times = int(self.logger.log_input())
        except ValueError:
            return

        # Note: The test hints at randomness. Using random.choice or similar 
        # is usually expected if you aren't cycling.
        card_list = list(self.deck.cards.items())
        for _ in range(times):
            term, data = random.choice(card_list)
            self.logger.log_print(f'Print the definition of "{term}":')
            guess = self.logger.log_input()
            
            if guess == data["definition"]:
                self.logger.log_print("Correct!")
            else:
                data["mistakes"] += 1
                # Check if it matches another card's definition
                other_term = next((t for t, d in self.deck.cards.items() if d["definition"] == guess), None)
                if other_term:
                    self.logger.log_print(f'Wrong. The right answer is "{data["definition"]}", but your definition is correct for "{other_term}".')
                else:
                    self.logger.log_print(f'Wrong. The right answer is "{data["definition"]}".')

    def export_action(self):
        self.logger.log_print("File name:")
        filename = self.logger.log_input()
        with open(filename, "w") as f:
            json.dump(self.deck.cards, f)
        self.logger.log_print(f"{len(self.deck.cards)} cards have been saved.")

    def import_action(self):
        self.logger.log_print("File name:")
        filename = self.logger.log_input()
        try:
            with open(filename, "r") as f:
                new_cards = json.load(f)
                self.deck.cards.update(new_cards)
                self.logger.log_print(f"{len(new_cards)} cards have been loaded.")
        except FileNotFoundError:
            self.logger.log_print("File not found.")

    def hardest_card_action(self):
        hardest, count = self.deck.get_hardest_cards()
        if not hardest:
            self.logger.log_print("There are no cards with errors.")
        elif len(hardest) == 1:
            self.logger.log_print(f'The hardest card is "{hardest[0]}". You have {count} errors answering it.')
        else:
            cards_str = ", ".join(f'"{c}"' for c in hardest)
            self.logger.log_print(f'The hardest cards are {cards_str}. You have {count} errors answering them.')

    def reset_stats_action(self):
        for data in self.deck.cards.values():
            data["mistakes"] = 0
        self.logger.log_print("Card statistics have been reset.")

    def log_action(self):
        self.logger.log_print("File name:")
        filename = self.logger.log_input()
        self.logger.save(filename)
        self.logger.log_print("The log has been saved.")

def main():
    app = FlashcardApp()
    app.run()

if __name__ == "__main__":
    main()