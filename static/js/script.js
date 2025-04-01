document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const regexInput = document.getElementById('regex-input');
    const testInput = document.getElementById('test-input');
    const highlightedText = document.getElementById('highlighted-text');
    const matchesCount = document.getElementById('matches-count');
    const validationMessage = document.getElementById('regex-validation');
    const matchedElements = document.getElementById('matched-elements');
    const regexDisplay = document.getElementById('regex-display');
    
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
    
    // Function to escape HTML
    function escapeHTML(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    // Function to render regex pattern with explanations
    function renderRegexExplanation(pattern, explanations) {
        if (!pattern) {
            regexDisplay.innerHTML = '';
            return;
        }
        
        // If no explanations were provided
        if (!explanations || !Array.isArray(explanations) || explanations.length === 0) {
            regexDisplay.innerHTML = escapeHTML(pattern);
            return;
        }
        
        // Sort explanations by start position
        const sortedExplanations = [...explanations].sort((a, b) => a.start - b.start);
        
        let html = '';
        let lastIndex = 0;
        
        for (const exp of sortedExplanations) {
            // Add any characters before this explanation
            if (exp.start > lastIndex) {
                const plainText = pattern.substring(lastIndex, exp.start);
                html += `<span class="regex-char">${escapeHTML(plainText)}</span>`;
            }
            
            // Add the explained segment with appropriate styling
            const segmentText = pattern.substring(exp.start, exp.end);
            const escapedText = escapeHTML(segmentText);
            
            // Determine CSS class based on pattern type
            let cssClass = 'regex-char';
            if (segmentText.startsWith('(')) {
                cssClass += ' regex-group';
            } else if (segmentText.startsWith('[')) {
                cssClass += ' regex-set';
            } else if (['*', '+', '?', '{'].includes(segmentText[0])) {
                cssClass += ' regex-quantifier';
            } else if (['^', '$', '\\b'].includes(segmentText)) {
                cssClass += ' regex-anchor';
            } else if (['.', '|', '\\'].includes(segmentText[0])) {
                cssClass += ' regex-special';
            }
            
            // Simplify the HTML structure for the tooltip
            html += `<span class="${cssClass}" data-explanation="${exp.explanation}">${escapedText}</span>`;
            
            lastIndex = exp.end;
        }
        
        // Add any remaining characters
        if (lastIndex < pattern.length) {
            const plainText = pattern.substring(lastIndex);
            html += `<span class="regex-char">${escapeHTML(plainText)}</span>`;
        }
        
        regexDisplay.innerHTML = html;
        
        // Add manual event listeners for each tooltip element
        document.querySelectorAll('.regex-char').forEach(el => {
            el.addEventListener('mouseenter', function(event) {
                if (this.dataset.explanation) {
                    // Create tooltip dynamically
                    let tooltip = document.getElementById('regex-tooltip');
                    if (!tooltip) {
                        tooltip = document.createElement('div');
                        tooltip.id = 'regex-tooltip';
                        tooltip.className = 'regex-tooltip';
                        document.getElementById('tooltip-container').appendChild(tooltip);
                    }
                    
                    // Set tooltip content
                    tooltip.textContent = this.dataset.explanation;
                    
                    // Calculate position based on element and window
                    const rect = this.getBoundingClientRect();
                    
                    // Position tooltip centered above the element
                    const centerX = rect.left + rect.width / 2;
                    tooltip.style.left = `${centerX}px`;
                    tooltip.style.top = `${rect.top - 15}px`;
                    
                    // Show the tooltip
                    tooltip.style.display = 'block';
                    
                    // Ensure tooltip is fully visible (not clipped)
                    setTimeout(() => {
                        const tooltipRect = tooltip.getBoundingClientRect();
                        
                        // Adjust horizontal position if needed
                        if (tooltipRect.right > window.innerWidth) {
                            tooltip.style.left = `${window.innerWidth - tooltipRect.width - 10}px`;
                        }
                        if (tooltipRect.left < 0) {
                            tooltip.style.left = '10px';
                        }
                        
                        // Adjust vertical position if needed
                        if (tooltipRect.top < 0) {
                            tooltip.style.top = '10px';
                        }
                    }, 0);
                }
            });
            
            el.addEventListener('mouseleave', function() {
                const tooltip = document.getElementById('regex-tooltip');
                if (tooltip) {
                    tooltip.style.display = 'none';
                }
            });
        });
    }
    
    // Function to call the Python backend API
    async function processRegex() {
        const pattern = regexInput.value;
        const testText = testInput.value;
        
        if (!pattern) {
            highlightedText.innerHTML = testText ? escapeHTML(testText) : '';
            matchesCount.textContent = '0 matches';
            validationMessage.textContent = '';
            validationMessage.className = 'validation-message';
            matchedElements.innerHTML = '';
            regexDisplay.innerHTML = '';
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
                    text: testText || '', // Handle empty test text
                    flags: flags
                }),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Update the regex pattern display with explanations
            renderRegexExplanation(pattern, data.pattern_explanation);
            
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
            regexDisplay.innerHTML = escapeHTML(pattern);
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