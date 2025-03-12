import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import TimeForm from "./components/TimeForm";
import ResultsTable from "./components/ResultsTable";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePrediction = async (time) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:5000/predict?time=${time}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch predictions");
      }

      const data = await response.json();
      console.log("API Response:", data); // Debug log

      if (data.success && data.doctors) {
        setResults(data.doctors);
      } else {
        throw new Error(data.error || "Invalid response from server");
      }
    } catch (err) {
      setError(err.message);
      console.error("Error fetching predictions:", err);
    } finally {
      setLoading(false);
    }
  };

  const exportToCsv = () => {
    if (!results.length) return;

    const headers = Object.keys(results[0]).join(",");
    const csvRows = results.map((row) => Object.values(row).join(","));
    const csvContent = [headers, ...csvRows].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `doctor_predictions_${new Date().toISOString().slice(0, 10)}.csv`
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Doctor Survey Targeting System</h1>
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow">
            <div className="card-body">
              <TimeForm onSubmit={handlePrediction} />

              {loading && (
                <div className="text-center my-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              )}

              {error && (
                <div className="alert alert-danger mt-3" role="alert">
                  {error}
                </div>
              )}

              {results.length > 0 && (
                <div className="mt-4">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4>Recommended Doctors</h4>
                    <button className="btn btn-success" onClick={exportToCsv}>
                      Export to CSV
                    </button>
                  </div>
                  <ResultsTable doctors={results} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
