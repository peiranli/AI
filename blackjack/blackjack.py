import pygame, sys, random, copy
from pygame.locals import *
from cards import *
import time
import numpy as np

def genCard(cList, xList):
    #Generate and remove an card from cList and append it to xList.
    #Return the card, and whether the card is an Ace
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    #Generates two cards for dealer and user, one at a time for each.
    #Returns if card is Ace and the total amount of the cards per person.
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    #The values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst

def make_state(userSum, userA, dealFirst, dealAFirst):
    #Eliminate duplicated bust cases
    if userSum > 21: 
        userSum = 22
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace   
    return (userSum, userA, dealFirst, dealAFirst)

def policy(userSum):
    if userSum < 17:
        return 0
    else:
        return 1

def MC_Policy_Evaluation(policy, states, gamma, MCvalues, G):
    converge = False
    while not converge:
        # generate random game
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        # do simulation
        episode = simulation_sequence(policy, state, userCard, dealCard, ccards)
        delta = 0
        # update
        for e in episode:
            G[e[0]].append(reward_to_go(e[0], gamma, episode))
            old_value = MCvalues[e[0]]
            MCvalues[e[0]] = sum(G[e[0]])/float(len(G[e[0]]))
            delta = max(delta, abs(MCvalues[e[0]] - old_value))
        if delta < 0.05:
            converge = True

def reward_to_go(s, gamma, episode):
    index = 0
    # find state in sequence
    while index < len(episode):
        if episode[index][0] == s:
            break
        index += 1
    reward = 0.0
    k = 0
    # compute reward to go
    while index < len(episode):
        reward += float(gamma)**k*float(episode[index][1])
        index += 1
        k += 1
    return reward

def simulation_sequence(policy, state, userCard, dealCard, ccards):
    episode = []
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    stand = False
    gameover = False
    # follow the game engine to do simulation
    while True:
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        # calculate reward
        if not (gameover or stand):
            episode.append((state,0))
        else:
            if userSum == dealSum:
                reward = 0
            elif userSum <= 21 and len(userCard) == 5:
                reward = 1
            elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                reward = 1
            else:
                reward = -1
            episode.append((state,reward))
            return episode
        action = policy(userSum)
        if not (gameover or stand) and action == 0:
            #Give player a card
            card, cA = genCard(ccards, userCard)
            userA += cA
            userSum += getAmt(card)
            while userSum > 21 and userA > 0:
                userA -= 1
                userSum -= 10
        elif not gameover and action == 1:
            #Dealer plays, user stands
            stand = True
            if dealSum == 21:
                pass
            else:
                while dealSum <= userSum and dealSum < 17:
                    card, cA = genCard(ccards, dealCard)
                    dealA += cA
                    dealSum += getAmt(card)
                    while dealSum > 21 and dealA > 0:
                        dealA -= 1
                        dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)

def TD_Policy_Evaluation(policy, states, gamma, TDvalues, NTD):
    converge = False
    while not converge:
        # generate random game
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        stand = False
        delta = 0
        while state:
            action = policy(state[0])
            next_state, curr_reward, next_reward, stand= simulate_one_step(state, action, userCard, dealCard, ccards, stand)
            if not next_state:
                break
            old_value = TDvalues[state]
            u_next_state = TDvalues[next_state]
            # use reward of terminal state
            if next_reward != 0:
                u_next_state = next_reward
            # temporal difference update
            TDvalues[state] = TDvalues[state] + (10/float(9+NTD[state]))*(curr_reward+gamma*u_next_state-TDvalues[state])
            NTD[state] += 1
            # compute max delta value
            delta = max(delta, abs(TDvalues[state]-old_value))
            state = next_state
        if delta < 0.05:
            converge = True

