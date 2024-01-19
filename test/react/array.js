import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [dataArray, setDataArray] = useState([]);

  useEffect(() => {
    const getArrayData = async () => {
      try {
        const response = await axios.post('http://localhost:5000/get_array');
        setDataArray(response.data);
        console.log("Array Data:", response.data);
      } catch (error) {
        console.error("Error fetching array data:", error);
      }
    };

    getArrayData();
  }, []); // 空的依赖数组表示这个效果会在组件挂载后运行一次。

  return (
    <div>
      <h1>Array Data:</h1>
      <ul>
        {dataArray.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
