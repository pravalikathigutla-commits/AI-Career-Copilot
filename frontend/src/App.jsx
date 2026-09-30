import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setAnalysis(null);
    setError("");
  };

  const analyzeResume = async () => {
  if (!file) {
    setError("Please select a PDF resume first.");
    return;
  }

  setLoading(true);
  setError("");
  setAnalysis(null);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/upload-resume",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Server error ${response.status}: ${errorText}`
      );
    }

    const data = await response.json();

    if (!data.ai_analysis) {
      throw new Error("AI analysis was not returned by the server.");
    }

    setAnalysis(data.ai_analysis);

  } catch (err) {
    console.error("Analysis error:", err);
    setError(
      err.message || "Something went wrong while analyzing the resume."
    );
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="app">

      <header>
        <h1>🚀 AI Career Copilot</h1>

        <p>
          Upload your resume and get AI-powered career guidance
        </p>
      </header>

      <main>

        {/* Upload Section */}

        <section className="upload-card">

          <h2>📄 Resume Analyzer</h2>

          <p>
            Upload your resume PDF and let AI analyze your
            skills, projects and career opportunities.
          </p>

          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
          />

          {file && (
            <p className="selected-file">
              Selected: {file.name}
            </p>
          )}

          <button
            onClick={analyzeResume}
            disabled={loading}
          >
            {loading ? "🤖 AI is analyzing..." : "Analyze Resume"}
          </button>

          {error && (
            <p className="error">
              {error}
            </p>
          )}

        </section>


        {/* AI Results */}

        {analysis && (

          <section className="results">

            <h2>🤖 AI Resume Analysis</h2>


            {/* Score */}

            <div className="score-card">

              <h3>Resume Score</h3>

              <div className="score">
                {analysis.score}
                <span>/100</span>
              </div>

              <p>
                Your resume's current AI evaluation
              </p>

            </div>


            {/* Skills */}

            <div className="grid">

              <div className="info-card">

                <h3>💪 Strong Skills</h3>

                <ul>
                  {analysis.strong_skills?.map(
                    (skill, index) => (
                      <li key={index}>
                        {skill}
                      </li>
                    )
                  )}
                </ul>

              </div>


              <div className="info-card">

                <h3>⚠️ Missing / Weak Skills</h3>

                <ul>
                  {analysis.missing_skills?.map(
                    (skill, index) => (
                      <li key={index}>
                        {skill}
                      </li>
                    )
                  )}
                </ul>

              </div>

            </div>


            {/* Recommended Skills */}

            <div className="info-card full">

              <h3>📚 Recommended Skills to Learn</h3>

              <ul>
                {analysis.recommended_skills?.map(
                  (skill, index) => (
                    <li key={index}>
                      {skill}
                    </li>
                  )
                )}
              </ul>

            </div>


            {/* Job Roles */}

            <div className="info-card full">

              <h3>💼 Suitable Job Roles</h3>

              <div className="tags">

                {analysis.job_roles?.map(
                  (role, index) => (
                    <span key={index}>
                      {role}
                    </span>
                  )
                )}

              </div>

            </div>


            {/* Projects */}

            <div className="info-card full">

              <h3>🚀 Recommended Projects</h3>

              <ul>
                {analysis.recommended_projects?.map(
                  (project, index) => (
                    <li key={index}>
                      {project}
                    </li>
                  )
                )}
              </ul>

            </div>


            {/* Roadmap */}

            <div className="roadmap">

              <h3>🗺️ 3-Month Learning Roadmap</h3>

              <div className="roadmap-grid">

                <div>
                  <h4>Month 1</h4>

                  <ul>
                    {analysis.roadmap?.month_1?.map(
                      (item, index) => (
                        <li key={index}>
                          {item}
                        </li>
                      )
                    )}
                  </ul>
                </div>


                <div>
                  <h4>Month 2</h4>

                  <ul>
                    {analysis.roadmap?.month_2?.map(
                      (item, index) => (
                        <li key={index}>
                          {item}
                        </li>
                      )
                    )}
                  </ul>
                </div>


                <div>
                  <h4>Month 3</h4>

                  <ul>
                    {analysis.roadmap?.month_3?.map(
                      (item, index) => (
                        <li key={index}>
                          {item}
                        </li>
                      )
                    )}
                  </ul>
                </div>

              </div>

            </div>


            {/* Improvements */}

            <div className="info-card full">

              <h3>✨ Resume Improvement Suggestions</h3>

              <ul>
                {analysis.improvements?.map(
                  (item, index) => (
                    <li key={index}>
                      {item}
                    </li>
                  )
                )}
              </ul>

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;