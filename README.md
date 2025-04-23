# Interactive Regular Expressions Learning Platform

A comprehensive web-based platform for learning and practicing regular expressions (regex) through interactive lessons, quizzes, and a playground environment.

## Features

- **Interactive Learning**: Step-by-step lessons with visual examples
- **Regex Playground**: Test and visualize regex patterns in real-time
- **Quiz System**: Test your knowledge with interactive quizzes
- **Detailed Explanations**: Hover over regex components to see explanations
- **Progress Tracking**: Track your learning progress and quiz scores

## Project Structure

- **app.py**: Main Flask application with routes and backend logic
- **templates/**: HTML templates for different pages
  - `index.html`: Home page with introduction
  - `learn.html`: Interactive lesson pages
  - `quiz.html`: Quiz questions and interface
  - `results.html`: Quiz results and feedback
  - `playground.html`: Interactive regex testing environment
- **static/**: Static assets
  - `css/styles.css`: Styling for all pages
  - `js/script.js`: JavaScript for the regex playground

## Setup Instructions

1. Clone the repository:
   ```
   git clone [repository URL]
   ```

2. Navigate to the project directory:
   ```
   cd regex-learning-platform
   ```

3. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5001
   ```

## Development

The application uses:
- **Flask**: Web framework
- **HTML/CSS/JavaScript**: Frontend
- **Bootstrap**: Responsive UI components
- **Session Storage**: User progress tracking

## Requirements

- Python 3.6+
- Flask
- Web browser with JavaScript enabled

## Future Enhancements

- User accounts and persistent progress tracking
- More advanced lessons and quiz questions
- Custom regex challenge creation
- Social sharing of regex patterns
