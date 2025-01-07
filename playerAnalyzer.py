from datetime import datetime, timedelta
import requests as rq
import pandas as pd
import chess.pgn
import chessAnalyzer as ca

class PlayerAnalyzer:

    def __init__(self, playerName: str):
            """
            Initialise l'objet ChessAnalyzer avec une partie PGN.
            """
            self.player_name = playerName
            self.pgn_data = []
            self.analyzed_games = pd.DataFrame()
            self.max_months = 3
            self.max_games = 50


    def get_pgn_data(self, player_name: str):
        """
        Récupère les PGN des parties les plus récentes d'un joueur sur Chess.com, limité à 24 mois d'ancienneté.
        
        Args:
            player_name (str): Nom du joueur (par exemple "magnuscarlsen").
            max_games (int): Nombre maximum de parties à récupérer.
            max_months (int): Nombre maximum de mois à parcourir en arrière (par défaut 24).
        
        Returns:
            List[str]: Liste contenant les parties au format PGN.
        """
        games_pgn = []
        headers = {"User-Agent": "MyChessApp"}
        
        # Date actuelle
        now = datetime.now()
        start_date = now - timedelta(days=self.max_months * 30)  # Approximation de 30 jours par mois
        year = now.year
        month = now.month

        while len(games_pgn) < self.max_games:
            # Arrêt si on dépasse la période de 24 mois
            if datetime(year, month, 1) < start_date:
                break
            
            # Construire l'URL pour une année et un mois donnés
            url = f"https://api.chess.com/pub/player/{player_name}/games/{year}/{month:02d}"
            response = rq.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Erreur lors de la récupération des données pour {year}/{month:02d}")
            else:
                games = response.json().get('games', [])
                for game in games:
                    if 'pgn' in game:
                        games_pgn.append(game['pgn'])
                    if len(games_pgn) >= self.max_games:
                        break

            # Passer au mois précédent
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        return games_pgn
    

    def set_pgn_data(self):
        """
        Sets the PGN data for the player
        """
        self.pgn_data = self.get_pgn_data(self.player_name)

    def analyse_one_game(self, game_pgn):

        chessAnalyzer = ca.ChessAnalyzer(game_pgn)

        return {
            "trades": chessAnalyzer.count_trades(),
            # "queen_lifetime": chessAnalyzer.queen_lifetime(),
            "queen_moves": chessAnalyzer.queen_moves(),
            "piece_advancement": chessAnalyzer.piece_advancement(),
            "central_pawns": chessAnalyzer.central_pawns(),
            "game_length": chessAnalyzer.game_length(),
            "castling_type": chessAnalyzer.castling_type(),
            # "piece_moves": chessAnalyzer.piece_moves()
        }
    
    def analyse_games(self, games_pgn):
        """
        Analyse les parties données et stocke les résultats dans l'attribut analyzed_games
        Args:
            games_pgn (List[str]): Liste de parties au format PGN.
        """
        analyse = [self.analyse_one_game(game_pgn) for game_pgn in games_pgn]
        self.analyzed_games = pd.DataFrame(analyse)


if __name__ == "__main__":
    analyzer = PlayerAnalyzer("magnuscarlsen")

    analyzer.set_pgn_data()

    analyzer.analyse_games(analyzer.pgn_data)

    print(analyzer.analyzed_games.head(4))