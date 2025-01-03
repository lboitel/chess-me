import chess.pgn
from io import StringIO
import requests as rq 

headers = {
    "User-Agent": "Chess-me/1.0"
}
chess_moves_temp = rq.get(url = "https://api.chess.com/pub/player/magnuscarlsen/games/2024/12", headers=headers).json()['games'][1]['pgn']

class ChessAnalyzer:

    def __init__(self, pgn_data: str):
        """
        Initialise l'objet ChessAnalyzer avec une partie PGN.
        """
        pgn = StringIO(pgn_data)  # Convertir le PGN en flux de texte
        self.game = chess.pgn.read_game(pgn)  # Charger la partie

    def count_trades(self) -> int:
        """
        Compte le nombre d'échanges (captures) dans la partie.
        
        Returns:
            int: Nombre d'échanges de pièces.
        """
        
        board = chess.Board()
        num_trades = 0
        for move in self.game.mainline_moves():
            if board.is_capture(move):  # Vérifie si le coup capture une pièce
                num_trades += 1
            board.push(move)  # Appliquer le coup pour avancer la position
        
        return num_trades
    

    def game_length(self) -> int:
        """
        Retourne le nombre total de coups dans la partie.
        """
        return len(list(self.game.mainline_moves()))

    def queen_lifetime(self) -> int:
        """
        Retourne le nombre de coups pendant lesquels la reine reste sur l'échiquier.
        """
        board = chess.Board()
        queen_squares = {chess.D1, chess.D8}  # Cases initiales des reines
        move_count = 0
        for move in self.game.mainline_moves():
            if board.piece_at(move.to_square) and board.piece_at(move.to_square).piece_type == chess.QUEEN:
                queen_squares.discard(move.to_square)
            if not queen_squares:  # Les deux reines ont été prises
                break
            move_count += 1
            board.push(move)
        return move_count

    def central_pawns(self) -> int:
        """
        Retourne le nombre moyen de pions centraux présents dans la partie.
        """
        board = chess.Board()

        central_squares = {chess.D4, chess.D5, chess.E4, chess.E5}
        total_pawns = 0
        move_count = 0

        for move in self.game.mainline_moves():
            board.push(move)
            pawns = sum(1 for square in central_squares if board.piece_at(square) and board.piece_at(square).piece_type == chess.PAWN)
            total_pawns += pawns
            move_count += 1

        return total_pawns // max(1, move_count)

    def piece_advancement(self) -> int:
        """
        Retourne le nombre total de coups où une pièce avance dans le camp adverse.
        """
        board = chess.Board()
        advancement_count = 0
        for move in self.game.mainline_moves():
            rank = chess.square_rank(move.to_square)
            if (board.turn and rank >= 4) or (not board.turn and rank <= 3):
                advancement_count += 1
            board.push(move)
        return advancement_count

    def queen_moves(self) -> int:
        """
        Retourne le nombre de mouvements de la dame dans la partie.
        """
        board = chess.Board()
        queen_moves = 0
        for move in self.game.mainline_moves():
            piece = board.piece_at(move.from_square)
            if piece and piece.piece_type == chess.QUEEN:
                queen_moves += 1
            board.push(move)
        return queen_moves

    def castling_type(self) -> str:
        """
        Retourne le type de roque effectué par le joueur blanc.
        """
        board = chess.Board()
        white_king_side = False
        white_queen_side = False

        for move in self.game.mainline_moves():
            if board.is_castling(move):
                if board.turn and move.to_square in {chess.G1, chess.G8}:
                    white_king_side = True
                elif board.turn and move.to_square in {chess.C1, chess.C8}:
                    white_queen_side = True
            board.push(move)

        if white_king_side and white_queen_side:
            return "Both"
        elif white_king_side:
            return "King-side"
        elif white_queen_side:
            return "Queen-side"
        else:
            return "None"

    def piece_moves(self) -> dict:
        """
        Retourne le nombre de déplacements de chaque type de pièce.
        """
        board = chess.Board()
        piece_counts = {chess.PAWN: 0, chess.KNIGHT: 0, chess.BISHOP: 0, chess.ROOK: 0, chess.QUEEN: 0, chess.KING: 0}

        for move in self.game.mainline_moves():
            piece = board.piece_at(move.from_square)
            if piece:
                piece_counts[piece.piece_type] += 1
            board.push(move)

        return {
            "Pawns": piece_counts[chess.PAWN],
            "Knights": piece_counts[chess.KNIGHT],
            "Bishops": piece_counts[chess.BISHOP],
            "Rooks": piece_counts[chess.ROOK],
            "Queens": piece_counts[chess.QUEEN],
            "Kings": piece_counts[chess.KING],
        }

# Exemple d'utilisation
if __name__ == "__main__":
    pgn_data = chess_moves_temp  # PGN récupéré via l'API
    analyzer = ChessAnalyzer(pgn_data)
    # analyzer.display_game_info()

    print(f"Nombre d'échanges de pièces : {analyzer.count_trades()}")

    print(f"Longueur de la partie : {analyzer.game_length()} coups")
    print(f"Durée de vie de la dame : {analyzer.queen_lifetime()} coups")

    print(f"Nombre moyen de pions centraux : {analyzer.central_pawns()}")
    print(f"Nombre de déplacements vers l'avant : {analyzer.piece_advancement()}")
    print(f"Nombre de déplacements de la dame : {analyzer.queen_moves()}")
    print(f"Type de roque : {analyzer.castling_type()}")
    print(f"Nombre de mouvements par pièce : {analyzer.piece_moves()}")

    
    

