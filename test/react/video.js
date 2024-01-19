import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [videoData, setVideoData] = useState(null);

  useEffect(() => {
    const getVideoData = async () => {
      try {
        // 使用 POST 请求
        const response = await axios.post('http://localhost:5000/get_video', {}, { responseType: 'blob' });

        // 创建一个 Blob URL，用于设置 <video> 的 src
        const blob = new Blob([response.data], { type: 'video/mp4' });
        const videoUrl = URL.createObjectURL(blob);

        setVideoData(videoUrl);
        console.log("Video Data:", videoUrl);
      } catch (error) {
        console.error("Error fetching video data:", error);
      }
    };

    getVideoData();
  }, []); // The empty dependency array means this effect will run once after the component mounts.

  return (
    <div>
      <h1>Video Data:</h1>
      {videoData && (
        <video controls>
          <source src={videoData} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
}

export default App;
