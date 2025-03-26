// Initialize AOS
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Initialize Particles.js
particlesJS('particles-js', {
    particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: '#6366f1' },
        shape: { type: 'circle' },
        opacity: { value: 0.5, random: false },
        size: { value: 3, random: true },
        line_linked: {
            enable: true,
            distance: 150,
            color: '#6366f1',
            opacity: 0.4,
            width: 1
        },
        move: {
            enable: true,
            speed: 2,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false
        }
    },
    interactivity: {
        detect_on: 'canvas',
        events: {
            onhover: { enable: true, mode: 'repulse' },
            onclick: { enable: true, mode: 'push' },
            resize: true
        }
    },
    retina_detect: true
});

// Preloader
window.addEventListener('load', () => {
    const preloader = document.querySelector('.preloader');
    preloader.style.opacity = '0';
    setTimeout(() => {
        preloader.style.display = 'none';
    }, 500);
});

// Global variables
let processes = [];
let ganttChart = null;

// DOM Elements
const processTable = document.getElementById('processTable').getElementsByTagName('tbody')[0];
const algorithmSelect = document.getElementById('algorithm');
const timeQuantumContainer = document.getElementById('timeQuantumContainer');
const timeQuantumInput = document.getElementById('timeQuantum');
const runBtn = document.getElementById('runBtn');
const addProcessBtn = document.getElementById('addProcessBtn');
const randomBtn = document.getElementById('randomBtn');
const clearBtn = document.getElementById('clearBtn');
const themeToggle = document.getElementById('themeToggle');
const loadingOverlay = document.querySelector('.loading-overlay');
const downloadBtn = document.getElementById('downloadBtn');

// Theme Management
const setTheme = (isDark) => {
    document.body.classList.toggle('dark-theme', isDark);
    localStorage.setItem('darkTheme', isDark);
    if (ganttChart) {
        ganttChart.destroy();
        updateGanttChart(lastTimelineData);
    }
};

// Initialize theme
themeToggle.checked = localStorage.getItem('darkTheme') === 'true';
setTheme(themeToggle.checked);

// Theme toggle event listener
themeToggle.addEventListener('change', (e) => setTheme(e.target.checked));

// Show/hide time quantum input based on algorithm selection
algorithmSelect.addEventListener('change', () => {
    const container = document.getElementById('timeQuantumContainer');
    if (algorithmSelect.value === 'RR') {
        container.style.display = 'block';
        container.style.animation = 'fadeIn 0.3s ease-in-out';
    } else {
        container.style.animation = 'fadeOut 0.3s ease-in-out';
        setTimeout(() => {
            container.style.display = 'none';
        }, 300);
    }
});

// Process Management
const addProcess = () => {
    const pid = `P${processes.length + 1}`;
    const process = {
        pid,
        arrivalTime: Math.floor(Math.random() * 10),
        burstTime: Math.floor(Math.random() * 10) + 1,
        priority: Math.floor(Math.random() * 5) + 1
    };
    processes.push(process);
    updateProcessTable();
    
    // Animate new process row
    const newRow = processTable.lastElementChild;
    newRow.style.opacity = '0';
    newRow.style.transform = 'translateX(-20px)';
    requestAnimationFrame(() => {
        newRow.style.transition = 'all 0.3s ease-in-out';
        newRow.style.opacity = '1';
        newRow.style.transform = 'translateX(0)';
    });
};

const removeProcess = (pid) => {
    const row = document.querySelector(`tr[data-pid="${pid}"]`);
    row.style.transition = 'all 0.3s ease-in-out';
    row.style.opacity = '0';
    row.style.transform = 'translateX(20px)';
    
    setTimeout(() => {
        processes = processes.filter(p => p.pid !== pid);
        updateProcessTable();
    }, 300);
};

