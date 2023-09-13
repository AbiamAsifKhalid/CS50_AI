"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    moves =0
    if board == initial_state():
        return X
    
    for row in range(3):
        for col in range (3):
            if board[row][col] == EMPTY:
                moves += 1
    
    if moves%2 == 0:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    allaction = set()
    for row in range(3):
        for col in range (3):
            if board[row][col] == EMPTY:
                allaction.add((row, col))
    return allaction

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)
    cplayer = player(new_board)
    row, col = action

    if 0>row>2 or 0>col>2:
        raise Exception ("Invalid Action")
    
    new_board[row][col] = cplayer

    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range (3):
        if board[i][0]==board[i][1]==board[i][2]== X:
                return X
        elif board[i][0]==board[i][1]==board[i][2]==O:
                return O
    
    for j in range (3):
        if board[0][j]==board[1][j]==board[2][j]== X:
                return X
        elif board[0][j]==board[1][j]==board[2][j]== O:
                return O

    if board[0][0] == board[1][1] == board[2][2]== X:
        return X
    elif board[0][0] == board[1][1] == board[2][2]== O:
        return O

    if board[0][2] == board[1][1] == board[2][0]== X:
        return X
    elif board[0][2] == board[1][1] == board[2][0]== O:
        return O

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    for row in range(3):
        for col in range (3):
            if board[row][col]  == EMPTY:
                return False

    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else: 
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    moves=0
    for row in range(3):
        for col in range (3):
            if board[row][col] == EMPTY:
                moves += 1
    
    if moves==9:
        return (0,1)

    def minval(board):
        if terminal(board):
            return utility(board),()
        v = 100000000000000000
        move=()
        for action in actions(board):
            vmin = maxval(result(board,action))[0]
            if vmin < v:
                v = vmin
                move = action
        return v,move

    def maxval(board):
        if terminal(board):
            return utility(board),()
        v = -100000000000000000
        move=()
        for action in actions(board):
            vmax = minval(result(board,action))[0]
            if vmax > v:
                v = vmax
                move = action
        return v,move
    
    if player(board) == X:
        v,bestmove = maxval(board)
    elif player(board) == O:
        v,bestmove = minval(board)
    else: 
        bestmove = None
    return bestmove