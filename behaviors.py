import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def take_best_planet(state):
    # Calculate what the best planet is
    deficit = {}

    for target in state.not_my_planets():
        accounted = False
        for outgoing in state.my_fleets():
            if outgoing.destination_planet is target.ID:
                accounted = True
                break
        if accounted:
           continue 
        total = 0
        # if planet is neutral
        if target.owner == 0:
            total += (target.num_ships/target.growth_rate)
        owned_planets = state.my_planets().copy()
        travel_time = 0
        found = False
        while any(owned_planets):
            closest_planet = min(owned_planets, key=lambda p: state.distance(p.ID, target.ID), default=None)
            ships_required = target.num_ships
            for attacker in state.enemy_fleets():
                if attacker.destination_planet == target.ID:
                    ships_required += attacker.num_ships
                    if target.owner == 0 and attacker.turns_remaining < state.distance(closest_planet.ID, target.ID):
                        ships_required += (state.distance(closest_planet.ID,target.ID) - attacker.turns_remaining) * target.growth_rate - target.num_ships * 2

            if target.owner == 2:
                ships_required += target.growth_rate * state.distance(closest_planet.ID, target.ID)
            else:
                logging.debug(target.owner)

            if closest_planet.num_ships > ships_required:
                travel_time = state.distance(closest_planet.ID,target.ID)
                found = True
                break
            else:
                owned_planets.remove(closest_planet)
        
        if found:
            deficit[target] = (total + travel_time ,closest_planet, ships_required)
            #logging.debug(deficit[target])
    
    lowest = 9999999
    ships_sent = 0
    from_planet = None
    best_planet = None
    for candidate in deficit.keys(): 
        if deficit[candidate][0] < lowest: 
            lowest, from_planet, ships_sent = deficit[candidate]
            best_planet = candidate
    
    if best_planet: 
        logging.debug(best_planet)
        return issue_order(state, from_planet.ID, best_planet.ID, ships_sent + 1)
    return False