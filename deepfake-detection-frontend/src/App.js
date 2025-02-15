import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [prediction, setPrediction] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    setLoading(true);
    setMessage("⏳ Processing video...");
    setPrediction("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      console.log("🚀 Backend Response:", response.data); // Debugging Log
      if (response.data && response.data.prediction) {
        setMessage(response.data.message);
        setPrediction(response.data.prediction);
      } else {
        setMessage("❌ No prediction received. Please check backend logs.");
      }
    } catch (error) {
      setMessage("❌ Error processing the video. Please try again.");
      console.error("Upload Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="App-header">
        <h1>Deepfake Video Detector</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="file-upload" className="custom-file-upload">
            {file ? file.name : "Choose a video file (.mp4)"}
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".mp4"
            onChange={handleFileChange}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Upload and Detect"}
          </button>
        </form>

        {message && <p className="message">{message}</p>}

        {prediction && (
          <p className="prediction">
            Prediction: <span>{prediction}</span>
          </p>
        )}
      </div>
    </div>
  );
}

export default App;