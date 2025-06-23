import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [jobInfo, setJobInfo] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/get-job-details")
      .then((res) => res.json())
      .then((data) => {
        setJobInfo(data);
      })
      .catch((err) => {
        console.error("Error fetching job details:", err);
        setError("Could not load job details. Please try refreshing the page.");
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!resume) {
      setError("Please upload your resume PDF.");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null); // Clear previous results

    const formData = new FormData();
    formData.append("candidate_name", name);
    formData.append("candidate_email", email);
    formData.append("resume", resume);

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze-resume/', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.detail || "Error analyzing resume");
      }
    } catch (err) {
      console.error(err);
      setError("Network error. Please check your connection and try again.");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header className="navbar">
        <h1 className="navbar-title">Job Application Agent</h1>
      </header>

      <main className="main-content">
        <div className="job-details-column">
          {jobInfo ? (
            <div className="card">
              <h2>Job Information</h2>
              <p><strong>Job ID:</strong> 1234</p>
              <p><strong>Title:</strong> {jobInfo.job_title}</p>
              <p><strong>Details:</strong> {jobInfo.job_details}</p>
              <p><strong>Requirements:</strong> {jobInfo.requirements}</p>
              <p><strong>Experience:</strong> {jobInfo.experience}</p>
              <p><strong>Skills:</strong> {jobInfo.skills}</p>
            </div>
          ) : (
             !error && <p>Loading job details...</p>
          )}
        </div>

        <div className="application-column">
          <div className="card">
            <h2>Apply Now</h2>
            <form onSubmit={handleSubmit} className="form">
              <input
                type="text"
                placeholder="Your Name"
                value={name}
                required
                onChange={(e) => setName(e.target.value)}
              />
              <input
                type="email"
                placeholder="Your Email"
                value={email}
                required
                onChange={(e) => setEmail(e.target.value)}
              />
              <p>Upload Your Resume</p>
              <input
                type="file"
                accept=".pdf"
                required
                onChange={(e) => setResume(e.target.files[0])}
              />
              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Submit Application"}
              </button>
            </form>
            {error && <p className="error">{error}</p>}
          </div>

          {loading && <div className="card"><p>Analyzing your resume, please wait...</p></div>}

          {result && (
            <div className="result-card">
              <h2>Application Result</h2>
              <p><strong>Decision:</strong> {result.decision}</p>
              <p><strong>Compatibility Score:</strong> {result.compatibility_score}</p>
              <p><strong>Justification:</strong> {result.justification}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;