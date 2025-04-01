from flask import Flask, render_template, request, jsonify
import re
import html

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/regex', methods=['POST'])
def process_regex():
    data = request.json
    
    pattern = data.get('pattern', '')
    test_text = data.get('text', '')
    flags = data.get('flags', '')
    
    if not pattern or not test_text:
        return jsonify({
            'valid': True,
            'matches': [],
            'highlighted_html': html.escape(test_text),
            'count': 0,
            'match_details': []
        })
    
    # Convert flags to Python re flags
    flag_value = 0
    if 'i' in flags:
        flag_value |= re.IGNORECASE
    if 'm' in flags:
        flag_value |= re.MULTILINE
    
    try:
        regex = re.compile(pattern, flag_value)
        
        # First escape the HTML to display it safely
        escaped_text = html.escape(test_text)
        
        # Find all matches with positions in the original text
        matches = []
        match_details = []
        
        for match in regex.finditer(test_text):
            match_text = match.group(0)
            matches.append({
                'index': match.start(),
                'length': len(match_text),
                'text': match_text
            })
            match_details.append(html.escape(match_text))
        
        # Generate highlighted HTML
        highlighted_html = highlight_matches_in_escaped_text(test_text, escaped_text, matches)
        
        return jsonify({
            'valid': True,
            'matches': matches,
            'highlighted_html': highlighted_html,
            'count': len(matches),
            'match_details': match_details
        })
        
    except re.error as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'matches': [],
            'highlighted_html': html.escape(test_text),
            'count': 0,
            'match_details': []
        })

def highlight_matches_in_escaped_text(original_text, escaped_text, matches):
    """Highlight matches in the escaped text by carefully mapping positions"""
    result = escaped_text
    segments = []
    last_end = 0
    
    # Sort matches by their start position
    sorted_matches = sorted(matches, key=lambda m: m['index'])
    
    for match in sorted_matches:
        start = match['index']
        end = start + match['length']
        
        # Before the match
        if start > last_end:
            pre_match_original = original_text[last_end:start]
            pre_match_escaped = html.escape(pre_match_original)
            segments.append(pre_match_escaped)
        
        # The match itself
        match_original = original_text[start:end]
        match_escaped = html.escape(match_original)
        segments.append(f'<span class="highlight">{match_escaped}</span>')
        
        last_end = end
    
    # Add any remaining text after the last match
    if last_end < len(original_text):
        post_match_original = original_text[last_end:]
        post_match_escaped = html.escape(post_match_original)
        segments.append(post_match_escaped)
    
    return ''.join(segments)

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5001) 
    app.run(debug=True, port=5001) 