const generateRandomProcesses = () => {
    processes = [];
    const count = Math.floor(Math.random() * 5) + 3; // 3-7 processes
    for (let i = 0; i < count; i++) {
        const process = {
            pid: `P${i + 1}`,
            arrivalTime: Math.floor(Math.random() * 10),
            burstTime: Math.floor(Math.random() * 10) + 1,
            priority: Math.floor(Math.random() * 5) + 1
        };
        processes.push(process);
    }
    updateProcessTable();
    
    // Animate all process rows
    const rows = processTable.getElementsByTagName('tr');
    Array.from(rows).forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease-in-out';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 100);
    });
};

const clearProcesses = () => {
    const rows = processTable.getElementsByTagName('tr');
    Array.from(rows).forEach((row, index) => {
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease-in-out';
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
        }, index * 100);
    });
    
    setTimeout(() => {
        processes = [];
        updateProcessTable();
        if (ganttChart) {
            ganttChart.destroy();
            ganttChart = null;
        }
        document.getElementById('avgWaitingTime').textContent = '-';
        document.getElementById('avgTurnaroundTime').textContent = '-';
    }, rows.length * 100 + 300);
};

// UI Updates
const updateProcessTable = () => {
    processTable.innerHTML = '';
    processes.forEach((process, index) => {
        const row = processTable.insertRow();
        row.setAttribute('data-pid', process.pid);
        row.innerHTML = `
            <td>
                <span class="badge bg-primary">${process.pid}</span>
            </td>
            <td>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-clock"></i></span>
                    <input type="number" class="form-control" value="${process.arrivalTime}" 
                        onchange="updateProcess('${process.pid}', 'arrivalTime', this.value)" min="0">
                </div>
            </td>
            <td>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-hourglass"></i></span>
                    <input type="number" class="form-control" value="${process.burstTime}" 
                        onchange="updateProcess('${process.pid}', 'burstTime', this.value)" min="1">
                </div>
            </td>
            <td>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-layer-group"></i></span>
                    <input type="number" class="form-control" value="${process.priority}" 
                        onchange="updateProcess('${process.pid}', 'priority', this.value)" min="1">
                </div>
            </td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeProcess('${process.pid}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        // Add hover effect
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'scale(1.01)';
            row.style.transition = 'transform 0.2s ease-in-out';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'scale(1)';
        });
    });
};

const updateProcess = (pid, field, value) => {
    const process = processes.find(p => p.pid === pid);
    if (process) {
        process[field] = parseInt(value) || 0;
    }
};

let lastTimelineData = [];

// Generate colors for Gantt chart
const generateColors = (count) => {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const hue = (i * 360) / count;
        colors.push(`hsla(${hue}, 70%, 60%, 0.8)`);
    }
    return colors;
};

// Gantt Chart
const updateGanttChart = (timeline) => {
    lastTimelineData = timeline;
    const ctx = document.getElementById('ganttChart').getContext('2d');
    
    if (ganttChart) {
        ganttChart.destroy();
    }

    const uniquePids = [...new Set(timeline.map(t => t.pid))];
    const colors = generateColors(uniquePids.length);
    const colorMap = Object.fromEntries(uniquePids.map((pid, i) => [pid, colors[i]]));

    const datasets = uniquePids.map(pid => ({
        label: pid,
        data: timeline
            .filter(t => t.pid === pid)
            .map(t => ([
                { x: t.time, y: uniquePids.indexOf(pid) },
                { x: t.time + 1, y: uniquePids.indexOf(pid) }
            ])).flat(),
        backgroundColor: colorMap[pid],
        borderColor: colorMap[pid],
        borderWidth: 2,
        segment: {
            borderColor: ctx => colorMap[pid],
            backgroundColor: ctx => colorMap[pid]
        },
        stepped: 'before',
        tension: 0
    }));

    ganttChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time Units',
                        color: document.body.classList.contains('dark-theme') ? '#f9fafb' : '#111827'
                    },
                    min: 0,
                    ticks: {
                        stepSize: 1,
                        color: document.body.classList.contains('dark-theme') ? '#f9fafb' : '#111827'
                    },
                    grid: {
                        color: document.body.classList.contains('dark-theme') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Processes',
                        color: document.body.classList.contains('dark-theme') ? '#f9fafb' : '#111827'
                    },
                    ticks: {
                        callback: (value) => uniquePids[value],
                        color: document.body.classList.contains('dark-theme') ? '#f9fafb' : '#111827'
                    },
                    grid: {
                        color: document.body.classList.contains('dark-theme') ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: document.body.classList.contains('dark-theme') ? '#f9fafb' : '#111827',
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const pid = context.dataset.label;
                            return `${pid} at time ${context.parsed.x}`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'nearest'
            }
        }
    });
};

// Simulation
const runSimulation = async () => {
    if (processes.length === 0) {
        alert('Please add at least one process.');
        return;
    }

    // Show loading overlay with animation
    loadingOverlay.style.display = 'flex';
    loadingOverlay.style.opacity = '0';
    requestAnimationFrame(() => {
        loadingOverlay.style.opacity = '1';
    });

    runBtn.disabled = true;

    try {
        const response = await fetch('/api/schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                algorithm: algorithmSelect.value,
                timeQuantum: parseInt(timeQuantumInput.value),
                processes: processes
            })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Update Gantt Chart with animation
        updateGanttChart(data.timeline);

        // Update Metrics with animation
        const avgWaitingTime = document.getElementById('avgWaitingTime');
        const avgTurnaroundTime = document.getElementById('avgTurnaroundTime');
        
        avgWaitingTime.style.transform = 'translateY(20px)';
        avgTurnaroundTime.style.transform = 'translateY(20px)';
        avgWaitingTime.style.opacity = '0';
        avgTurnaroundTime.style.opacity = '0';
        
        requestAnimationFrame(() => {
            avgWaitingTime.style.transition = 'all 0.5s ease-out';
            avgTurnaroundTime.style.transition = 'all 0.5s ease-out';
            avgWaitingTime.style.transform = 'translateY(0)';
            avgTurnaroundTime.style.transform = 'translateY(0)';
            avgWaitingTime.style.opacity = '1';
            avgTurnaroundTime.style.opacity = '1';
            
            avgWaitingTime.textContent = data.metrics.avgWaitingTime.toFixed(2);
            avgTurnaroundTime.textContent = data.metrics.avgTurnaroundTime.toFixed(2);
        });

        // Update process table with results
        processes = data.processes;
        updateProcessTable();

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        // Hide loading overlay with animation
        loadingOverlay.style.opacity = '0';
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
            runBtn.disabled = false;
        }, 300);
    }
};

// Download functionality
document.getElementById('downloadBtn').addEventListener('click', () => {
    // Create PDF content
    const content = {
        title: 'CPU Scheduling Simulation Report',
        algorithm: document.getElementById('algorithm').value,
        timeQuantum: document.getElementById('timeQuantum').value,
        processes: processes.map(p => ({
            pid: p.pid,
            arrivalTime: p.arrivalTime,
            burstTime: p.burstTime,
            priority: p.priority,
            waitingTime: p.waitingTime,
            turnaroundTime: p.turnaroundTime
        })),
        metrics: {
            avgWaitingTime: document.getElementById('avgWaitingTime').textContent,
            avgTurnaroundTime: document.getElementById('avgTurnaroundTime').textContent
        }
    };

    // Create new jsPDF instance
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Add title with better contrast
    doc.setFontSize(20);
    doc.setTextColor(51, 65, 85); // Darker blue for better contrast
    doc.text('CPU Scheduling Simulation Report', 20, 20);
    
    // Add algorithm info with better contrast
    doc.setFontSize(14);
    doc.setTextColor(31, 41, 55); // Dark gray for better readability
    doc.text(`Algorithm: ${content.algorithm}`, 20, 35);
    if (content.algorithm === 'RR') {
        doc.text(`Time Quantum: ${content.timeQuantum}`, 20, 45);
    }
    
    // Add process table
    doc.setFontSize(12);
    doc.setTextColor(31, 41, 55); // Consistent dark gray
    doc.text('Process Details:', 20, 60);
    
    // Only create table if there are processes
    if (processes.length > 0) {
        const headers = ['PID', 'Arrival', 'Burst', 'Priority', 'Waiting', 'Turnaround'];
        const data = content.processes.map(p => [
            p.pid,
            p.arrivalTime.toString(),
            p.burstTime.toString(),
            p.priority.toString(),
            (p.waitingTime || '-').toString(),
            (p.turnaroundTime || '-').toString()
        ]);
        
        doc.autoTable({
            head: [headers],
            body: data,
            startY: 65,
            theme: 'grid',
            styles: { 
                fontSize: 10,
                textColor: [31, 41, 55] // Dark gray text
            },
            headStyles: { 
                fillColor: [51, 65, 85], // Darker blue background
                textColor: [248, 250, 252], // Light gray text for contrast
                fontStyle: 'bold'
            },
            bodyStyles: {
                textColor: [31, 41, 55] // Dark gray text
            },
            alternateRowStyles: {
                fillColor: [248, 250, 252] // Light gray background for alternate rows
            }
        });
        
        // Add metrics with better contrast
        const finalY = doc.previousAutoTable.finalY + 15;
        doc.setTextColor(31, 41, 55); // Dark gray
        doc.text('Performance Metrics:', 20, finalY);
        doc.text(`Average Waiting Time: ${content.metrics.avgWaitingTime}`, 20, finalY + 10);
        doc.text(`Average Turnaround Time: ${content.metrics.avgTurnaroundTime}`, 20, finalY + 20);
        
        // Add Gantt chart if it exists
        if (ganttChart) {
            try {
                doc.addPage();
                const canvas = document.getElementById('ganttChart');
                
                // Temporarily increase canvas size for better quality
                const originalWidth = canvas.width;
                const originalHeight = canvas.height;
                canvas.width = canvas.width * 2;
                canvas.height = canvas.height * 2;
                const ctx = canvas.getContext('2d');
                ctx.scale(2, 2);
                ganttChart.draw();
                
                // Get the high resolution image
                const imgData = canvas.toDataURL('image/png', 1.0);
                
                // Restore original canvas size
                canvas.width = originalWidth;
                canvas.height = originalHeight;
                ctx.scale(1, 1);
                ganttChart.draw();
                
                // Add to PDF with better positioning and size
                doc.setFontSize(14);
                doc.setTextColor(31, 41, 55);
                doc.text('Gantt Chart:', 20, 30);
                doc.addImage(imgData, 'PNG', 20, 40, 170, 100);
            } catch (e) {
                console.error('Error adding Gantt chart to PDF:', e);
            }
        }
    } else {
        doc.text('No processes added yet.', 20, 70);
    }
    
    // Add footer with better contrast
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(10);
        doc.setTextColor(71, 85, 105); // Slate gray for footer
        doc.text('Developed by: Harsh Nag', 20, doc.internal.pageSize.height - 10);
        doc.text(`Page ${i} of ${pageCount}`, doc.internal.pageSize.width - 40, doc.internal.pageSize.height - 10);
    }
    
    // Save the PDF
    try {
        doc.save('cpu-scheduling-report.pdf');
    } catch (e) {
        console.error('Error saving PDF:', e);
        alert('Error generating PDF. Please try again.');
    }
});

// Event Listeners
addProcessBtn.addEventListener('click', addProcess);
randomBtn.addEventListener('click', generateRandomProcesses);
clearBtn.addEventListener('click', clearProcesses);
runBtn.addEventListener('click', runSimulation);

// Initialize
algorithmSelect.dispatchEvent(new Event('change'));
