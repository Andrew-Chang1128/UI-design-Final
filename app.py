from flask import Flask, render_template, request, jsonify, session
import re
import html
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'regex_learning_app_secret_key'  # Required for session

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

# Learning content in JSON format
LESSONS = [
    {
        "id": 1,
        "title": "What is Regex?",
        "content": "Regular expressions (regex) are patterns used to match character combinations in strings. In this tutorial, you'll learn how to use regular expressions to match and extract data.",
        "example_pattern": "cat",
        "example_text": "The cat sat on the catalogue.",
        "explanation": "The pattern 'cat' matches the first 'cat' in 'The cat sat on the catalogue' and also the first part of 'catalogue'."
    },
    {
        "id": 2,
        "title": "Character Classes",
        "content": "Character classes allow you to match any character from a specific set.",
        "example_pattern": "[a-z]",
        "example_text": "Hello123",
        "explanation": "The pattern [a-z] matches any lowercase letter in 'Hello123', which are 'e', 'l', 'l', and 'o'."
    },
    {
        "id": 3,
        "title": "Quantifiers",
        "content": "Quantifiers specify how many instances of a character, group, or character class must be present for a match to be found.",
        "example_pattern": "ha*",
        "example_text": "haaaa!",
        "explanation": "The pattern 'ha*' matches 'h' followed by zero or more 'a' characters. In 'haaaa!', it matches 'haaaa'."
    },
    {
        "id": 4,
        "title": "Anchors",
        "content": "Anchors match positions rather than characters. They include start of line (^) and end of line ($).",
        "example_pattern": "^Hello",
        "example_text": "Hello World\nHello again",
        "explanation": "The pattern '^Hello' matches 'Hello' only at the start of a line. In our multiline text, it matches the first 'Hello' and the 'Hello' after the newline."
    },
    {
        "id": 5,
        "title": "Groups & Ranges",
        "content": "Groups allow you to apply quantifiers to entire patterns. Ranges within character classes let you specify a range of characters.",
        "example_pattern": "([A-Z]\\w+)",
        "example_text": "The Quick Brown Fox Jumps",
        "explanation": "The pattern '([A-Z]\\w+)' matches words that start with a capital letter followed by one or more word characters."
    },
    {
        "id": 6,
        "title": "Regex Flags",
        "content": "Flags change how the matching behaves. Common flags include 'g' (global), 'i' (case-insensitive), and 'm' (multiline).",
        "example_pattern": "test",
        "example_text": "Test this test and this test again.",
        "explanation": "With the 'g' flag, the pattern 'test' will match all occurrences of 'test'. With 'i' flag, it will match 'Test' as well."
    }
]

# Quiz questions in JSON format
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which regex pattern matches all capitalized words?",
        "text": "The Quick Brown Fox Jumps",
        "options": [
            {"id": "a", "pattern": "[A-Z]\\w+"},
            {"id": "b", "pattern": "\\b[A-Z][a-z]*\\b"},
            {"id": "c", "pattern": "[A-Z][a-z]+"}
        ],
        "correct_answer": "b",
        "explanation": "\\b[A-Z][a-z]*\\b matches words that begin with a capital letter followed by zero or more lowercase letters, with word boundaries on both sides."
    },
    {
        "id": 2,
        "question": "Which regex pattern matches all digits in the text?",
        "text": "Room 404, Floor 2",
        "options": [
            {"id": "a", "pattern": "[0-9]"},
            {"id": "b", "pattern": "\\d"},
            {"id": "c", "pattern": "\\d+"}
        ],
        "correct_answer": "c",
        "explanation": "\\d+ matches one or more consecutive digits, which captures '404' and '2'."
    },
    {
        "id": 3,
        "question": "Which regex pattern matches valid email addresses?",
        "text": "Contact us at example@email.com or support@company.org",
        "options": [
            {"id": "a", "pattern": "\\w+@\\w+\\.\\w+"},
            {"id": "b", "pattern": "[a-z]+@[a-z]+\\.[a-z]+"},
            {"id": "c", "pattern": ".*@.*\\..*"}
        ],
        "correct_answer": "a",
        "explanation": "\\w+@\\w+\\.\\w+ matches one or more word characters, followed by @, more word characters, a period, and finally more word characters."
    },
    {
        "id": 4,
        "question": "Which regex pattern matches lines that start with 'Error:'?",
        "text": "Error: File not found\nWarning: Low battery\nError: Connection lost",
        "options": [
            {"id": "a", "pattern": "Error:"},
            {"id": "b", "pattern": "^Error:"},
            {"id": "c", "pattern": "Error:.*"}
        ],
        "correct_answer": "b",
        "explanation": "^Error: uses the ^ anchor to match 'Error:' only at the beginning of a line."
    }
]

