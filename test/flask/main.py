from flask import Flask, send_file, jsonify, send_from_directory
from flask_cors import CORS  # 导入CORS模块
from plyfile import PlyData
import cv2
import numpy as np
import os
import shutil
from CAL import cal_dis

app = Flask(__name__)
CORS(app)  # 在应用上启用CORS

@app.route('/get_array', methods=['POST'])
def get_array():
    res = [0] * 10
    ##处理逻辑
    return jsonify(res)

def save_frames(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_dir = os.path.join(output_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)

    frames_paths = []

    for frame_number in range(total_frames):
        _, frame = cap.read()
        frame_path = os.path.join(frames_dir, f'frame_{frame_number}.jpg')
        cv2.imwrite(frame_path, frame)
        frames_paths.append(frame_path)

    return frames_paths

@app.route('/get_frames', methods=['POST'])
def get_frames():
    try:
        video_path = 'C:\\Users\\oewt\\Desktop\\datas\\1\\1.mp4'
        temp_dir = 'C:\\Users\\oewt\\Desktop\\temp_frames'

        frames_paths = save_frames(video_path, temp_dir)

        # 返回所有帧的文件路径
        return jsonify({'frames_paths': frames_paths})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get_frame/<frame_number>')
def get_frame(frame_number):
    temp_dir = 'C:\\Users\\oewt\\Desktop\\temp_frames\\frames\\'
    return send_from_directory(temp_dir, f'frame_{frame_number}.jpg')

@app.route('/get_video', methods=['POST'])
def get_video():
    video_path = 'C:\\Users\\oewt\\Desktop\\datas\\1\\1.mp4'
    return send_file(video_path, mimetype='video/mp4')


def convert_float32(value):
    if isinstance(value, float):
        return value
    elif isinstance(value, list):
        return [convert_float32(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(convert_float32(item) for item in value)
    return float(value)

@app.route('/get_point_cloud', methods=['POST'])
def get_point_cloud():
    point_cloud_path = 'C:\\Users\\oewt\\Desktop\\ply\\ply\\ground_truth.ply'

    # 读取PLY文件
    ply_data = PlyData.read(point_cloud_path)

    # 获取点云坐标数据
    vertex_data = ply_data['vertex']
    points = [{"x": convert_float32(vertex['x']),
               "y": convert_float32(vertex['y']),
               "z": convert_float32(vertex['z'])} for vertex in vertex_data]
    return jsonify(points)

if __name__ == '__main__':
    app.run(debug=True)
