import flask
from flask import request, jsonify, Flask
import playerAnalyzer as pa

app = Flask(__name__)

import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("C:/Users/lboitel/Documents/PC-30-11/perso/chess-me/stockfish/stockfish.exe")

# Définir une route de base (GET)
@app.route('/')
def home():
    return "Bienvenue sur l'API Flask !"

# Route API pour obtenir des données (GET)
@app.route('/player/analysis', methods=['GET'])
def generate_analysis():
    player_name = request.args.get('player_name')
    print(player_name)
    # Données simples simulées
    analyzer = pa.PlayerAnalyzer(player_name)
    analyzer.set_pgn_data()
    analyzer.analyse_games(analyzer.pgn_data)

    print(analyzer.analyzed_games.mean(numeric_only=True))

    data = analyzer.analyzed_games.head(10).to_dict()

    engine.configure({
        "Skill Level": 15,  # Niveau de force
        "UCI_LimitStrength": True,  # Limitation de l'ELO
        "UCI_Elo": 800,  # ELO cible
        "UCI_Contempt": 10,  # Privilégier les parties agressives (éviter les nulles)
        "Hash": 512,  # 512 Mo pour le cache
        "Use NNUE": True,  # Utilisation du réseau neuronal pour l'évaluation
    })

    return jsonify(data)  # Retourne un JSON


# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)  # mode debug pour rechargement automatique