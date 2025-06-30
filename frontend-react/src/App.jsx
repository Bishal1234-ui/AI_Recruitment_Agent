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

  const FileIcon = () => (
    <svg className="file-icon" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zM3 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V6zM7 11a1 1 0 011-1h4a1 1 0 110 2H8a1 1 0 01-1-1z" clipRule="evenodd" />
    </svg>
  );

  return (
    <div className="app-container">
      <header className="navbar">
        <h1 className="navbar-title">🚀 Career Opportunities Portal</h1>
      </header>

      <main className="main-content">
        <div className="job-details-column">
          {jobInfo ? (
            <div className="card">
              <h2>💼 Position Details</h2>
              <div className="job-info-grid">
                <div className="job-info-item">
                  <p><strong>Job ID:</strong> #JOB-2024-001</p>
                </div>
                <div className="job-info-item">
                  <p><strong>Title:</strong> {jobInfo.job_title}</p>
                </div>
                <div className="job-info-item">
                  <p><strong>Description:</strong> {jobInfo.job_details}</p>
                </div>
                <div className="job-info-item">
                  <p><strong>Requirements:</strong> {jobInfo.requirements}</p>
                </div>
                <div className="job-info-item">
                  <p><strong>Experience Level:</strong> {jobInfo.experience}</p>
                </div>
                <div className="job-info-item skills-section">
                  <p><strong>Key Skills:</strong></p>
                  <div className="skills-list">
                    {jobInfo.skills.split(',').map((skill, index) => (
                      <span key={index} className="skill-tag">
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
             !error && (
               <div className="card loading-card">
                 <h2>💼 Position Details</h2>
                 <p>Loading exciting opportunities for you...</p>
               </div>
             )
          )}
        </div>

        <div className="application-column">
          <div className="card">
            <h2>📝 Submit Your Application</h2>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  required
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  placeholder="your.email@domain.com"
                  value={email}
                  required
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Upload Resume (PDF)</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    accept=".pdf"
                    required
                    onChange={(e) => setResume(e.target.files[0])}
                  />
                  <div className={`file-input-display ${resume ? 'file-selected' : ''}`}>
                    <FileIcon />
                    <span className="file-text">
                      {resume ? resume.name : 'Choose your resume file (PDF only)'}
                    </span>
                  </div>
                </div>
              </div>
              
              <button type="submit" disabled={loading}>
                {loading && <span className="loading-spinner"></span>}
                {loading ? "Analyzing Your Profile..." : "🚀 Submit Application"}
              </button>
            </form>
            {error && <div className="error">⚠️ {error}</div>}
          </div>

          {loading && (
            <div className="card loading-card">
              <h2>🔍 AI Analysis in Progress</h2>
              <p>Our intelligent system is carefully reviewing your profile and matching it against our requirements...</p>
            </div>
          )}

          {result && (
            <div className={`result-card ${result.decision?.toLowerCase() === 'rejected' ? 'rejected' : ''}`}>
              <h2>📊 Application Assessment</h2>
              <p>
                <strong>Decision:</strong> 
                <span className={`decision-badge ${result.decision?.toLowerCase() === 'accepted' ? 'accepted' : 'rejected'}`}>
                  {result.decision}
                </span>
              </p>
              <p>
                <strong>Compatibility Score:</strong>
                <span className="compatibility-score">{result.compatibility_score}</span>
              </p>
              <p><strong>Detailed Analysis:</strong> {result.justification}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;