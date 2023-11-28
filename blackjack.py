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
Hand is its own class
Dealer controls the deck object (as in real life)
Players share a dealer object to request dealer methods
Players each have a Hand object


Wants:
A helper function for valid inputs, currently have a fair amount of repeated code
    that looks like:
        valid = False
        while valid == False:
            so on and so forth


'''

import random

def player_banner(i: int):
    print(' ---------')
    print(f'| Player{i + 1} |')
    print(' ---------')

def dealer_banner():
    print(' ---------')
    print(f'| Dealer |')
    print(' ---------')

class CardDeck():

    def __init__(self, num_decks = 1) -> None:
        self.deck = [(x,y) for x in ["\u2663", "\u2665", "\u2666", "\u2660"] for y in ([z for z in range(2,11)] + ['J', 'Q', 'K', 'A'])]
        self.num_decks = num_decks
        self.deck *= num_decks
        random.shuffle(self.deck)

    def draw_card(self):
        if self.deck:
            return self.deck.pop()
        else:
            self.deck = [(x,y) for x in ["\u2663", "\u2665", "\u2666", "\u2660"] for y in ([z for z in range(2,11)] + ['J', 'Q', 'K', 'A'])]
            self.deck *= self.num_decks
            random.shuffle(self.deck)
    
class Hand():

    def __init__(self) -> None:
        self.cards = []
        self.total = [0]
        self.stand = False
        self.blackjack = False
        self.bust = False
        self.bet = 0

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
            else:
                self.total = list(map(lambda x: x + card, self.total))
        
        self.total = list(filter(lambda x : x < 22, self.total)) # filter out bust scores
        self.total = list(sorted(set(self.total)))  # remove duplicate total entries
        if not self.total: # check if only bust scores existed before filtering (resulting in empty list)
            self.bust = True
            print('Oh no! BUST!')
            self.stand = True
        elif 21 in self.total:
            self.stand = True

class Player():

    def __init__(self, dealer = None) -> None:
        self.dealer = dealer
        self.hand = [Hand()]
        self.bank = 200

    def check_in(self, position: int):
        player_banner(position - 1)
        print(f'Hello Player{position}')
        valid = False
        while valid == False:
            bank = input('Entering the table, what is your bank? $')
            if bank.isdigit():
                self.bank = int(bank)
                valid = True
            else:
                print('Invalid input, please enter a whole dollar amount')

    def place_bet(self):
        valid = False
        while valid == False:
            valid = True
            wager = input('How much would you like to bet? ')
            if not wager.isdigit():
                print('Please enter a whole dollar amount')
                valid = False
            elif int(wager) > 200:
                valid = False
                print("Wagers cannot exceed $200 at this table")
            elif int(wager) > self.bank:
                valid = False
                print('Insufficient bank')
        self.hand[0].bet = int(wager)
        self.bank -= int(wager)
    
    def take_card(self, card: tuple, hand_index: int = 0):   # Player should always be passed a card
        '''
            take_card adds a card to the player's hand

            card: expected to be a tuple of (suit, value)
            hand_index: should be an integer, defines which hand is being altered
                in the case of a split hand. Default value is zero
        '''
        self.hand[hand_index].cards.append(card)
        self.hand[hand_index].calc_total()

    def show_hand(self, hand_index: int = 0):
        holding = [hand.cards for hand in self.hand]
        totals = [hand.total for hand in self.hand]
        #return self.hand[hand_index].cards, self.hand[hand_index].total
        return holding, totals
    
    def check_blackjack(self, hand_index: int = 0):
        self.hand[hand_index].calc_total()
        if 21 in self.hand[hand_index].total:
            self.hand[hand_index].blackjack = True

    def check_split(self, hand_index: int = 0):
        if self.bank < self.hand[hand_index].bet:
            print('Cannot split, insufficient bank.')
            return
        if self.hand[hand_index].cards[0][1] == self.hand[hand_index].cards[1][1]:
            valid = False
            while valid == False:
                valid = True
                print(self.hand[hand_index].cards)
                split = input('Split your hand? y/n ')
                if split.lower() == 'y':
                    self.split_hand(hand_index)
                elif split.lower() == 'n':
                    return
                else:
                    print("Invalid input. Try 'y' or 'n' ")
                    valid = False

    def split_hand(self, hand_index: int = 0):
        # oooohhhh take a look at this for calling the dealer to deal a second hand in self.cards[]

        # First split the hand into two new hands
        self.hand.append(Hand())
        self.take_card(self.hand[hand_index].cards.pop(), len(self.hand) - 1)
        
        # then deal one to the each of the two hands
        self.take_card(self.dealer.deal_one())
        self.take_card(self.dealer.deal_one(), len(self.hand) - 1)

        #apply same bet to second hand, doubling bet
        self.hand[len(self.hand) - 1].bet =  self.hand[hand_index].bet
        self.bank -= self.hand[hand_index].bet

        # check/update the two hand totals
        self.hand[hand_index].calc_total()
        self.hand[len(self.hand) - 1].calc_total()

    def check_double_down(self, hand_index: int = 0):
        if self.bank < self.hand[hand_index].bet:
            print('Cannot double down. Insufficent bank')
            return
        dbl_vals = {9, 10, 11}
        hand_set = dbl_vals.intersection(set(self.hand[hand_index].total))
        if hand_set and self.hand[hand_index].blackjack == False:
            valid = False
            while valid == False:
                valid = True
                print(self.hand[hand_index].cards)
                double_answer = input('Would you like to double down? ')
                if double_answer.lower() in 'yes':
                    self.double_down()
                elif double_answer.lower() in 'no':
                    return
                else:
                    print('Invalid entry, please choose y/n ')
                    valid = False

    def double_down(self, hand_index: int = 0):
        self.hand[hand_index].bet *= 2
        self.action_hit(hand_index)
        self.hand[hand_index].calc_total()
        self.hand[hand_index].stand = True


    def action_hit(self, hand_index: int = 0):
        self.hand[hand_index].cards.append(self.dealer.deal_one())
        self.hand[hand_index].calc_total()

    def action_stand(self, hand_index: int = 0):
        self.hand[hand_index].stand = True

    def play_hand(self): # currently only plays the first hand of a split
        hand_index = 0
        for hand in self.hand:
            self.dealer.show_table()
            self.check_blackjack(hand_index)
            self.check_split(hand_index)
            self.check_double_down(hand_index)
            while hand.stand == False:
                valid = False
                while valid == False:
                    valid = True
                    card_list, total = self.show_hand(hand_index)
                    print(card_list)
                    print(f'TOTAL: {total}')
                    decision = input('Would you like to hit or stand? (enter "hit" or "stand") ')
                    if decision.lower() in ['hit', 'stand']:
                        if decision.lower() == 'hit':
                            self.action_hit(hand_index)
                        else:
                            self.action_stand(hand_index)
                    else:
                        print('Invalid input')
                        valid = False
            print(self.hand[hand_index].cards)
            print(self.hand[hand_index].total)
            hand_index += 1
            
    def clear_hand(self):
        self.hand.clear()
        self.hand = [Hand()]
        #if self.total



class Dealer(Player):

    def __init__(self, deck: CardDeck()) -> None:
        super().__init__()
        self.table = []     # Table will be a list of Player objects
        self.deck = deck
        self.hand = Hand()
        
    
    def create_table(self, table: list[Player()]):
        self.table = table[:]

    def take_bets(self):
        for i, player in enumerate(self.table):
            player_banner(i)
            print(f'Bank: ${player.bank}')
            player.place_bet()
            

    def deal(self):
        for _ in range(2):
            for player in self.table:
                player.take_card(self.deck.draw_card())
            self.hand.cards.append(self.deck.draw_card())
        
    def show_table(self, end_game: bool = False):
        print(' ---------------------------------------------')
        print(f'| Dealer showing:  {self.show_card(end_game)}')
        for i, player in enumerate(self.table):
            hand, tot = player.show_hand()
            for k, cards in enumerate(hand):
                print(f'| Player{i + 1} showing: {cards} \t TOTAL: {tot[k]}')
        print(' ---------------------------------------------') 
        

    def show_card(self, end_game: bool = False):
        if end_game == False:
            return self.hand.cards[0]
        else:
            return self.hand.cards

    def deal_one(self):
        return self.deck.draw_card()
    

    def dealer_play(self):
        #while len(list(filter(lambda x : x < 18), self.total)) == len(self.total):
            # the above is problematic, only checks to see if some value is 18+, but could be a bust
            # when in real life the dealer would convert the ACE to a 1 and keep going without busting
            # HOW TO RE-WRITE?
            # Hand.calc_total() filters values over 21 when adding computing ACE values
            # perhaps a simple < while max(self.hand.total) < 17 would work sufficiently well?
        self.hand.calc_total()
        while self.hand.total and max(self.hand.total) < 17:
            self.hand.cards.append(self.deal_one())
            self.hand.calc_total()
        print(self.hand.cards)
        print(self.hand.total)

    def players_play(self):
        for player in self.table:
            player.play_hand()

    def reveal_hand(self):
        return self.hand.cards

    def determine_winners(self):
        self.show_table(end_game=True)
        if self.hand.bust == True:
            for i, player in enumerate(self.table):
                for hand in player.hand:
                    if hand.blackjack == True:
                        print(f'| Player{i + 1} won ${int(hand.bet * 1.5)}')
                        player.bank += int(hand.bet + hand.bet * 1.5)
                    elif hand.bust == False:
                        player.bank += hand.bet * 2
                        print(f'Player{i + 1} won ${hand.bet}')
                    else:
                        print(f'Player{i + 1} lost ${hand.bet}')
        
        elif self.hand.blackjack == True:
            for i, player in enumerate(self.table):
                for hand in player.hand:
                    if hand.blackjack == True:
                        player.bank += hand.bet   # push
                        print(f'Player{i + 1} pushed')
                    else:
                        print(f'Player{i + 1} lost ${hand.bet}')
        else:            
            for i, player in enumerate(self.table):
                for hand in player.hand:
                    if hand.bust == True:
                        print(f'| Player{i + 1} lost ${hand.bet}')
                        continue
                    elif hand.blackjack == True:
                        print(f'| Player{i + 1} won ${int(hand.bet * 1.5)}')
                        player.bank += int(hand.bet + hand.bet * 1.5)
                    elif max(hand.total) > max(self.hand.total):
                        print(f'| Player{i + 1} won ${hand.bet}')
                        player.bank += hand.bet * 2
                    elif max(hand.total) == max(self.hand.total):
                        print(f'| Player{i + 1} pushed')
                        player.bank += hand.bet
                    else:
                        print(f'| Player{i + 1} lost ${hand.bet}')
        print(' ---------------------------------------------') 

    
    def clear_hand(self):
        self.hand = Hand()

    def another_hand(self):
        while True:
            again = input('Would you like to play another round? y/n/bank ')
            if again.lower() == 'y':
                for player in self.table:
                    player.clear_hand()
                self.clear_hand()
                return True
            elif again.lower() == 'n':
                return False
            elif again.lower() == 'bank':
                for i, player in enumerate(self.table):
                    print(f'Player{i + 1} bank: ${player.bank}')
            else:
                print("Invalid input, please enter 'y' or 'n' ")
        

                


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
    deck = CardDeck()
    dealer = Dealer(deck)

    # first find the number of players/hands to deal
    valid = False
    while valid == False:
        valid = True
        num_players = input('How many players are at the table? ')
        if not num_players.isdigit():
            valid = False
        elif int(num_players) > 9:
            valid = False
    
    # next, create table
    players_at_table = [Player(dealer) for x in range(int(num_players))]

    dealer.create_table(players_at_table)
    for i, player in enumerate(dealer.table):
        player.check_in(i+1)

    play_round = True
    while play_round == True:    
        dealer.take_bets()

        # check order of play, deal cards or bet first? Either way:
        dealer.deal()
        
        # everyone plays
        for i, player in enumerate(players_at_table):
            player_banner(i)
            print(f'Bank: ${player.bank}')
            player.play_hand()
        dealer_banner()
        dealer.dealer_play()

        # winnings are determined
        dealer.determine_winners()
        play_round = dealer.another_hand()



if __name__ == '__main__':
    play()
