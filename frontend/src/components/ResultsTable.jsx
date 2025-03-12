import React from "react";

function ResultsTable({ doctors }) {
  if (!doctors || doctors.length === 0) {
    return null;
  }

  console.log("Doctors data for table:", doctors); // Debug log

  // Function to determine progress bar color based on likelihood score
  const getProgressBarColor = (score) => {
    if (score < 40) return "bg-danger"; // Red for low likelihood
    if (score < 70) return "bg-warning"; // Yellow for medium likelihood
    return "bg-success"; // Green for high likelihood
  };

  return (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="table-dark">
          <tr>
            <th>NPI</th>
            <th>Specialty</th>
            <th>Region</th>
            <th>Likelihood Score</th>
          </tr>
        </thead>
        <tbody>
          {doctors.map((doctor, index) => (
            <tr key={index}>
              <td>{doctor.npi || "N/A"}</td>
              <td>{doctor.specialty || "N/A"}</td>
              <td>{doctor.region || "N/A"}</td>
              <td>
                <div className="d-flex align-items-center">
                  <div
                    className="progress flex-grow-1"
                    style={{ height: "20px" }}
                  >
                    <div
                      className={`progress-bar ${getProgressBarColor(
                        doctor.likelihood_score
                      )}`}
                      role="progressbar"
                      style={{ width: `${doctor.likelihood_score}%` }}
                      aria-valuenow={doctor.likelihood_score}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    >
                      {doctor.likelihood_score}%
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ResultsTable;
