import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [pointCloud, setPointCloud] = useState([]);

  useEffect(() => {
    const getPointCloudData = async () => {
      try {
        // 使用 POST 请求，并传递空的请求体
        const response = await axios.post('http://localhost:5000/get_point_cloud');
        setPointCloud(response.data.slice(0, 10));  // 只获取前十个点
        console.log("PointCloud Data:", response.data);
      } catch (error) {
        console.error("Error fetching point cloud data:", error);
      }
    };

    getPointCloudData();
  }, []); // The empty dependency array means this effect will run once after the component mounts.

  return (
    <div>
      <h1>Point Cloud Data:</h1>
      <ul>
        {pointCloud.map((point, index) => (
          <li key={index}>{`X: ${point.x}, Y: ${point.y}, Z: ${point.z}`}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
