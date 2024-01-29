from flask import Flask, send_file, jsonify, send_from_directory, request
from flask_cors import CORS  # 导入CORS模块
from flask_socketio import SocketIO, emit
from plyfile import PlyData
import cv2
import numpy as np
import os
import shutil
import tempfile

app = Flask(__name__)
CORS(app)  # 在应用上启用CORS
socketio = SocketIO(app, cors_allowed_origins="*")

video_path = os.path.dirname(os.path.realpath(__file__))
point_cloud_xyz = None
point_cloud_color = None
frames = None

@app.route('/upload', methods=['POST'])
def upload():
    global video_path
    # 获取上传的视频文件
    video_file = request.files['video']

    # 储存视频
    video_path = os.path.join(video_path, video_file.filename)
    video_file.save(video_path)

    # 处理视频，按帧拆成图片
    frames = process_video(video_path)

    # 处理点云数据
    point_cloud = process_point_cloud()

    # 计算相机（每一帧的贡献值、相机高度，位置等信息，目前先只是传一个一维数组）
    cameras = process_cameras()


    # 构建返回给前端的数据
    response_data = {
        'frames': frames,
        'point_cloud': point_cloud,
        'camera': cameras  # 示例需要替换为实际数据
    }

    return jsonify(response_data)

def process_video(video_path):
    #聚类问题还需要进一步补充
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # frames.append(frame.tolist()) #这里tolist性能可能不佳，需要进一步修改
        frames.append(frame)
    return frames

def process_point_cloud():
    # 调用splatting（或者其他方法），先生成一些随机值代替
    global point_cloud_xyz, point_cloud_color
    num_points = 100
    point_cloud_xyz = np.random.rand(num_points * 3)  # 生成随机坐标
    point_cloud_color = np.random.randint(0, 255, size=(num_points, 3))  # 生成随机颜色,rgb信息

    point_cloud_data = {
        'coordinates': point_cloud_xyz.tolist(),
        'colors': point_cloud_color.tolist()
    }

    return point_cloud_data

def process_cameras():
    # Todo
    # 计算每个相机的贡献
    return [1,2,3,4]

@app.route('/process_point_cloud', methods=['POST'])
def process_point_cloud():
    try:
        data = request.get_json()
        point_cloud_info = data.get('pointCloudInfo', [])

        # 在这里进行点云信息的处理
        processed_result = process_point_cloud_info(point_cloud_info)

        return jsonify({'result': processed_result})
    except Exception as e:
        return jsonify({'error': str(e)})

def process_point_cloud_info(point_cloud_info):
    # 在这里进行点云信息的处理示例，这里只是简单的返回使用的点的数量
    num_used_points = sum(point_cloud_info)
    return f'Number of used points: {num_used_points}'


if __name__ == '__main__':
    app.run(debug=True)
