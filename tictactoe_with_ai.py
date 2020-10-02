import random
from abc import abstractmethod
import pickle
import os.path
from enum import Enum


class GameResult(Enum):
    WIN_X = 'X wins'
    WIN_O = 'O wins'
    DRAW = 'Draw'
    IN_PROGRESS = 'Game not finished'
    WRONG_POSITION = 'Wrong state!'


class TicTacToe:
    # Такой хардкод – не гуд. Если захочется передалать игру в 4x4/NxN, то нужно будет много хардкодить
    MEANINGFUL_POSITIONS = ((0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows, columns, diagonals
                            (0, 3, 6), (1, 4, 7), (2, 5, 8),
                            (0, 4, 8), (2, 4, 6))

    def __init__(self):
        self._state = [' '] * 9
        self._turn = 'X'
        self._opp_turn = 'O'
        self._player = None
        self._next_player = None

    def reset(self):
        self._state = [' '] * 9
        self._turn = 'X'
        self._opp_turn = 'O'
        self._player = None
        self._next_player = None

    def get_state(self):
        return self._state

    def get_xo(self):
        return self._turn, self._opp_turn

    def set_state(self, state):
        self._state = state

    def set_players(self, player1, player2):
        self._player = player1
        self._next_player = player2

    def get_players(self):
        return self._player, self._next_player

    def print_state(self):
        print('y^--------')
        print('3|', self._state[0], self._state[1], self._state[2], '|')
        print('2|', self._state[3], self._state[4], self._state[5], '|')
        print('1|', self._state[6], self._state[7], self._state[8], '|')
        print(' -------->x')
        print('   1 2 3')

    def state_analyze(self):
        """
        Checking state of the game. Is the game finished and how
        """
        wins = ''
        for pos in self.MEANINGFUL_POSITIONS:
            if self._state[pos[0]] == self._state[pos[1]] == self._state[pos[2]] \
                    and self._state[pos[0]] != ' ':
                wins += self._state[pos[0]]
        if wins == '' and ' ' in self._state:
            return GameResult.IN_PROGRESS
        elif wins == '' and ' ' not in self._state:
            return GameResult.DRAW
        elif wins == 'X':
            return GameResult.WIN_X
        elif wins == 'O':
            return GameResult.WIN_O
        else:
            return GameResult.WRONG_POSITION

    def change_turn(self):
        self._turn, self._opp_turn = self._opp_turn, self._turn
        self._player, self._next_player = self._next_player, self._player


class TicTacToeUser:
    POSITION = {'1 3': 0, '2 3': 1, '3 3': 2,  # translating x,y coordinates to position in state list
                '1 2': 3, '2 2': 4, '3 2': 5,
                '1 1': 6, '2 1': 7, '3 1': 8, }
    NAME = 'User'

    def get_name(self):
        return self.NAME

    @staticmethod
    def make_move(state, xo):
        """
        get coordinates from user, validate it, and make a move
        """
        while True:
            x_y = input(f'Enter the coordinates for "{xo}" (x y): ')
            if TicTacToeUser._validate_input(state, x_y):
                state[TicTacToeUser.POSITION[x_y]] = xo
                return state

    @staticmethod
    def _validate_input(state, x_y):
        """
        Validating user input: 2 integers from 1 to 3 separated by a space
        """
        x_y_list = x_y.split()
        if len(x_y_list) == 2 and x_y_list[0].isdigit() and x_y_list[1].isdigit():
            if 0 < int(x_y_list[0]) < 4 and 0 < int(x_y_list[1]) < 4:
                if state[TicTacToeUser.POSITION[x_y]] == ' ':
                    return True
                else:
                    print('This cell is occupied! Choose another one!')
            else:
                print('Coordinates should be from 1 to 3!')
        else:
            print('You should enter two numbers separated by space!')
        return False


# Вынести все AI в отдельный модуль.
# Это поможет отделить логику игры от логики AI
class TicTacToeAI:

    @abstractmethod
    def get_name(self):
        pass

    @staticmethod
    @abstractmethod
    def make_move(state, xo):
        pass

    @staticmethod
    def _empty_indexes(state):
        return [i for i, idx in enumerate(state) if idx == ' ']


class TicTacToeEasyAI(TicTacToeAI):
    NAME = 'EasyAI'

    def get_name(self):
        return self.NAME

    @staticmethod
    def make_move(state, xo):
        """
        easy AI, just random moves
        """
        state[random.choice(TicTacToeAI._empty_indexes(state))] = xo
        print(f'Making move level "easy" with "{xo}"')
        return state


class TicTacToeMediumAI(TicTacToeAI):
    NAME = 'MediumAI'

    def get_name(self):
        return self.NAME

    @staticmethod
    def make_move(state, xo):
        """
        medium AI, if two Xs or Os in one line it uses it, otherwise random move
        """
        ox = 'O' if xo == 'X' else 'X'
        if TicTacToeMediumAI._ready_to_win(state, xo):
            state[int(TicTacToeMediumAI._ready_to_win(state, xo))] = xo
            print(f'Making move level "medium" with "{xo}"')
            return state
        elif TicTacToeMediumAI._ready_to_win(state, ox):
            state[int(TicTacToeMediumAI._ready_to_win(state, ox))] = xo
            print(f'Making move level "medium" with "{xo}"')
            return state
        state[random.choice(TicTacToeAI._empty_indexes(state))] = xo
        print(f'Making move level "medium" with "{xo}"')
        return state

    @staticmethod
    def _ready_to_win(state, xo):
        """
        helper function for medium AI, determines if X or O player ready to win in one move
        """
        for pos in TicTacToe.MEANINGFUL_POSITIONS:
            line = state[pos[0]] + state[pos[1]] + state[pos[2]]
            if line.count(xo) == 2 and ' ' in line:
                return str(pos[line.index(' ')])
        return


class MinMaxResult(Enum):
    WIN = 1
    LOOSE = -1
    DRAW = 0


class TicTacToeHardAI(TicTacToeAI):
    BEST_MOVES_FILE = 'moves.pickle'
    NAME = 'HardAI'

    def __init__(self):  # reading best moves from file
        self._pickles = {}
        if os.path.isfile(TicTacToeHardAI.BEST_MOVES_FILE):
            with open(TicTacToeHardAI.BEST_MOVES_FILE, 'rb') as f:
                self._pickles = pickle.load(f)

    def __del__(self):  # dumping best moves to file
        with open(TicTacToeHardAI.BEST_MOVES_FILE, 'wb') as f:
            pickle.dump(self._pickles, f)

    def get_name(self):
        return self.NAME

    def make_move(self, state, xo):
        """
        hard AI, check for best move in self.pickles, if not found: use minimax on every possible move
        randomly select from the best moves, write best moves to BEST_MOVES_FILE on exit
        """

        if tuple(state) in self._pickles:
            best_moves = self._pickles[tuple(state)]
        else:
            new_state = state[:]
            moves = [' '] * 9
            for idx in TicTacToeAI._empty_indexes(state):
                new_state[idx] = xo
                moves[idx] = TicTacToeHardAI._min_max(new_state, xo)
                new_state[idx] = ' '
            best_moves = [i for i, n in enumerate(moves) if (n == 1
                                                             or n == 0 and 1 not in moves
                                                             or n == -1 and 1 not in moves and 0 not in moves)]
            self._pickles[tuple(state)] = best_moves
        state[random.choice(best_moves)] = xo
        print(f'Making move level "hard" with "{xo}"')
        return state

    @staticmethod
    def _min_max(state, xo):
        """
        minimax recursive function. goes all over the tree, MAX on player turn, MIN on opponent turn
        """
        # перенести логику в TicTacToe
        changing_xo = 'X' if state.count('X') == state.count('O') else 'O'
        win = TicTacToeHardAI._min_max_win(state, xo).value
        if win:
            return win
        elif len(TicTacToeHardAI._empty_indexes(state)) == 0:
            return 0
        scores = []
        new_state = state[:]
        for idx in TicTacToeHardAI._empty_indexes(state):
            new_state[idx] = changing_xo
            scores.append(TicTacToeHardAI._min_max(new_state, xo))
            new_state[idx] = ' '
        return max(scores) if changing_xo == xo else min(scores)

    @staticmethod
    def _min_max_win(state, xo):
        """
        helper function for minimax,
        returns +1 if X (or O) already wins and -1 if O (or X) already wins
        """
        for pos in TicTacToe.MEANINGFUL_POSITIONS:
            if state[pos[0]] == state[pos[1]] == state[pos[2]]:
                if state[pos[0]] == xo:
                    return MinMaxResult.WIN
                elif state[pos[0]] != ' ':
                    return MinMaxResult.LOOSE
        return MinMaxResult.DRAW


class Players(Enum):
    USER = TicTacToeUser
    EASY = TicTacToeEasyAI
    MEDIUM = TicTacToeMediumAI
    HARD = TicTacToeHardAI


class Commands(Enum):
    USER = 'user'
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


def main():
    print('''
possible commands: "start <player1> <player2>", "exit"
possible players: "user", "easy", "medium", "hard"
coordinates are in form "x y" <x> - columns, <y> - rows, "1 1" - left bottom corner
"X" plays first
        ''')

    game = TicTacToe()

    user = Players.USER.value()
    easy = Players.EASY.value()
    medium = Players.MEDIUM.value()
    hard = Players.HARD.value()

    players = {
        Commands.USER.value: user,
        Commands.EASY.value: easy,
        Commands.MEDIUM.value: medium,
        Commands.HARD.value: hard
    }

    #  вынести бесконечный цикл в отдельную функцию

    possible_commands = [item.value for item in Commands]
    while True:
        command = input('Input command: ').split()
        if len(command) == 1 or len(command) == 3:
            if command[0] == 'start' and command[1] in possible_commands and command[2] in possible_commands:
                if command[1] == 'user' or command[2] == 'user':
                    game.print_state()
                game.set_players(players[command[1]], players[command[2]])
                while game.state_analyze() == GameResult.IN_PROGRESS:
                    game.set_state(game.get_players()[0].make_move(game.get_state(), game.get_xo()[0]))
                    game.print_state()
                    game.change_turn()
                    print()
                if game.state_analyze() == GameResult.WIN_O or game.state_analyze() == GameResult.WIN_X:
                    print(f'{game.get_players()[1].get_name()} wins with "{game.get_xo()[1]}"\n')
                elif game.state_analyze() == GameResult.DRAW:
                    print('Draw\n')
                game.reset()
            elif command[0] == 'exit':
                break
            else:
                print('Bad parameters!')
        else:
            print('Bad parameters!')


if __name__ == '__main__':
    main()
