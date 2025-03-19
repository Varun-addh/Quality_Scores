// Global weights object to track weights of all metrics
const weights = {};
let totalWeight = 0;

function toggleMetricScores(metric) {
    const checkBox = document.getElementById(`checkbox-${metric}`);
    const inputBox = document.getElementById(`input-${metric}`);
    const allCells = document.querySelectorAll(`[id^="score-${metric}-"]`);
    const headerCell = document.getElementById(`header-${metric}`);
    const table = document.getElementById('scores-table');
    const tableHeader = document.getElementById('table-header');

    // Toggle visibility for metric-specific elements
    const isVisible = checkBox.checked;
    const displayStyle = isVisible ? "table-cell" : "none";

    headerCell.style.display = displayStyle;
    inputBox.style.display = isVisible ? "inline-block" : "none";
    allCells.forEach(cell => {
        cell.style.display = displayStyle;
    });

    if (isVisible) {
        // Set the input box empty when checkbox is selected only if it doesn't have an existing weight
        if (!weights[metric]) {
            inputBox.value = "";
        } else {
            inputBox.value = weights[metric];
        }
        inputBox.addEventListener('input', () => handleInputChange(metric));
        if (Object.keys(weights).length > 0) {
            // Automatically set remaining weight if not already entered
            const remainingWeight = 100 - totalWeight;
            inputBox.placeholder = remainingWeight > 0 ? remainingWeight : "";
        }
    } else {
        // Only remove the weight for the unchecked metric
        delete weights[metric];
        totalWeight = calculateTotalWeight();
    }

    // Check if any checkbox is selected and update table visibility
    const isAnyChecked = [...document.querySelectorAll('input[type="checkbox"]')].some(cb => cb.checked);
    table.style.display = isAnyChecked ? "table" : "none";
    tableHeader.style.display = isAnyChecked ? "table-row-group" : "none";
}

function handleInputChange(metric) {
    const inputBox = document.getElementById(`input-${metric}`);
    const updatedValue = parseFloat(inputBox.value) || 0;

    if (updatedValue < 0 || updatedValue > 100) {
        alert("Weight must be between 0 and 100.");
        inputBox.value = weights[metric] || "";
        return;
    }

    // Update weights and calculate remaining weight
    weights[metric] = updatedValue;
    totalWeight = calculateTotalWeight();

    const remainingWeight = 100 - totalWeight;

    // Update placeholder for unchecked metrics with remaining weight
    const uncheckedMetrics = [...document.querySelectorAll('input[type="checkbox"]')]
        .filter(cb => cb.checked && !weights[cb.id.split('-')[1]]);

    uncheckedMetrics.forEach(cb => {
        const metricId = cb.id.split('-')[1];
        const input = document.getElementById(`input-${metricId}`);
        input.placeholder = remainingWeight > 0 ? remainingWeight : "";
    });
}


function adjustWeightsAfterRemoval() {
    totalWeight = calculateTotalWeight();
}

function calculateTotalWeight() {
    return Object.values(weights).reduce((sum, weight) => sum + weight, 0);
}

function submitAllWeights() {
    const metricInputs = document.querySelectorAll('.metric-input');
    let valid = true;

    // Reset the weights object
    Object.keys(weights).forEach(metric => delete weights[metric]);

    // Update weights for all visible inputs
    metricInputs.forEach(input => {
        const metric = input.id.split('-')[1];
        if (document.getElementById(`checkbox-${metric}`).checked) {
            const weight = parseFloat(input.value);

            if (isNaN(weight) || weight < 0 || weight > 100) {
                valid = false;
                input.style.borderColor = "red";
            } else {
                weights[metric] = weight; 
                input.style.borderColor = "";
            }
        }
    });

    // Validate the total weight
    const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
    if (valid && totalWeight === 100) {
        recalculateOverallScore(); // Recalculate overall score if all weights are valid
    } else if (!valid) {
        alert("Please enter valid weights for all selected metrics (0-100).");
    } else if (totalWeight !== 100) {
        alert(`The total priority weight must equal 100%. Current total: ${totalWeight}%.`);
    }
}

