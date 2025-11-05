// Custom JavaScript for Student Attendance Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Attendance form enhancements
    var attendanceSelects = document.querySelectorAll('.attendance-status-select');
    attendanceSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            updateStatusIndicator(this);
            updateFormState();
        });
    });

    // Mark all present functionality
    window.markAllPresent = function() {
        attendanceSelects.forEach(function(select) {
            select.value = 'Present';
            updateStatusIndicator(select);
        });
        updateFormState();
    };

    // Mark all absent functionality
    window.markAllAbsent = function() {
        attendanceSelects.forEach(function(select) {
            select.value = 'Absent';
            updateStatusIndicator(select);
        });
        updateFormState();
    };

    // Update status indicator
    function updateStatusIndicator(select) {
        var studentId = select.id.replace('status_', '');
        var indicator = document.getElementById('indicator_' + studentId);
        var status = select.value;
        
        if (status) {
            var badgeClass = 'bg-secondary';
            if (status === 'Present') badgeClass = 'bg-success';
            else if (status === 'Late') badgeClass = 'bg-warning';
            else if (status === 'Excused') badgeClass = 'bg-info';
            else if (status === 'Absent') badgeClass = 'bg-danger';
            
            indicator.innerHTML = '<span class="badge ' + badgeClass + '">' + status + '</span>';
        } else {
            indicator.innerHTML = '<span class="text-muted small">Not marked</span>';
        }
    }

    // Update form state based on selections
    function updateFormState() {
        var totalStudents = attendanceSelects.length;
        var markedStudents = 0;
        
        attendanceSelects.forEach(function(select) {
            if (select.value) {
                markedStudents++;
            }
        });
        
        // Update save button state
        var saveButton = document.querySelector('button[type="submit"]');
        if (saveButton) {
            if (markedStudents === totalStudents) {
                saveButton.classList.remove('btn-outline-primary');
                saveButton.classList.add('btn-success');
                saveButton.innerHTML = '<i class="bi bi-check-circle me-1"></i>All Marked - Save';
            } else {
                saveButton.classList.remove('btn-success');
                saveButton.classList.add('btn-primary');
                saveButton.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save Attendance';
            }
        }
        
        // Show progress
        var progressInfo = document.querySelector('.progress-info');
        if (progressInfo) {
            progressInfo.textContent = markedStudents + ' of ' + totalStudents + ' students marked';
        }
    }

    // Initialize form state
    updateFormState();

    // Print functionality
    window.printReport = function() {
        window.print();
    };

    // Export functionality (placeholder for future CSV export)
    window.exportReport = function() {
        // This will be implemented in the finals version
        alert('CSV export will be available in the finals version!');
    };

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save attendance
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            var saveButton = document.querySelector('button[type="submit"]');
            if (saveButton) {
                saveButton.click();
            }
        }
        
        // Ctrl+P to print
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
    });

    // Confirmation for form submissions
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && submitButton.textContent.includes('Save')) {
                if (!confirm('Are you sure you want to save the attendance data?')) {
                    e.preventDefault();
                }
            }
        });
    });

    // Auto-save functionality (localStorage backup)
    var attendanceForm = document.querySelector('form[method="POST"]');
    if (attendanceForm) {
        var formData = {};
        
        // Load saved data
        var savedData = localStorage.getItem('attendance_backup');
        if (savedData) {
            try {
                formData = JSON.parse(savedData);
                Object.keys(formData).forEach(function(studentId) {
                    var select = document.getElementById('status_' + studentId);
                    if (select) {
                        select.value = formData[studentId];
                        updateStatusIndicator(select);
                    }
                });
            } catch (e) {
                console.log('Could not load saved attendance data');
            }
        }
        
        // Save data on change
        attendanceSelects.forEach(function(select) {
            select.addEventListener('change', function() {
                var studentId = this.id.replace('status_', '');
                formData[studentId] = this.value;
                localStorage.setItem('attendance_backup', JSON.stringify(formData));
            });
        });
        
        // Clear backup on successful save
        attendanceForm.addEventListener('submit', function() {
            localStorage.removeItem('attendance_backup');
        });
    }
});

// Utility functions
function showLoading(button) {
    button.classList.add('loading');
    button.disabled = true;
}

function hideLoading(button) {
    button.classList.remove('loading');
    button.disabled = false;
}

function showToast(message, type = 'info') {
    // Simple toast notification
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + type + ' border-0';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = 
        '<div class="d-flex">' +
            '<div class="toast-body">' + message + '</div>' +
            '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
        '</div>';
    
    document.body.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
