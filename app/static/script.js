let latestMatchResult = null;
function showResult(text) {
    document.getElementById("result").innerText = text;
}
async function uploadEHR() {
    const file = document.getElementById("ehrFile").files[0];
    if (!file) {
        alert("Please select a PDF file.");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch("/upload-ehr", {
        method: "POST",
        body: formData
    });
    const data = await response.json();
    let output = "";
    output += "EHR Uploaded Successfully\n\n";
    output += "Raw Text Preview:\n";
    output += data.raw_text_preview + "\n\n";
    output += "Extracted Information:\n";
    for (const key in data.extracted) {
        output += `${key}: ${data.extracted[key]}\n`;
    }
    showResult(output);
}
async function matchPatient() {

    const payload = {
        patient_name: document.getElementById("patient_name").value,
        age: parseInt(document.getElementById("age").value) || null,
        gender: document.getElementById("gender").value,
        disease: document.getElementById("disease").value,
        medication: document.getElementById("medication").value,
        medical_history: document.getElementById("medical_history").value,
        top_k: parseInt(document.getElementById("top_k").value) || 5
    };

    const response = await fetch("/match-patient", {
        method: "POST",
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    latestMatchResult = data;

    let output = "";
    output += "PATIENT DETAILS\n";
    output += "====================\n";
    output += `Name: ${data.patient.patient_name}\n`;
    output += `Age: ${data.patient.age}\n`;
    output += `Gender: ${data.patient.gender}\n`;
    output += `Disease: ${data.patient.disease}\n\n`;
    output += "MATCHED CLINICAL TRIALS\n";
    output += "====================\n\n";

    data.retrieved_trials.forEach((trial, index) => {

        output += `Trial ${index + 1}\n`;
        output += `Title: ${trial.title}\n`;
        output += `Disease: ${trial.disease}\n`;
        output += `Eligible: ${trial.eligible}\n`;
        output += `Match Score: ${trial.match_score}\n`;
        output += `Reason: ${trial.reason}\n`;
        output += `Recommendation: ${trial.recommendation}\n`;
        output += "---------------------------------\n\n";

    });

    if (data.best_match) {

        output += "BEST MATCH\n";
        output += "====================\n";
        output += `Title: ${data.best_match.title}\n`;
        output += `Disease: ${data.best_match.disease}\n`;
        output += `Match Score: ${data.best_match.match_score}\n`;
        output += `Recommendation: ${data.best_match.recommendation}\n`;
    }

    showResult(output);
}

async function createTrial() {

    const payload = {
        title: document.getElementById("title").value,
        disease: document.getElementById("trialDisease").value,
        description: document.getElementById("description").value,
        inclusion_criteria: document.getElementById("inclusion").value,
        exclusion_criteria: document.getElementById("exclusion").value,
        min_age: parseInt(document.getElementById("minAge").value) || null,
        max_age: parseInt(document.getElementById("maxAge").value) || null,
        status: document.getElementById("status").value
    };

    const response = await fetch("/trials", {
        method: "POST",
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    let output = "";

    output += "CLINICAL TRIAL CREATED SUCCESSFULLY\n\n";
    output += `Trial ID: ${data.id}\n`;
    output += `Title: ${data.title}\n`;
    output += `Disease: ${data.disease}\n`;
    output += `Status: ${data.status}\n`;

    showResult(output);
}

async function getTrials() {

    const response = await fetch("/trials");
    const data = await response.json();

    let output = "";

    output += "AVAILABLE CLINICAL TRIALS\n";
    output += "=========================\n\n";

    data.forEach(trial => {

        output += `ID: ${trial.id}\n`;
        output += `Title: ${trial.title}\n`;
        output += `Disease: ${trial.disease}\n`;
        output += `Status: ${trial.status}\n`;
        output += "---------------------------------\n\n";

    });

    showResult(output);
}

async function generateReport() {
    if (!latestMatchResult) {
        alert("Please run Match Patient first.");
        return;
    }
    const payload = {
        patient: latestMatchResult.patient,
        match_result: latestMatchResult
    };

    const response = await fetch("/generate-report", {
        method: "POST",
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    let output = "";

    output += "REPORT GENERATED SUCCESSFULLY\n\n";
    output += `Report Path:\n${data.report_path}\n\n`;
    output += "Downloading report...";

    showResult(output);
    window.open(
        `/download-report?path=${encodeURIComponent(data.report_path)}`,
        "_blank"
    );
}