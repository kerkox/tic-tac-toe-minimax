import random
import string
import re


class TicTacToe:
    def __init__(self):
        self.board = []
        self.playerX = 'X'
        self.playerO = 'O'
        self.next_player = None
        self.players = []
        self.current_state = {}

    def start(self, type_player_1, type_player_2):
        initial_state = "".join([str(n) for n in range(9)])
        self.symbol_to_start(initial_state)
        self.create_board(initial_state)
        self.players = {self.playerX: type_player_1, self.playerO: type_player_2}
        self.show_board()
        self.next_move()

    def next_move(self):
        no_winner = True
        while no_winner:
            if self.players[self.next_player] == "user":
                self.next_move_human()
            else:
                self.next_move_pc(player_symbol=self.next_player, level=self.players[self.next_player])
            no_winner, status = self.next_player_game()
            if not no_winner:
                print(status, "\n")
                break

    def set_player_move(self, position: int, player_symbol: str):
        self.board[position] = player_symbol
        self.current_state = self.load_current_state(self.board)

    def load_current_state(self, board):
        current_sate = {}
        list_state = self.get_board_string(board)
        for i, state in enumerate(list_state):
            current_sate[i] = state
        return current_sate

    def next_move_human(self):
        valid_input = False
        while not valid_input:
            coordinates = input("Enter the coordinates: ")
            if self.validate_coordinates(coordinates):
                index = self.get_format_coordinates(coordinates)
                self.set_player_move(int(index), self.next_player)
                valid_input = True

    def next_player_game(self):
        self.set_next_player()
        self.show_board()
        status = self.check_status_game()
        no_winner = status == ""
        return no_winner, status

    def next_move_pc(self, player_symbol="O", level="easy"):
        if not self.is_positions_available(self.board):
            return
        if level == "easy":
            print('Making move level "easy": ')
            self.random_position_available(player_symbol)
        elif level == "medium":
            print('Making move level "medium": ')
            opponent_symbol = self.playerO if player_symbol == "X" else self.playerX
            valid = self.next_move_level_medium(player_symbol, opponent_symbol)
            if not valid:
                self.random_position_available(player_symbol)
        elif level == "hard":
            print('Making move level "hard"')
            opponent_symbol = self.playerO if player_symbol == "X" else self.playerX
            self.next_move_minimax(player_symbol, opponent_symbol)

    def next_move_minimax(self, player_symbol, opponent_symbol):
        cloned_board = self.get_cloned_board()
        best_spot = self.minimax(cloned_board, player_symbol, opponent_symbol, player_symbol)
        self.set_player_move(int(best_spot["index"]), player_symbol)

    def minimax(self, cloned_board, player_symbol: str, opponent_symbol: str, current_player: str):
        available_spots = self.get_positions_available(cloned_board)
        if self.check_winner(cloned_board) == opponent_symbol:
            return {"score": -10}
        elif self.check_winner(cloned_board) == player_symbol:
            return {"score": 10}
        elif len(available_spots) == 0:
            return {"score": 0}

        moves = []

        for spot in available_spots:
            move = {"index": cloned_board[int(spot)]}
            cloned_board[int(spot)] = current_player

            if current_player == player_symbol:
                result = self.minimax(
                    cloned_board,
                    player_symbol,
                    opponent_symbol,
                    current_player=opponent_symbol)
                move["score"] = result["score"]
            else:
                result = self.minimax(
                    cloned_board,
                    player_symbol,
                    opponent_symbol,
                    current_player=player_symbol
                )
                move["score"] = result["score"]

            cloned_board[int(spot)] = move["index"]

            moves.append(move)

        best_move = -1
        if current_player == player_symbol:
            best_score = -10_000
            for i, move in enumerate(moves):
                if move["score"] > best_score:
                    best_score = move["score"]
                    best_move = i
        else:
            best_score = 10_000
            for i, move in enumerate(moves):
                if move["score"] < best_score:
                    best_score = move["score"]
                    best_move = i

        return moves[best_move]

    def get_cloned_board(self):
        cloned_board = []
        for n in self.board:
            cloned_board.append(n)
        return cloned_board

    def next_move_level_medium(self, player_symbol, opponent_symbol=""):
        index_move = self.two_in_row_check_availability_to_win(player_symbol)
        if index_move == -1:
            index_move = self.two_in_row_check_availability_to_win(player_symbol, opponent_symbol)
        if index_move == -1:
            return False
        self.set_player_move(index_move, player_symbol)
        return True

    def get_vertical_values(self, board):
        vertical_values = []
        for i in range(3):
            column = f"{board[i]}{board[i+3]}{board[i+6]}"
            vertical_values.append(column)
        return vertical_values

    def two_in_row_check_availability_to_win(self, player_symbol: str, opponent_symbol=""):
        symbol_to_search = opponent_symbol if opponent_symbol != "" else player_symbol
        index_move = self.two_in_line_horizontal_search(self.board, symbol_to_search)
        if index_move == -1:
            index_move = self.tow_in_line_vertical_search(self.board, symbol_to_search)
        if index_move == -1:
            index_move = self.two_in_line_diagonal_search(self.board, symbol_to_search)

        return index_move

    def two_in_line_diagonal_search(self, board, symbol_to_search):
        index_move = -1
        diagonal1 = [board[i] for i in [0, 4, 8]]
        diagonal2 = [board[i] for i in [2, 4, 6]]

        index_player1, index_available1 = self.get_index_possible_winner(''.join(diagonal1), symbol_to_search)
        if index_player1 != -1 and index_available1 != -1:
            index_move = int(index_available1)
            return index_move

        index_player2, index_available2 = self.get_index_possible_winner(''.join(diagonal2), symbol_to_search)
        if index_player2 != -1 and index_available2 != -1:
            index_move = int(index_available2)
            return index_move
        return index_move

    def two_in_line_horizontal_search(self, board, symbol_to_search):
        index_move = -1
        board_horizontal_str = self.get_board_string(board)
        for i, row in enumerate(board_horizontal_str):
            index_player, index_available = self.get_index_possible_winner(row, symbol_to_search)
            if index_player != -1 and index_available != -1:
                index_move = int(index_available)
                break
        return index_move

    def tow_in_line_vertical_search(self, board, symbol_to_search):
        index_move = -1
        board_vertical_str = self.get_vertical_values(board)
        for i, row in enumerate(board_vertical_str):
            index_player, index_available = self.get_index_possible_winner(row, symbol_to_search)
            if index_player != -1 and index_available != -1:
                index_move = int(index_available)
                break
        return index_move
    def get_index_possible_winner(self, row, player_symbol: str):
        index_player = row.find(player_symbol * 2)
        if index_player == -1:
            result_player = re.search(rf"{player_symbol}\d{player_symbol}", row)
            index_player = -1 if result_player is None else result_player.span()[0]

        result_available = re.search(r'\d', row)
        index_available = -1 if result_available is None else result_available.group()
        return index_player, index_available

    def get_board_string(self, board) -> list[str]:
        part_length = 3
        return ["".join(board[i:i + part_length]) for i in range(0, len(board), part_length)]

    def random_position_available(self, player_symbol="O"):
        random.seed = 15
        position = random.choice(self.get_positions_available(self.board))
        self.set_player_move(int(position), player_symbol)

    def get_positions_available(self, board):
        positions_available = [pos for pos in board if pos in string.digits]
        return positions_available

    def check_status_game(self):
        status = ""
        winner = self.check_winner(self.board)
        if winner != "":
            status = f"{winner} wins"
        elif not self.is_positions_available(self.board):
            status = "Draw"
        return status

    def is_positions_available(self, board):
        return any(pos in string.digits for pos in board)

    def check_winner(self, board):
        winner_positions = [
            # diagonals:
            [0, 4, 8],
            [2, 4, 6],

            # horizontal:
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],

            # vertical
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
        ]
        winner = None
        for positions in winner_positions:
            winner = ""
            for index in positions:
                winner += board[index]
            if winner.count(self.playerX) == 3:
                winner = self.playerX
                break
            elif winner.count(self.playerO) == 3:
                winner = self.playerO
                break
            else:
                winner = ""
        return winner

    def set_next_player(self):
        if self.next_player == self.playerX:
            self.next_player = self.playerO
        else:
            self.next_player = self.playerX

    def get_format_coordinates(self, coordinates):
        positions = {
            "11": 0, "12": 1, "13": 2,
            "21": 3, "22": 4, "23": 5,
            "31": 6, "32": 7, "33": 8
        }
        return positions[coordinates.replace(" ", "")]

    def validate_coordinates(self, coordinates):
        if not self.is_coordinates_number(coordinates):
            print("You should enter numbers!")
            return False
        if not self.is_coordinates_in_correct_range(coordinates):
            print("Coordinates should be from 1 to 3!")
            return False
        if not self.is_available_coordinate(coordinates):
            print("This cell is occupied! Choose another one!")
            return False
        return True

    def is_coordinates_in_correct_range(self, coordinate):
        coordinates = [int(n) for n in coordinate.split()]
        return all(1 <= n <= 3 for n in coordinates)

    def is_available_coordinate(self, coordinate):
        position = self.get_format_coordinates(coordinate)
        return self.board[int(position)] in string.digits

    def is_coordinates_number(self, coordinates):
        numbers = coordinates.split()
        if len(numbers) != 2:
            return False
        return all(n.isdigit() and len(n) == 1 for n in numbers)

    def show_board(self):
        print(self.render_board(self.board))

    def render_board(self, board):
        game = "---------\n"
        for n in range(9):
            game += "| " if n % 3 == 0 else ""
            game += " " if board[n] in string.digits else board[n]
            game += " "
            game += "|\n" if (n + 1) % 3 == 0 else ""
        game += "---------\n"
        return game

    def create_board(self, initial_state):
        self.board = []
        for symbol in initial_state:
            self.board.append(symbol)

    def symbol_to_start(self, initial_state):
        count_x = initial_state.upper().count('X')
        count_o = initial_state.upper().count('O')
        if count_x > count_o:
            self.next_player = self.playerO
        else:
            self.next_player = self.playerX


def input_parameters_start():
    valid_parameters = False
    while not valid_parameters:
        parameters = input("Input command: ").split()
        if parameters[0] == "exit":
            break
        if len(parameters) < 3:
            print("Bad parameters!")
            continue
        if parameters[0] == "start":
            game_tictactoe = TicTacToe()
            game_tictactoe.start(*parameters[1:])


input_parameters_start()
