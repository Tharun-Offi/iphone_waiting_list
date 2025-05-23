# iPhone Waiting List Application

This is a Flask-based web application that allows users to sign up for a waiting list for the iPhone 16 pre-order. The application includes features such as referral tracking, rankings, and email notifications.

## Features

- **Signup Form**: Users can sign up with their name, email, phone number, and an optional referral code.
- **Referral System**: Users can refer others using a unique referral code, and the number of referred persons is tracked.
- **Rankings**: Displays a leaderboard of users based on their referral count.
- **Email Notifications**: Sends a confirmation email with a coupon code to users upon successful signup.
- **Top 10 Rankings**: Allows users to view the top 10 users with the highest referrals.

## Prerequisites

- Python 3.7 or higher
- Flask
- SQLite3

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd iphone_waiting_list
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database and Run the applications:

   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure

```
iphone_waiting_list/
├── app.py                # Main application file
├── templates/            # HTML templates
│   ├── index.html        # Signup page
│   ├── rank.html         # Rankings page
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css     # Stylesheet
│   ├── js/
│   │   └── script.js     # JavaScript file
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
```

## Contact

For any questions or issues, please contact:

**Email**: tharunmctv@gmail.com
