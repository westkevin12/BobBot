from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/notifyOrder": {"origins": "https://www.extremevisiongaming.com", "https://extremevisiongaming.com", "https://app.extremevisiongaming.com"}})
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow WebSocket connections from any origin

@app.route('/notifyOrder', methods=['POST'])
def notify_order():
    try:
        data = request.get_json()
        # Assuming you want to broadcast the data to connected WebSocket clients
        socketio.emit('order_notification', data)  # Broadcast data to WebSocket clients
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print(f"Starting Flask App...")
    socketio.run(app, host='0.0.0.0', port=8049)
    