def simulate_one_step(state, action, userCard, dealCard, ccards, stand):
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    stand = stand
    # check if current state is terminal
    if (userSum >= 21 and userA == 0) or len(userCard) == 5:
        gameover = True
    else:
        gameover = False
    if len(userCard) == 2 and userSum == 21:
        gameover = True
    if gameover or stand:
        if userSum == dealSum:
            reward = 0
        elif userSum <= 21 and len(userCard) == 5:
            reward = 1
        elif userSum <= 21 and dealSum < userSum or dealSum > 21:
            reward = 1
        else:
            reward = -1
        return (None, reward, 0, stand)
        
    if not (gameover or stand) and action == 0:
        #Give player a card
        card, cA = genCard(ccards, userCard)
        userA += cA
        userSum += getAmt(card)
        while userSum > 21 and userA > 0:
            userA -= 1
            userSum -= 10
    elif not gameover and action == 1:
        #Dealer plays, user stands
        stand = True
        if dealSum == 21:
            pass
        else:
            while dealSum <= userSum and dealSum < 17:
                card, cA = genCard(ccards, dealCard)
                dealA += cA
                dealSum += getAmt(card)
                while dealSum > 21 and dealA > 0:
                    dealA -= 1
                    dealSum -= 10
    # check if next state is terminal
    if (userSum >= 21 and userA == 0) or len(userCard) == 5:
        gameover = True
    else:
        gameover = False
    if len(userCard) == 2 and userSum == 21:
        gameover = True
    next_state = make_state(userSum, userA, dealFirst, dealAFirst)
    # calculate reward
    if gameover or stand:
        if userSum == dealSum:
            reward = 0
        elif userSum <= 21 and len(userCard) == 5:
            reward = 1
        elif userSum <= 21 and dealSum < userSum or dealSum > 21:
            reward = 1
        else:
            reward = -1
        return (next_state, 0, reward, stand)
    else:
        return (next_state, 0, 0, stand)
    
def Q_Learning(states, gamma, Qvalues, NQ):
    converge = False
    while not converge:
        # generate random game
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        epsilon = random.uniform(0.0, 0.5)
        stand = False
        delta = 0
        while state:
            action = pick_action(state, epsilon, Qvalues)
            next_state, curr_reward, next_reward, stand = simulate_one_step(state, action, userCard, dealCard, ccards, stand)
            if not next_state:
                break
            old_value = Qvalues[state][action]
            u_next_state = Qvalues[next_state][np.argmax(Qvalues[next_state])]
            # use reward of terminal state
            if next_reward != 0:
                u_next_state = next_reward
            # Q learning
            Qvalues[state][action] = Qvalues[state][action] + (10/float(9+NQ[state]))*(curr_reward+gamma*u_next_state-Qvalues[state][action])
            NQ[state] += 1
            delta = max(delta, abs(Qvalues[state][action]-old_value))
            state = next_state
        if delta < 0.05:
            converge = True


def pick_action(state, epsilon, Qvalues):
    if random.uniform(0.0, 1.0) < epsilon:
        return random.randint(0,1)
    else:
        return np.argmax(Qvalues[state])

def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    #Initialize Game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)
    #Prepare table of utilities
    G = {}
    MCvalues = {}
    R = {}
    TDvalues = {}
    NTD = {}
    Qvalues = {}
    NQ = {}
    #i iterates through the sum of user's cards. It is set to 22 if the user went bust. 
    #j iterates through the value of the dealer's first card. Ace is eleven. 
    #a1 is the number of Aces that the user has.
    #a2 denotes whether the dealer's first card is Ace. 
    states = []
    for i in range(2,23):
        for j in range(2,12):
            for a1 in range(0,5):
                for a2 in range(0,2):
                    s = (i,a1,j,a2)
                    states.append(s)
                    #utility computed by MC-learning
                    MCvalues[s] = 0
                    G[s] = []
                    #utility computed by TD-learning
                    TDvalues[s] = 0
                    NTD[s] = 0
                    #first element is Q value of "Hit", second element is Q value of "Stand"
                    Qvalues[s] = [0,0]
                    NQ[s] = 0
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealSum: sum of dealer's cards (including hidden one)
    #dealA: number of all dealer's Aces, 
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    #Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    #Event loop
    while True:
        #Our state information does not take into account of number of cards
        #So it's ok to ignore the rule of winning if getting 5 cards without going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        if autoMC:
            #MC Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            MC_Policy_Evaluation(policy, states, 0.9, MCvalues, G)
        if autoTD:
            #TD Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            TD_Policy_Evaluation(policy, states, 0.9, TDvalues, NTD)
        if autoQL:
            #Q-Learning
            #For each state, compute the Q value of the action "Hit" and "Stand"
            Q_Learning(states, 0.9, Qvalues, NQ)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #Clicking the white buttons can start or pause the learning processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand):
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()):
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()):
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %f' % MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %f' % TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %f (Stand) %f' % (Qvalues[state][0], Qvalues[state][1]) , 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()

if __name__ == '__main__':
    main()

