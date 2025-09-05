import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResults(null);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/analyze_url', { url });
      setResults(response.data);
    } catch (err) {
      console.error('API Error:', err);
      setError('An error occurred. Please check the URL and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>VeriMedia</h1>
        <p>Analyze any URL for authenticity and key insights.</p>
      </header>
      
      <main>
        <form onSubmit={handleSubmit} className="url-form">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL to analyze (e.g., a news article)"
            required
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {isLoading && <p>Loading...</p>}
        {error && <p className="error-message">{error}</p>}
        
        {results && (
          <div className="results-container">
            <h2>Analysis Results</h2>
            
            {results.text_summary && (
              <div className="analysis-card">
                <h3>Text Summary</h3>
                <p>{results.text_summary}</p>
              </div>
            )}
            
            {results.text_sentiment && (
              <div className="analysis-card">
                <h3>Text Sentiment</h3>
                <p>
                  Sentiment: <strong>{results.text_sentiment.label}</strong>
                </p>
                <p>
                  Confidence: <strong>{results.text_sentiment.score.toFixed(2)}</strong>
                </p>
              </div>
            )}
            
            {results.image_analysis.length > 0 && (
              <div className="analysis-card">
                <h3>Image Analysis</h3>
                {results.image_analysis.map((img, index) => (
                  <div key={index} className="image-result">
                    {img.base64_image && (
                      <img 
                        src={`data:image/jpeg;base64,${img.base64_image}`} 
                        alt="Analyzed content" 
                        className="analyzed-image" 
                      />
                    )}
                    {img.error && <p className="error-message">Error: {img.error}</p>}
                    
                    {img.vqa_answer && (
                      <p>
                        <strong>What's in this image?</strong> {img.vqa_answer}
                      </p>
                    )}
                    
                    {img.zero_shot_classification && (
                      <div>
                        <p><strong>Image Type:</strong></p>
                        <ul>
                          {img.zero_shot_classification.map((item, i) => (
                            <li key={i}>
                              {item.label}: <strong>{item.score.toFixed(2)}</strong>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {!results.text_summary && !results.image_analysis.length && (
              <p>No content found for analysis.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;