# Initialize user session data
def init_user_session():
    if 'user_data' not in session:
        session['user_data'] = {
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lessons_viewed': [],
            'quiz_answers': {},
            'score': 0
        }

@app.route('/')
def index():
    # Reset user session data when accessing home page
    session.pop('user_data', None)
    return render_template('index.html')

@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    init_user_session()
    
    # Record lesson access in user session
    if 'lessons_viewed' in session['user_data'] and lesson_id not in session['user_data']['lessons_viewed']:
        session['user_data']['lessons_viewed'].append(lesson_id)
        session.modified = True
    
    # Find the requested lesson
    if 1 <= lesson_id <= len(LESSONS):
        lesson = LESSONS[lesson_id-1]
        next_id = lesson_id + 1 if lesson_id < len(LESSONS) else None
        
        return render_template('learn.html', 
                              lesson=lesson, 
                              next_id=next_id, 
                              has_next=lesson_id < len(LESSONS),
                              total_lessons=len(LESSONS))
    else:
        return "Lesson not found", 404

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    init_user_session()
    
    # Reset score and answers when starting a new quiz
    if question_id == 1 and request.method == 'GET':
        session['user_data']['score'] = 0
        session['user_data']['quiz_answers'] = {}
        session.modified = True
        print(f"Reset quiz: score={session['user_data']['score']}, answers={session['user_data']['quiz_answers']}")
    
    if request.method == 'POST':
        # Save the previous question answer
        prev_id = request.form.get('prev_question_id')
        if prev_id:
            prev_id = int(prev_id)
            selected_answer = request.form.get('answer')
            # Convert prev_id to string when using as dictionary key
            session['user_data']['quiz_answers'][str(prev_id)] = selected_answer
            
            # Check if answer is correct and update score
            if prev_id <= len(QUIZ_QUESTIONS):
                correct_answer = QUIZ_QUESTIONS[prev_id-1]['correct_answer']
                if selected_answer == correct_answer:
                    session['user_data']['score'] += 1
                    print(f"Correct answer for question {prev_id}! New score: {session['user_data']['score']}")
                else:
                    print(f"Wrong answer for question {prev_id}. Selected: {selected_answer}, Correct: {correct_answer}")
            
            session.modified = True
            print(f"Updated quiz data: score={session['user_data']['score']}, answers={session['user_data']['quiz_answers']}")
    
    # Find the requested question
    if 1 <= question_id <= len(QUIZ_QUESTIONS):
        question = QUIZ_QUESTIONS[question_id-1]
        next_id = question_id + 1 if question_id < len(QUIZ_QUESTIONS) else None
        
        # Get previously selected answer, if any
        selected_answer = session['user_data']['quiz_answers'].get(str(question_id), None)
        
        return render_template('quiz.html', 
                              question=question, 
                              next_id=next_id, 
                              has_next=question_id < len(QUIZ_QUESTIONS),
                              selected_answer=selected_answer,
                              total_questions=len(QUIZ_QUESTIONS))
    else:
        return "Question not found", 404

@app.route('/results')
def results():
    init_user_session()
    
    score = session['user_data']['score']
    total = len(QUIZ_QUESTIONS)
    percentage = (score / total) * 100 if total > 0 else 0
    
    print(f"Results page: score={score}, total={total}, answers={session['user_data']['quiz_answers']}")
    
    user_answers = {}
    for q_id_str, answer in session['user_data']['quiz_answers'].items():
        q_id = int(q_id_str)  # Convert the string key back to integer
        if 1 <= q_id <= len(QUIZ_QUESTIONS):
            question = QUIZ_QUESTIONS[q_id-1]
            is_correct = answer == question['correct_answer']
            
            # Find the selected option text
            selected_option = next((opt for opt in question['options'] if opt['id'] == answer), None)
            correct_option = next((opt for opt in question['options'] if opt['id'] == question['correct_answer']), None)
            
            user_answers[q_id_str] = {
                'question': question['question'],
                'selected': selected_option['pattern'] if selected_option else "No answer",
                'correct': correct_option['pattern'],
                'is_correct': is_correct,
                'explanation': question['explanation']
            }
    
    return render_template('results.html', 
                          score=score, 
                          total=total, 
                          percentage=percentage,
                          user_answers=user_answers)

@app.route('/playground')
def playground():
    return render_template('playground.html')

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