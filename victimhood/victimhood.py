#!/usr/bin/python3

"""
Original post http://marlinschamps.blogspot.com/2006/08/tdl-gaming-world-series-of-victimhood.html
"""

import random
import string

deck = {
 # Key: (points,class)
 'Black':           (14, 'skin'),
 'Native-American': (13, 'ethnicity'),
 'Muslim':          (12, 'religion'),
 'Hispanic':        (11, 'ethnicity'),
 'Transgender':     (10, 'gender'),
 'Gay':              (9, 'none'),
 'Female':           (8, 'gender'),
 'Woman':            (8, 'gender'),
 'Oriental':         (7, 'ethnicity'),
 'Handicapped':      (6, 'none'),
 'Satanist':         (6, 'religion'),
 'Furry':            (5, 'none'),
 'Non-Christian':    (4, 'religion'),
 'East-Indian':      (3, 'ethnicity'),
 'Chinese':          (3, 'ethnicity'),
 'Hindu':            (3, 'religion'),
 'Destitute':        (2, 'economic'),
 'White':            (0, 'skin'),
 'Straight':         (0, 'gender'),
 'Christian':        (0, 'religion'),
 'Bourgeois':        (0, 'economic'),
 'Man':              (0, 'gender'),
}

# Categories in the order you'd describe someone
category_list = [
 'economic','none','skin','religion','ethnicity','gender',
]
categories = set(category_list)

def cardscore(card):
 """ How much does this card score? """
 (s, unused_cls) = deck[card]
 return s

def cardclass(card):
 """ What class does this card represent? """
 (unused_s, cls) = deck[card]
 return cls


class Hand(object):
 """ A hand is a list of cards with some associated scoring functions """
 def __init__(self, start_cards=None):
  if start_cards is None:
   self.cards = []
  else:
   self.cards = start_cards[:]

 @classmethod
 def parse(cls, desc):
  desc = desc.lower()
  for card in deck.keys():
    if card.find('-') >= 0:
      # handle the hyphens
      c = card.lower() 
      nc = c.replace('-', ' ')
      desc = desc.replace(nc, c)
  words = desc.split()
  nonempty_words = set([w for w in words if len(w) >= 1])
  cards = [c for c in deck.keys() if c.lower() in nonempty_words]
  return Hand(cards)

 def add(self, card):
  self.cards.append(card)

 def bestscore(self):
  (score, bestcards) = self.besthand()
  return score

 def bestcards(self):
  (score, bestcards) = self.besthand()
  return bestcards

 def besthand(self):
  """ What's the highest possible score for this hand?
  Limitations: one card per class, no more than 5
  cards in total
  Return (score, best_hand)
  """
  score_by_class = { }
  card_by_class = { }
  for card in self.cards:
    try:
      s = cardscore(card)
      card_class = cardclass(card) 
    except KeyError as err:
      raise KeyError("Invalid card name '%s'" % card)
    if card_class not in score_by_class:
      score_by_class[card_class] = s
    if s >= score_by_class[card_class]:
      score_by_class[card_class] = s
      card_by_class[card_class] = card
  # We now have the best scoring card in each
  # class. But we can only use the best 5.
  cards = card_by_class.values()
  cards = sorted(cards, key=cardscore)
  if len(cards) > 5:
    cards = cards[0:5]
  tot = 0
  for card in cards:
    tot += cardscore(card)
  best_hand = Hand(cards)
  return (tot, best_hand)

 def merge(self, hand):
  """ Merge this hand and another to return a new one """
  ans = self.copy()
  for c in hand.cards:
   ans.add(c)
  return ans

 def copy(self):
  return Hand(self.cards)
 
 def __str__(self):
  return ', '.join(['%s (%d)' % (c, cardscore(c)) for c in self.cards])

 def card_in_class(self,class_name):
  """Returns a card in the given class, if the hand has one"""
  for card in self.cards:
   (s,c) = deck[card] 
   if c == class_name:
    return card
  # No match
  return None

 def description(self):
   card_order = [self.card_in_class(c) for c in category_list]
   card_order = filter(lambda x: x is not None, card_order)
   return ' '.join(card_order)

class Game(object):
 def __init__(self, player_count, deck_multiple=2):
   self.player_count = player_count
   self.deck_multiple = deck_multiple
   self.player_hands = { }
   for i in range(1,1+player_count):
     self.player_hands[i] = Hand()
   self.shuffle_deck()
   self.community = Hand()

 def shuffle_deck(self):
   self.deck = []
   for i in range(self.deck_multiple):
    self.deck.extend(deck.keys())
   random.shuffle(self.deck)

 def deal(self, cards_per_player):
   for p in range(1,1+self.player_count):
     for c in range(cards_per_player): 
       card = self.deck.pop()  # might run out
       self.player_hands[p].add(card)

 def deal_community(self, community_cards):
   self.community = Hand()
   for c in range(community_cards):
    card = self.deck.pop()
    self.community.add(card)

 def get_community(self):
  return self.community

 def best_hand(self, player_num):
   h = self.player_hands[player_num]
   # Expand the hand with any community cards
   h2 = h.merge(self.community)
   return h2.besthand()

if __name__ == '__main__':
 descriptions = [
   "chinese gay transgender",
   "black destitute woman",
   "native american east asian woman",
   "straight muslim man",
 ]
 for d in descriptions:
  h = Hand.parse(d)
  (score, hand) = h.besthand() 
  print("'%s' gives '%s' which scores %d" % (d, hand.description(), score))

 """
 player_count=4
 g = Game(player_count=player_count, deck_multiple=2)
 # Everyone gets 5 cards
 g.deal(5)
 # There are 3 community cards
 g.deal_community(3)
 print "Community cards: %s\n" % g.get_community()
 winner = None
 win_score = 0
 for p in range(1,1+player_count):
  (score, hand) = g.best_hand(p)
  print "Player %d scores %d with %s" % (p, score, hand)
  print "  which is a %s" % hand.description()
  if score > win_score:
    winner = p
    win_score = score

 print "\nPlayer %d wins!" % winner
 """
