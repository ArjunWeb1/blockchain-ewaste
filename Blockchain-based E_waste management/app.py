from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import time
import random
import json
import os

app = Flask(__name__)

# ------------------ FILE PATHS ------------------
DEVICES_FILE = 'devices.json'
BLOCKCHAIN_FILE = 'blockchain.json'
REWARDS_FILE = 'rewards.json'

# ------------------ LOAD DATA FROM FILES ------------------
def load_data(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return default

devices = load_data(DEVICES_FILE, [])
blockchain = load_data(BLOCKCHAIN_FILE, [])
users_rewards = load_data(REWARDS_FILE, {})

# ------------------ SAVE DATA TO FILES ------------------
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# ------------------ REALISTIC MATERIALS ------------------
device_materials = {
    'Mobile': ['Copper', 'Plastic', 'Glass', 'Aluminum', 'Gold (tiny trace)'],
    'Laptop': ['Aluminum', 'Copper', 'Plastic', 'Glass', 'Gold (tiny trace)'],
    'TV': ['Copper', 'Plastic', 'Glass', 'Steel'],
    'Battery': ['Lithium', 'Nickel', 'Cobalt', 'Plastic'],
    'Other': ['Plastic', 'Aluminum', 'Copper']
}

# ------------------ HOME PAGE ------------------
@app.route('/')
def index():
    return render_template('index.html', devices=devices, chain=blockchain, rewards=users_rewards)

# ------------------ REGISTER DEVICE ------------------
@app.route('/register', methods=['POST'])
def register_device():
    owner = request.form['owner']
    device_type = request.form['type']

    device = {
        'id': len(devices) + 1,
        'owner': owner,
        'type': device_type,
        'status': 'active',
        'materials': []
    }
    devices.append(device)
    save_data(DEVICES_FILE, devices)

    blockchain.append({
        'index': len(blockchain) + 1,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'data': f"{owner} registered {device_type}"
    })
    save_data(BLOCKCHAIN_FILE, blockchain)

    time.sleep(0.5)
    return redirect(url_for('index'))

# ------------------ SUBMIT DEVICE ------------------
@app.route('/submit/<int:id>')
def submit_device(id):
    for d in devices:
        if d['id'] == id:
            d['status'] = 'submitted'
            save_data(DEVICES_FILE, devices)

            blockchain.append({
                'index': len(blockchain) + 1,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': f"Device {id} submitted for recycling"
            })
            save_data(BLOCKCHAIN_FILE, blockchain)
            time.sleep(1)
    return redirect(url_for('index'))

# ------------------ RECYCLE DEVICE ------------------
@app.route('/recycle/<int:id>')
def recycle_device(id):
    for d in devices:
        if d['id'] == id and d['status'] != 'recycled':
            # Pick realistic materials
            materials_pool = device_materials.get(d['type'], device_materials['Other'])
            recovered = random.sample(materials_pool, k=random.randint(1, len(materials_pool)))
            d['materials'] = recovered
            d['status'] = 'recycled'
            save_data(DEVICES_FILE, devices)

            # Reward points
            reward_points = len(recovered) * 10
            users_rewards[d['owner']] = users_rewards.get(d['owner'], 0) + reward_points
            save_data(REWARDS_FILE, users_rewards)

            blockchain.append({
                'index': len(blockchain) + 1,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': f"Device {id} ({d['type']}) recycled - materials recovered: {', '.join(recovered)}"
            })
            save_data(BLOCKCHAIN_FILE, blockchain)
            time.sleep(1)
    return redirect(url_for('index'))

# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
