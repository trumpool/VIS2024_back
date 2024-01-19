import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [framesData, setFramesData] = useState({ framesPaths: [] });

  useEffect(() => {
    const getFramesData = async () => {
      try {
        // 使用 POST 请求获取帧数据
        const response = await axios.post('http://localhost:5000/get_frames');
        setFramesData(response.data);
        console.log("Frames Data:", response.data);
      } catch (error) {
        console.error("Error fetching frames data:", error);
      }
    };

    getFramesData();
  }, []); // The empty dependency array means this effect will run once after the component mounts.

  return (
    <div>
      <h1>Frames Data:</h1>
      {/* 直接输出第一帧 */}
      <img src={`http://localhost:5000/get_frame/0`} alt="First Frame" onError={() => console.error("Error loading first frame")} />
    </div>
  );
}

export default App;
