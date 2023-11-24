'''
How to organize this?
Player class just holds player data and functions are public
dealer is a special player class

or

Player class holds all relevant player info and contains methods
for player to interact with the game

---UPDATE---
Organized as such:
CardDeck is own contained class
Dealer controls the deck object (as in real life)
Players share a dealer object to request dealer methods


--STILL TO COME--
'Play' function, dictates the structure of the game/method calls
splits
insurance
double down
bet payouts

UUUUGGGGHHHHHHHHHH! Create a hand class. It will ultimately be the easiest way to
work with all scenarios of play. Much easier than storing cards and totals as 
arrays of arrays of arrays of arrays of arrays....
might involve changing less code than I think. 

maybe a bank for each player?


'''

import random

class CardDeck():

    def __init__(self, num_decks = 1) -> None:
        self.deck = [(x,y) for x in ["\u2663", "\u2665", "\u2666", "\u2660"] for y in ([z for z in range(2,11)] + ['J', 'Q', 'K', 'A'])]
        self.deck *= num_decks
        random.shuffle(self.deck)

    def draw_card(self):
        return self.deck.pop()
    
class Hand():

    def __init__(self) -> None:
        self.cards = []
        self.total = [0]
        self.stand = False
        self.blackjack = False
        self.bust = False

    def calc_total(self):
        # re-work this to handle split hands appropriately. Looks like I need to confine each hand to
        # a list element inside self.total, should be a list of lists with each element correspoinding to
        # its hand in self.cards
        self.total = [0]
        for _, card in self.cards:
            if str(card) in 'JQK':
                self.total = list(map(lambda x: x+10, self.total))
            elif str(card) == 'A':
                temp = self.total[:]
                self.total = list(map(lambda x: x+1, self.total))
                temp = list(map(lambda x: x+11, temp))
                self.total.extend(temp)
                self.total = list(filter(lambda x : x < 22, self.total))
            else:
                self.total = list(map(lambda x: x + card, self.total))
        
        if min(self.total) > 21:
            self.bust = True
            self.stand = True
        elif 21 in self.total:
            self.blackjack = True
            self.stand = True

class Player():

    def __init__(self, dealer = None) -> None:
        self.bet = -1
        self.dealer = dealer
        self.hand = [Hand()]

    def place_bet(self):
        valid = False
        while valid == False:
            valid = True
            wager = input('How much would you like to bet? ')
            if not wager.isdigit():
                valid = False
            elif int(wager) > 200:
                valid = False
                print("Wagers cannot exceed $200 at this table")
        self.bet = int(wager)
    
    def take_card(self, card: tuple, hand_index: int = 0):   # Player should always be passed a card
        '''
            take_card adds a card to the player's hand

            card: expected to be a tuple of (suit, value)
            hand_index: should be an integer, defines which hand is being altered
                in the case of a split hand. Default value is zero
        '''
        self.hand[hand_index].cards.append(card)
        self.hand[hand_index].calc_total()

    def check_split(self, hand_index: int = 0):
        if self.hand[hand_index].cards[0] == self.hand[hand_index].cards[1]:
            valid = False
            while valid == False:
                valid = True
                split = input('Split your hand? y/n')
                if split.lower() == 'y':
                    self.split_hand(hand_index)
                elif split.lower() == 'n':
                    break
                else:
                    print("Invalid input. Try 'y' or 'n'")

    def split_hand(self, hand_index: int = 0):
        # oooohhhh take a look at this for calling the dealer to deal a second hand in self.cards[]
        self.hand.append(Hand())
        self.take_card(self.hand[hand_index].pop(), len(self.hand) - 1)
        
        pass

    def double_down(self):
        self.bet = self.bet*2

    def action_hit(self):
        self.hand.cards.append(self.dealer.deal_one())
        self.hand.calc_total()

    def action_stand(self):
        self.hand.stand = True

    def play_hand(self):
        self.check_split()
        #if self.total



class Dealer(Player):

    def __init__(self, deck: CardDeck()) -> None:
        super().__init__()
        self.table = []     # Table will be a list of Player objects
        self.deck = deck
    
    def create_table(self, table: list[Player()]):
        self.table = table[:]


    def deal(self):
        for x in range(2):
            for player in self.table:
                player.take_card(self.deck.draw_card())
            self.take_card(self.deck.draw_card())


    def deal_one(self):
        return self.deck.draw_card()
    
    def dealer_play(self):
        while len(list(filter(lambda x : x < 18), self.total) == len(self.total)):
            self.action_hit()
            self.calc_total()

    def players_play(self):
        for player in self.table:
            player.play_hand()


'''
Order of play is as follows:
Bet
Deal one card around, deal a second card around (dealers first card is dealt face-down)
Play begins with the player to the left of the dealer and continues around anti-clockwise
-   players decide to split, double down, hit, stay 
-   in the event of a split, the player plays one hand then the other
-   once a player has made their decisions (after either busting or staying) the next player begins
The dealer reveal their face-down card and plays their hand (must hit until total is at least 17)
Winners are chosen
-   any player/hand that beats the dealer WINS!

'''
def play():
    # first find the number of players/hands to deal
    valid = False
    while valid == False:
        valid = True
        num_players = input('How many players are at the table? ')
        if not num_players.isdigit():
            valid = False
        elif int(num_players) > 6:
            valid = False
    
    # next, create table
    dealer = Dealer()
    players_at_table = [Player(dealer) for x in range(num_players)]

    dealer.create_table(players_at_table)

    # check order of play, deal cards or bet first? Either way:
    dealer.deal()

    for player in players_at_table:
        player.place_bet()
    



if __name__ == '__main__':

    list1 = [1, 41, 21, 12]
    list2 = [2, 31, 18, 17]
    list1.extend(list2)
    list3 = sorted(list(filter(lambda x: x < 22, list1)))
    if 21 in list3:
        print("That's it babeeeeeee")

    print(list(map(lambda x: x + 10, list2)))
    
    deck1 = CardDeck()
    dealer1 = Dealer(deck1)
    player1 = Player(dealer1)
    player2 = Player(dealer1)
    dealer1.create_table([player1, player2])
    dealer1.deal()
    print('Player 1 cards: ', player1.cards)
    print('Player 1 score: ', player1.total)
    print('Player 2 cards: ', player2.cards)
    print('Player 2 score: ', player2.total)
    print('Dealer 1 cards: ', dealer1.cards)
    print('Dealer 1 score: ', dealer1.total)


class Thingy():
    def __init__(self) -> None:
        self.item = 0

    def thinger(self):
        self.item2 = 2


test = Thingy()
test.thinger()
print(test.item2)