import flask
from flask import request, jsonify, Flask
import playerAnalyzer as pa
from flask_cors import CORS
import requests as rq 

app = Flask(__name__)
CORS(app)  # Autorise les requêtes cross-origin

import chess
import chess.engine

# engine = chess.engine.SimpleEngine.popen_uci("C:/Users/lboitel/Documents/PC-30-11/perso/chess-me/stockfish/stockfish.exe")
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish_exe")

# Définir une route de base (GET)
@app.route('/')
def home():
    return "Bienvenue sur l'API Flask !"

# Route API pour obtenir des données (GET)
@app.route('/player/analysis', methods=['GET'])
def generate_analysis():
    player_name = request.args.get('player_name')
    print(player_name)
    analyzer = pa.PlayerAnalyzer(player_name)
    analyzer.set_pgn_data()
    analyzer.analyse_games(analyzer.pgn_data)

    data = analyzer.analyzed_games.mean(numeric_only=True).to_dict()
    data['number_games'] = analyzer.analyzed_games.shape[0]

    headers = {"User-Agent": "MyChessApp"}

    elo = rq.get(url=f"https://api.chess.com/pub/player/{player_name}/stats", headers= headers).json()['chess_rapid']["last"]["rating"]
    if int(elo) < 1320:
        elo = 1320

    data['elo'] = elo

    engine.configure({
        "Skill Level": 10,  # Niveau de force
        "UCI_LimitStrength": True,  # Limitation de l'ELO
        "UCI_Elo": int(elo),  # ELO cible
        # "UCI_Contempt": 10,  # Privilégier les parties agressives (éviter les nulles)
        "Hash": 512,  # 512 Mo pour le cache
        # "Use NNUE": True,  # Utilisation du réseau neuronal pour l'évaluation
    })

    return jsonify(data)  # Retourne un JSON

@app.route('/next_move', methods=['GET'])
def calculate_next_move():
    fen = request.args.get('fen')  # Position actuelle en notation FEN
    if not fen:
        return jsonify({"error": "No FEN position provided"}), 400

    # Initialisation de l'échiquier
    board = chess.Board(fen)
    # Calcul du prochain coup
    result = engine.play(board, chess.engine.Limit(time=1))
    # Appliquer le coup sur l'échiquier
    board.push(result.move)

    # Retourner la position FEN après le coup de l'IA
    return jsonify({"fen": board.fen()})
  # Renvoie le coup en format UCI

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)  # mode debug pour rechargement automatique