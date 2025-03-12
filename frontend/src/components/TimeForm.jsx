import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

function TimeForm({ onSubmit }) {
  const [time, setTime] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (time) {
      onSubmit(time);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border rounded shadow-sm bg-light"
    >
      <div className="mb-3">
        <label htmlFor="timeInput" className="form-label fw-bold">
          Select Time to Send Survey Invitations:
        </label>
        <input
          type="time"
          className="form-control"
          id="timeInput"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          required
        />
        <div className="form-text">
          Choose a time when doctors are most likely to respond to your survey.
        </div>
      </div>
      <button type="submit" className="btn btn-primary w-100">
        Find Best Doctors
      </button>
    </form>
  );
}

export default TimeForm;
