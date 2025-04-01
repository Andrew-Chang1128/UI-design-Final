from flask import Flask, render_template, request, jsonify
import re
import html
import json

app = Flask(__name__)

# Regex component explanations
REGEX_EXPLANATIONS = {
    # Character classes
    r'\d': 'Matches any digit (0-9)',
    r'\w': 'Matches any word character (alphanumeric + underscore)',
    r'\s': 'Matches any whitespace character (space, tab, newline)',
    r'[a-z]': 'Matches any lowercase letter from a to z',
    r'[A-Z]': 'Matches any uppercase letter from A to Z',
    r'[0-9]': 'Matches any digit from 0 to 9',
    r'[aeiou]': 'Matches any vowel',
    
    # Anchors
    r'^': 'Matches the beginning of a string',
    r'$': 'Matches the end of a string',
    r'\b': 'Matches a word boundary',
    
    # Quantifiers
    r'*': 'Matches 0 or more of the preceding character',
    r'+': 'Matches 1 or more of the preceding character',
    r'?': 'Matches 0 or 1 of the preceding character',
    r'{n}': 'Matches exactly n of the preceding character',
    r'{n,}': 'Matches n or more of the preceding character',
    r'{n,m}': 'Matches between n and m of the preceding character',
    
    # Groups and alternation
    r'(...)': 'Capturing group. Groups multiple tokens together and captures the result',
    r'(?:...)': 'Non-capturing group. Groups multiple tokens together without capturing',
    r'|': 'Alternation. Acts like a boolean OR',
    
    # Special characters
    r'.': 'Matches any character except newline',
    r'\\': 'Escapes a special character',
    
    # Lookaheads and lookbehinds
    r'(?=...)': 'Positive lookahead. Matches if followed by ...',
    r'(?!...)': 'Negative lookahead. Matches if not followed by ...',
    r'(?<=...)': 'Positive lookbehind. Matches if preceded by ...',
    r'(?<!...)': 'Negative lookbehind. Matches if not preceded by ...',
}

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
            'match_details': [],
            'pattern_explanation': {}
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
        
        # Generate pattern explanation
        pattern_explanation = explain_pattern(pattern)
        
        return jsonify({
            'valid': True,
            'matches': matches,
            'highlighted_html': highlighted_html,
            'count': len(matches),
            'match_details': match_details,
            'pattern_explanation': pattern_explanation
        })
        
    except re.error as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'matches': [],
            'highlighted_html': html.escape(test_text),
            'count': 0,
            'match_details': [],
            'pattern_explanation': {}
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

