document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const regexInput = document.getElementById('regex-input');
    const testInput = document.getElementById('test-input');
    const highlightedText = document.getElementById('highlighted-text');
    const matchesCount = document.getElementById('matches-count');
    const validationMessage = document.getElementById('regex-validation');
    const matchedElements = document.getElementById('matched-elements');
    
    // Flag checkboxes
    const flagG = document.getElementById('flag-g');
    const flagI = document.getElementById('flag-i');
    const flagM = document.getElementById('flag-m');
    
    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Function to call the Python backend API
    async function processRegex() {
        const pattern = regexInput.value;
        const testText = testInput.value;
        
        if (!pattern || !testText) {
            highlightedText.innerHTML = testText;
            matchesCount.textContent = '0 matches';
            validationMessage.textContent = '';
            validationMessage.className = 'validation-message';
            matchedElements.innerHTML = '';
            return;
        }
        
        // Build flags string
        let flags = '';
        if (flagG.checked) flags += 'g';
        if (flagI.checked) flags += 'i';
        if (flagM.checked) flags += 'm';
        
        try {
            const response = await fetch('/api/regex', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pattern: pattern,
                    text: testText,
                    flags: flags
                }),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.valid) {
                highlightedText.innerHTML = data.highlighted_html;
                matchesCount.textContent = `${data.count} ${data.count === 1 ? 'match' : 'matches'}`;
                validationMessage.textContent = 'Valid regex pattern';
                validationMessage.className = 'validation-message success';
                
                // Display matched elements
                matchedElements.innerHTML = '';
                if (data.match_details && data.match_details.length > 0) {
                    data.match_details.forEach((match, index) => {
                        const matchElement = document.createElement('div');
                        matchElement.className = 'matched-element';
                        matchElement.innerHTML = `<span class="match-num">${index + 1}:</span> <code>${match}</code>`;
                        matchedElements.appendChild(matchElement);
                    });
                } else {
                    matchedElements.innerHTML = '<div class="no-matches">No matches found</div>';
                }
            } else {
                highlightedText.innerHTML = data.highlighted_html;
                matchesCount.textContent = '0 matches';
                validationMessage.textContent = `Invalid regex: ${data.error}`;
                validationMessage.className = 'validation-message error';
                matchedElements.innerHTML = '';
            }
        } catch (error) {
            console.error('Error:', error);
            validationMessage.textContent = `Error: ${error.message}`;
            validationMessage.className = 'validation-message error';
            matchedElements.innerHTML = '';
        }
    }
    
    // Debounced version to prevent too many API calls
    const debouncedProcessRegex = debounce(processRegex, 300);
    
    // Add event listeners
    regexInput.addEventListener('input', debouncedProcessRegex);
    testInput.addEventListener('input', debouncedProcessRegex);
    flagG.addEventListener('change', debouncedProcessRegex);
    flagI.addEventListener('change', debouncedProcessRegex);
    flagM.addEventListener('change', debouncedProcessRegex);
    
    // Initialize with example
    regexInput.value = '[A-Za-z]+';
    testInput.value = 'Hello World! This is a regex test.';
    processRegex(); // Initial call without debounce
}); 