function recalculateOverallScore() {
    const overallScoreSection = document.getElementById('overall-quality-score');
    const overallScoreValue = document.getElementById('overall-score-value');

    let totalWeightedScore = 0;

    // Iterate over table rows to calculate the total weighted score
    document.querySelectorAll('#table-body tr').forEach(row => {
        let rowScore = 0;

        Object.keys(weights).forEach(metric => {
            const cell = row.querySelector(`[id^="score-${metric}-"]`);
            const cellScore = parseFloat(cell?.innerText.replace('%', '') || 0);
            rowScore += cellScore * (weights[metric] / 100);
        });

        totalWeightedScore += rowScore;
    });

    // Calculate the overall score
    const rowCount = document.querySelectorAll('#table-body tr').length;
    const overallScore = rowCount > 0 ? (totalWeightedScore / rowCount).toFixed(2) : 0;

    // Update the overall score display
    overallScoreValue.innerText = `${overallScore}%`;
    overallScoreSection.style.display = Object.keys(weights).length > 0 ? "block" : "none";
}

function showChart(column) {
    // Hide all charts
    document.querySelectorAll("[id$='-charts']").forEach(chart => {
        chart.style.display = 'none';
    });

    // Show the selected chart
    const chartContainer = document.getElementById("chart-container");
    if (column) {
        const selectedChart = document.getElementById(`${column}-charts`);
        chartContainer.style.display = 'block';
        selectedChart.style.display = 'flex';
    } else {
        chartContainer.style.display = 'none';
    }
}


function toggleOverview() {
    // Show all overview sections
    const sections = ['dataset-statistics', 'detailed-scores', 'missing-values', 
                     'visualizations', 'overall-quality-score', 'scores-table-container'];
    sections.forEach(section => {
        const elem = document.getElementById(section);
        if (elem) elem.style.display = 'block';
    });
    
    // Show metric selection and scores table
    const metricSelection = document.querySelector('.metric-selection-container');
    if (metricSelection) metricSelection.style.display = 'block';
    
    // Hide alerts section
    document.getElementById('alerts-section').style.display = 'none';
}

function toggleAlerts() {
    const datasetStatistics = document.getElementById('dataset-statistics');
    const detailedScores = document.getElementById('detailed-scores');
    const missingValues = document.getElementById('missing-values');
    const visualizations = document.getElementById('visualizations');
    const alertsSection = document.getElementById('alerts-section');
    const overallQualityScore = document.getElementById('overall-quality-score');
    const charts = document.querySelectorAll('.charts-side-by-side');
    const metricSelectionContainer = document.querySelector('.metric-selection-container');
    const scoresTableContainer = document.getElementById('scores-table-container');

    if (datasetStatistics) datasetStatistics.style.display = 'none';
    if (detailedScores) detailedScores.style.display = 'none';
    if (missingValues) missingValues.style.display = 'none';
    if (visualizations) visualizations.style.display = 'none';
    if (overallQualityScore) overallQualityScore.style.display = 'none';
    charts.forEach(chart => chart.style.display = 'none');
    if (metricSelectionContainer) metricSelectionContainer.style.display = 'none';
    if (scoresTableContainer) scoresTableContainer.style.display = 'none';

    if (alertsSection) {
        alertsSection.style.display = 'block';
        const alertsContent = document.getElementById('alerts-content');
        if (window.alerts && window.alerts.length > 0) {
            let alertList = '<ul>';
            window.alerts.forEach(alert => {
                alertList += `<li>${alert}</li>`;
            });
            alertList += '</ul>';
            alertsContent.innerHTML = alertList;
        } else {
            alertsContent.innerHTML = '<p>No alerts found for this dataset.</p>';
        }
    }
}
