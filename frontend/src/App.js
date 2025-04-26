import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [screenshotsLoading, setScreenshotsLoading] = useState(false);
  const [modalImage, setModalImage] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setScreenshots([]);
    }
  };

  const fetchScreenshots = async (recordId) => {
    setScreenshotsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/screenshots/${recordId}/`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch screenshots");
      }

      setScreenshots(data.screenshots);
    } catch (err) {
      console.error("Error fetching screenshots:", err);
      setError(err.message || "An error occurred while fetching screenshots");
    } finally {
      setScreenshotsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) {
      setError("Please select an image first");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await fetch("http://localhost:8000/api/process-image/", {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to process image");
      }

      setResult(data);

      // Fetch screenshots if we have a record ID
      if (data.record_id) {
        fetchScreenshots(data.record_id);
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "An error occurred while processing the image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>RTC Document Processor</h1>
      </header>
      <main>
        <div className="upload-section">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="file-input"
          />
          {previewUrl && (
            <div className="image-preview">
              <img src={previewUrl} alt="Preview" />
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={!selectedImage || loading}
            className="process-button"
          >
            {loading ? "Processing..." : "Process Image"}
          </button>
        </div>

        {error && <div className="error-message">Error: {error}</div>}

        {result && (
          <div className="result-section">
            <h2>Extracted Information</h2>
            <div className="result-grid">
              <div className="result-item">
                <strong>Survey Number:</strong>{" "}
                {result.extracted_info["Survey Number"]}
              </div>
              <div className="result-item">
                <strong>Surnoc:</strong> {result.extracted_info["Surnoc"]}
              </div>
              <div className="result-item">
                <strong>Hissa:</strong> {result.extracted_info["Hissa"]}
              </div>
              <div className="result-item">
                <strong>Village:</strong> {result.extracted_info["Village"]}
              </div>
              <div className="result-item">
                <strong>Hobli:</strong> {result.extracted_info["Hobli"]}
              </div>
              <div className="result-item">
                <strong>Taluk:</strong> {result.extracted_info["Taluk"]}
              </div>
              <div className="result-item">
                <strong>District:</strong> {result.extracted_info["District"]}
              </div>
            </div>

            {result.scraper_result && (
              <div className="scraping-results">
                <h3>Scraping Results</h3>
                <div className="scraping-status">
                  <strong>Documents Found:</strong>{" "}
                  {result.scraper_result.length}
                </div>
              </div>
            )}

            {screenshotsLoading ? (
              <div className="screenshots-loading">Loading screenshots...</div>
            ) : screenshots.length > 0 ? (
              <div className="screenshots-section">
                <h3>Screenshots</h3>
                <div className="screenshots-grid">
                  {screenshots.map((screenshot, index) => (
                    <div key={index} className="screenshot-item">
                      <img
                        src={`http://localhost:8000${screenshot.url}`}
                        alt={screenshot.name}
                        className="screenshot-image"
                        style={{ cursor: "pointer" }}
                        onClick={() =>
                          setModalImage(
                            `http://localhost:8000${screenshot.url}`
                          )
                        }
                      />
                      <div className="screenshot-name">{screenshot.name}</div>
                      <a
                        href={`http://localhost:8000${screenshot.url}`}
                        download={screenshot.name}
                      >
                        <button>Download</button>
                      </a>
                    </div>
                  ))}
                </div>
                {modalImage && (
                  <div
                    style={{
                      position: "fixed",
                      top: 0,
                      left: 0,
                      width: "100vw",
                      height: "100vh",
                      background: "rgba(0,0,0,0.7)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      zIndex: 1000,
                    }}
                    onClick={() => setModalImage(null)}
                  >
                    <img
                      src={modalImage}
                      alt="Preview"
                      style={{
                        maxHeight: "90vh",
                        maxWidth: "90vw",
                        borderRadius: "8px",
                        background: "#fff",
                      }}
                    />
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
