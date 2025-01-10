import flask
from flask import request, jsonify, Flask
import playerAnalyzer as pa
from flask_cors import CORS

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

    engine.configure({
        "Skill Level": 10,  # Niveau de force
        "UCI_LimitStrength": True,  # Limitation de l'ELO
        "UCI_Elo": 1330,  # ELO cible
        # "UCI_Contempt": 10,  # Privilégier les parties agressives (éviter les nulles)
        "Hash": 512,  # 512 Mo pour le cache
        # "Use NNUE": True,  # Utilisation du réseau neuronal pour l'évaluation
    })
    
    return jsonify(data)  # Retourne un JSON


# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)  # mode debug pour rechargement automatique