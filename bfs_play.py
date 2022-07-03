import os.path as osp
import sys

from sympy import acsc
dirname = osp.dirname(__file__)
sys.path.append(dirname)

import pygame
import numpy as np
import time
from amazing_brick.game.wrapped_amazing_brick import \
        GameState, SCREEN
from collections import namedtuple
from queue import PriorityQueue
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--display', action='store_true', default=False)
args = parser.parse_args()

Node = namedtuple("Node", ['sta' , 'act', 'father'])
Node.__lt__ = lambda x,y:x.sta['y']<y.sta['y']

game_state = GameState(True)
game_state.player.velMaxY = 20
game_state.player.AccY = 5

ACTIONS = (0, 1, 2)

def bfs_forward(root_state, show=False):
    q = PriorityQueue()
    q.put(Node(root_state,None,None))
    while True:
        if q.empty():
            break
        father_node = q.get()
        father_state = father_node.sta
        if check_for_score(father_state) and father_state!=root_state:
            if show:
                pygame.draw.rect(SCREEN, (0, 0, 255), \
                        (father_state['x'] - game_state.s_c.x, father_state['y'] - game_state.s_c.y, game_state.player.width, game_state.player.height))
                pygame.display.update()
            break
        for action in ACTIONS:
            # father_state = move_forward(father_state, ACTIONS[0])
            new_state = move_forward(father_state, action)
            if check_crash(new_state):
                if show:
                    pygame.draw.rect(SCREEN, (255, 0, 0), \
                            (new_state['x'] - game_state.s_c.x, new_state['y'] - game_state.s_c.y, game_state.player.width, game_state.player.height))
                    pygame.display.update()
            else:
                if show:
                    pygame.draw.rect(SCREEN, (100, 100, 100), \
                            (new_state['x'] - game_state.s_c.x, new_state['y'] - game_state.s_c.y, game_state.player.width, game_state.player.height))
                    pygame.display.update()
                node = Node(new_state.copy(), action, father_node)
                q.put(node)
    
    return father_node

def check_for_score(state):
    # check for score
    playerMidPos = state['y'] - game_state.s_c.y + game_state.player.height / 2
    for ind, pipe in enumerate(game_state.pipes):
        if ind % 2 == 1:
            continue
        game_state.s_c(pipe)
        if playerMidPos <= pipe.y_c + pipe.height:
            if not pipe.scored:
                return True
    return False

def move_forward(state, action):
    new_state = state.copy()
    if action == 0:
        if state['velX'] > 0:
            new_state['velX'] -= game_state.player.dragForce
        elif state['velX'] < 0:
            new_state['velX'] += game_state.player.dragForce
        new_state['velY'] += game_state.player.gravity
        if new_state['velX'] > game_state.player.velMaxX:
            new_state['velX'] = game_state.player.velMaxX
        if new_state['velX'] < - game_state.player.velMaxX:
            new_state['velX'] = - game_state.player.velMaxX
        if new_state['velY'] > game_state.player.velMaxY:
            new_state['velY'] = game_state.player.velMaxY
        if new_state['velY'] < - game_state.player.velMaxY:
            new_state['velY'] = - game_state.player.velMaxY
    elif action == 1:
        new_state['velX'] -= game_state.player.AccX
        new_state['velY'] -= (game_state.player.AccY - game_state.player.gravity)
        if new_state['velX'] > game_state.player.velMaxX:
            new_state['velX'] = game_state.player.velMaxX
        if new_state['velX'] < - game_state.player.velMaxX:
            new_state['velX'] = - game_state.player.velMaxX
        if new_state['velY'] > game_state.player.velMaxY:
            new_state['velY'] = game_state.player.velMaxY
        if new_state['velY'] < - game_state.player.velMaxY:
            new_state['velY'] = - game_state.player.velMaxY
    elif action == 2:
        new_state['velX'] += game_state.player.AccX
        new_state['velY'] -= (game_state.player.AccY - game_state.player.gravity)
        if new_state['velX'] > game_state.player.velMaxX:
            new_state['velX'] = game_state.player.velMaxX
        if new_state['velX'] < - game_state.player.velMaxX:
            new_state['velX'] = - game_state.player.velMaxX
        if new_state['velY'] > game_state.player.velMaxY:
            new_state['velY'] = game_state.player.velMaxY
        if new_state['velY'] < - game_state.player.velMaxY:
            new_state['velY'] = - game_state.player.velMaxY
    
    new_state['x'] += new_state['velX']
    new_state['y'] += new_state['velY']
    return new_state

def check_crash(state):
    # check if crash here
    x_c = state['x'] - game_state.s_c.x
    y_c = state['y'] - game_state.s_c.y
    if y_c + game_state.player.height >= game_state.s_c.height:
        return True
    if x_c <= game_state.s_c.x or \
            x_c >= game_state.s_c.width - game_state.player.width:
        return True
    for pipe in game_state.pipes:
        x0, y0, x0_, y0_ = state['x'], state['y'], \
                state['x'] + game_state.player.width, \
                state['y'] + game_state.player.height
        x1, y1, x1_, y1_ = pipe.box()
        lx = abs((x0 + x0_) / 2 - (x1 + x1_) / 2)
        ly = abs((y0 + y0_) / 2 - (y1 + y1_) / 2)
        if lx <= (game_state.player.width + pipe.width) / 2 and \
                ly <= (game_state.player.height + pipe.height) / 2:
            return True
    for block in game_state.blocks:
        x0, y0, x0_, y0_ = state['x'], state['y'], \
                state['x'] + game_state.player.width, \
                state['y'] + game_state.player.height
        x1, y1, x1_, y1_ = block.box()
        lx = abs((x0 + x0_) / 2 - (x1 + x1_) / 2)
        ly = abs((y0 + y0_) / 2 - (y1 + y1_) / 2)
        if lx <= (game_state.player.width + block.width) / 2 and \
                ly <= (game_state.player.height + block.height) / 2:
            return True
    return False

while True:
    game_state.player.velMaxY = 20
    game_state.player.AccY = 5
    # game_state.frame_step(ACTIONS[0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    
    root_state = {}
    root_state['x'] = game_state.player.x
    root_state['y'] = game_state.player.y
    root_state['velX'] = game_state.player.velX
    root_state['velY'] = game_state.player.velY

    game_state.player.velMaxY = 20
    game_state.player.AccY = 5
    final_node = bfs_forward(root_state, args.display)
    if args.display:
        time.sleep(0.2)
    actions = []
    while True:
        node = final_node.father
        if node is None:
            break
        actions.append(final_node.act)
        final_node = node
    for i in range(-1, -len(actions)-1, -1):
        # game_state.frame_step(ACTIONS[0])
        game_state.frame_step(actions[i])
        game_state.player.velMaxY = 20
        game_state.player.AccY = 5

pygame.quit()
