#!/usr/bin/python3

import random

person_count = 100
half_person_count = int(person_count / 2)

# Hat choices
hat_choices = ['r','b']
hat_opposite = {'b':'r', 'r':'b'}

# 0.1% error rate in guesses
error_rate = 0.001

def guess_constant(heard_guesses, seen_hats):
    return 'b'

def guess_random(heard_guesses, seen_hats):
    return random.choice(hat_choices)

def guess_future(heard_guesses, seen_hats):
    """ First half of list calls out hat of correspondent in second half of list """
    full_list = heard_guesses + ['x'] + seen_hats
    my_index = len(heard_guesses)
    if my_index < half_person_count:
        # Call out the hat of the person in the second half of the list, hope same as mine
        return full_list[my_index+half_person_count]
    else:
        # Remember what was called out by my corresponding person in first half of list
        return heard_guesses[my_index - half_person_count]

def guess_parity(heard_guesses, seen_hats):
    """ Measure heard and seen parity of blue hats, call out blue for even, red for odd."""
    heard_blue_count = len([g for g in heard_guesses if g == 'b'])
    seen_blue_count = len([s for s in seen_hats if s == 'b'])
    if (heard_blue_count + seen_blue_count) % 2 == 0:
        return 'b'
    else:
        return 'r'

def run_test(guess_func):
    hat_list = [ random.choice(hat_choices) for i in range(0, person_count) ]
    print("Actual: " + "".join(hat_list))
    answer_list = []
    score_list = []
    error_list = []
    correct = 0
    for i in range(0, person_count):
        guess = guess_func(answer_list, hat_list[i+1:])
        if random.random() < error_rate:
            guess = hat_opposite[guess]
            error_list.append('X')
        else:
            error_list.append('-')
        answer_list.append(guess)
        if guess == hat_list[i]:
            correct += 1
            score_list.append('-')
        else:
            score_list.append('X')
    print("""
Called: %s
Score:  %s
  %d correct
""" % ("".join(answer_list), "".join(score_list), correct))
    return correct

if __name__ == "__main__":
    trial_count = 10
    averages = dict()
    for func in [guess_constant, guess_random, guess_future, guess_parity]:
        correct_total = 0.0
        print("%s:" % func.__name__)
        for i in range(0, trial_count):
            print("Trial %d" % (i+1))
            correct_total += run_test(func)
        averages[func.__name__] = (correct_total / trial_count)
    for (f,v) in averages.items():
        print("%20s average correct: %.2f" % (f,v))

