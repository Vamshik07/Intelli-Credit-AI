import React, { useState } from "react";

function UploadForm({ onSubmit }) {
  const [company, setCompany] = useState("");
  const [file, setFile] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!company || !file) {
      return;
    }

    onSubmit({ company, file });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Company Name"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
      />
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button type="submit">Analyze</button>
    </form>
  );
}

export default UploadForm;