def explain_pattern(pattern):
    """Break down a regex pattern into components and provide explanations."""
    explanation = []
    i = 0
    
    # Special case for capturing groups
    in_group = False
    group_start = 0
    
    # Keep track of component positions and explanations
    components = []
    
    while i < len(pattern):
        found_component = False
        
        # Check for start of a group
        if pattern[i] == '(' and not in_group:
            in_group = True
            group_start = i
            i += 1
            continue
            
        # Check for end of a group
        if pattern[i] == ')' and in_group:
            group_text = pattern[group_start:i+1]
            
            # Check for non-capturing group
            if group_text.startswith('(?:'):
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Non-capturing group. Groups multiple tokens together without capturing.'
                })
            # Check for lookahead/lookbehind
            elif group_text.startswith('(?='):
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Positive lookahead. Matches if followed by the pattern inside.'
                })
            elif group_text.startswith('(?!'):
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Negative lookahead. Matches if not followed by the pattern inside.'
                })
            elif group_text.startswith('(?<='):
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Positive lookbehind. Matches if preceded by the pattern inside.'
                })
            elif group_text.startswith('(?<!'):
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Negative lookbehind. Matches if not preceded by the pattern inside.'
                })
            else:
                components.append({
                    'start': group_start,
                    'end': i+1,
                    'pattern': group_text,
                    'explanation': 'Capturing group #1. Groups multiple tokens together and creates a capture group for extracting a substring or using a backreference.'
                })
                
            in_group = False
            found_component = True
            i += 1
            continue
        
        # Check for character classes
        if i < len(pattern) - 1 and pattern[i] == '\\':
            if pattern[i+1] in 'dswDSW':
                char_class = pattern[i:i+2]
                explanation_text = ''
                
                if char_class == '\\d':
                    explanation_text = 'Matches any digit (0-9)'
                elif char_class == '\\w':
                    explanation_text = 'Matches any word character (alphanumeric + underscore)'
                elif char_class == '\\s':
                    explanation_text = 'Matches any whitespace character (space, tab, newline)'
                elif char_class == '\\D':
                    explanation_text = 'Matches any non-digit character'
                elif char_class == '\\W':
                    explanation_text = 'Matches any non-word character'
                elif char_class == '\\S':
                    explanation_text = 'Matches any non-whitespace character'
                
                components.append({
                    'start': i,
                    'end': i+2,
                    'pattern': char_class,
                    'explanation': explanation_text
                })
                
                found_component = True
                i += 2
                continue
                
        # Check for character sets
        if pattern[i] == '[':
            set_start = i
            i += 1
            # Find the end of the character set
            while i < len(pattern) and pattern[i] != ']':
                if i < len(pattern) - 1 and pattern[i] == '\\':
                    i += 2  # Skip escaped character
                else:
                    i += 1
            
            if i < len(pattern) and pattern[i] == ']':
                char_set = pattern[set_start:i+1]
                
                if char_set == '[a-z]':
                    explanation_text = 'Matches any lowercase letter from a to z'
                elif char_set == '[A-Z]':
                    explanation_text = 'Matches any uppercase letter from A to Z'
                elif char_set == '[0-9]':
                    explanation_text = 'Matches any digit from 0 to 9'
                elif char_set == '[a-zA-Z]':
                    explanation_text = 'Matches any letter, uppercase or lowercase'
                elif char_set == '[a-zA-Z0-9]':
                    explanation_text = 'Matches any alphanumeric character'
                else:
                    explanation_text = f'Character set. Matches any single character from the set: {char_set}'
                
                components.append({
                    'start': set_start,
                    'end': i+1,
                    'pattern': char_set,
                    'explanation': explanation_text
                })
                
                found_component = True
                i += 1
                continue
        
        # Check for quantifiers
        if pattern[i] in '*+?':
            quantifier = pattern[i]
            explanation_text = ''
            
            if quantifier == '*':
                explanation_text = 'Matches 0 or more of the preceding character or group'
            elif quantifier == '+':
                explanation_text = 'Matches 1 or more of the preceding character or group'
            elif quantifier == '?':
                explanation_text = 'Matches 0 or 1 of the preceding character or group'
            
            components.append({
                'start': i,
                'end': i+1,
                'pattern': quantifier,
                'explanation': explanation_text
            })
            
            found_component = True
            i += 1
            continue
            
        # Check for curly brace quantifiers
        if pattern[i] == '{':
            brace_start = i
            i += 1
            # Find the end of the brace
            while i < len(pattern) and pattern[i] != '}':
                i += 1
            
            if i < len(pattern) and pattern[i] == '}':
                brace_quantifier = pattern[brace_start:i+1]
                
                # Parse the quantifier to determine the explanation
                if ',' not in brace_quantifier:
                    # {n}
                    n = brace_quantifier.strip('{}')
                    explanation_text = f'Matches exactly {n} of the preceding character or group'
                else:
                    parts = brace_quantifier.strip('{}').split(',')
                    if parts[1].strip() == '':
                        # {n,}
                        n = parts[0].strip()
                        explanation_text = f'Matches {n} or more of the preceding character or group'
                    else:
                        # {n,m}
                        n = parts[0].strip()
                        m = parts[1].strip()
                        explanation_text = f'Matches between {n} and {m} of the preceding character or group'
                
                components.append({
                    'start': brace_start,
                    'end': i+1,
                    'pattern': brace_quantifier,
                    'explanation': explanation_text
                })
                
                found_component = True
                i += 1
                continue
                
        # Check for anchors and other special characters
        if pattern[i] in '^$.|':
            special_char = pattern[i]
            explanation_text = ''
            
            if special_char == '^':
                explanation_text = 'Matches the beginning of a string'
            elif special_char == '$':
                explanation_text = 'Matches the end of a string'
            elif special_char == '.':
                explanation_text = 'Matches any character except newline'
            elif special_char == '|':
                explanation_text = 'Alternation. Acts like a boolean OR between options'
            
            components.append({
                'start': i,
                'end': i+1,
                'pattern': special_char,
                'explanation': explanation_text
            })
            
            found_component = True
            i += 1
            continue
            
        # If no special component was found, just move to the next character
        if not found_component:
            i += 1
    
    return components

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=5001) 
    app.run(debug=True, port=5001) 