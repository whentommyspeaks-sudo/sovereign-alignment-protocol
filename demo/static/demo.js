// SAP Live Demo - Interactive JavaScript

let demoData = [];
let violationChart = null;

// Initialize demo on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTestCases();
    updateDashboard();
});

// Load test cases from server
async function loadTestCases() {
    try {
        const response = await fetch('/api/test-cases');
        const data = await response.json();
        demoData = data.cases;
        renderTestCases();
    } catch (error) {
        console.error('Error loading test cases:', error);
    }
}

// Render test case cards
function renderTestCases() {
    const container = document.getElementById('casesGrid');
    container.innerHTML = '';

    demoData.forEach(testCase => {
        const card = document.createElement('div');
        card.className = 'test-case-card';
        card.onclick = () => validateCase(testCase.id);

        card.innerHTML = `
            <h4>${testCase.title}</h4>
            <p><strong>Input:</strong> ${testCase.input.substring(0, 50)}...</p>
            <p><strong>Response:</strong> ${testCase.ai_response.substring(0, 50)}...</p>
            <span class="category">${testCase.category}</span>
        `;

        container.appendChild(card);
    });
}

// Validate a single case
async function validateCase(caseId) {
    const testCase = demoData.find(c => c.id === caseId);
    if (!testCase) return;

    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                response: testCase.ai_response,
                case_id: caseId
            })
        });

        const result = await response.json();
        displayResult(testCase, result);
        updateDashboard();
    } catch (error) {
        console.error('Error validating case:', error);
    }
}

// Display validation result
function displayResult(testCase, result) {
    const container = document.getElementById('resultsContainer');
    
    const resultCard = document.createElement('div');
    resultCard.className = `result-card ${result.approved ? 'approved' : 'blocked'}`;

    let violationsHTML = '';
    if (result.violations.length > 0) {
        violationsHTML = '<div class="violations-list"><strong>Violations:</strong>';
        result.violations.forEach(v => {
            violationsHTML += `
                <div class="violation-item ${v.severity}">
                    <strong>${v.rule_id}</strong><br>
                    ${v.description}
                </div>
            `;
        });
        violationsHTML += '</div>';
    }

    resultCard.innerHTML = `
        <h4>${testCase.title}</h4>
        <div class="result-status ${result.approved ? 'approved' : 'blocked'}">
            ${result.approved ? '✅ APPROVED' : '❌ BLOCKED'}
        </div>
        <p><strong>Message:</strong> ${result.message}</p>
        <p><strong>Status Code:</strong> ${result.status_code}</p>
        ${violationsHTML}
        <p style="font-size: 0.85em; color: #999; margin-top: 10px;">
            Confidence: ${(result.metadata.action_hash)} | ${new Date(result.metadata.timestamp).toLocaleTimeString()}
        </p>
    `;

    container.insertBefore(resultCard, container.firstChild);

    // Keep only last 10 results
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

// Run all test cases
async function runAllTests() {
    console.log('Running all 8 test cases...');
    
    try {
        const response = await fetch('/api/run-all-tests');
        const data = await response.json();
        
        // Display all results
        const container = document.getElementById('resultsContainer');
        container.innerHTML = '';
        
        data.results.forEach(result => {
            const testCase = demoData.find(c => c.id === result.case_id);
            displayResult(testCase, {
                approved: result.approved,
                message: result.message,
                status_code: result.approved ? 200 : 403,
                violations: [],
                metadata: {
                    action_hash: 'demo',
                    timestamp: new Date().toISOString()
                }
            });
        });
        
        updateDashboard();
        showNotification('All 8 test cases completed!');
    } catch (error) {
        console.error('Error running all tests:', error);
        showNotification('Error running tests', 'error');
    }
}

// Update dashboard metrics and chart
async function updateDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = response.json();
        
        data.then(dashboard => {
            // Update metrics
            const globalMetrics = dashboard.global_metrics;
            document.getElementById('totalValidations').textContent = globalMetrics.total_validations || 0;
            document.getElementById('approvalRate').textContent = globalMetrics.approval_rate.toFixed(1) + '%';
            document.getElementById('blockedCount').textContent = globalMetrics.total_validations - globalMetrics.total_violations || 0;
            document.getElementById('totalViolations').textContent = globalMetrics.total_violations || 0;
            
            // Update health indicator
            const health = dashboard.health;
            const indicator = document.getElementById('healthIndicator');
            indicator.className = `health-indicator ${health.health_status.toLowerCase()}`;
            document.getElementById('healthText').textContent = 
                `Status: ${health.health_status} | Approval Rate: ${health.approval_rate.toFixed(1)}%`;
            
            // Update chart
            updateViolationChart(dashboard.violation_breakdown);
        });
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Update violation breakdown chart
function updateViolationChart(violationData) {
    const ctx = document.getElementById('violationChart');
    if (!ctx) return;
    
    const labels = Object.keys(violationData);
    const data = Object.values(violationData);
    
    if (violationChart) {
        violationChart.destroy();
    }
    
    violationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => l.replace('RULE_', '')),
            datasets: [{
                label: 'Violations Detected',
                data: data,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(139, 92, 246, 0.7)',
                    'rgba(16, 185, 129, 0.7)'
                ],
                borderColor: [
                    'rgb(239, 68, 68)',
                    'rgb(245, 158, 11)',
                    'rgb(59, 130, 246)',
                    'rgb(139, 92, 246)',
                    'rgb(16, 185, 129)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Reset demo
function resetDemo() {
    document.getElementById('resultsContainer').innerHTML = '';
    document.getElementById('totalValidations').textContent = '0';
    document.getElementById('approvalRate').textContent = '0%';
    document.getElementById('blockedCount').textContent = '0';
    document.getElementById('totalViolations').textContent = '0';
    showNotification('Demo reset successfully');
}

// Show notification
function showNotification(message, type = 'success') {
    // Simple notification (can be enhanced with toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

// Auto-refresh dashboard every 5 seconds
setInterval(updateDashboard, 5000);
