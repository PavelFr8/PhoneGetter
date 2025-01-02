# **Website Guide**

Website pulls data from a database, visualizes it, and presents it in a user-friendly format. 
Designed specifically for teachers, the website provides the ability to remotely manage phones in virtual class.

# Technologies Used

## Frontend Technologies
- **HTML**: For structuring the content of the web pages.
- **CSS**: For styling webpage elements.
- **JavaScript**: For interactivity and handling dynamic content.
- **AJAX (Fetch API)**: For asynchronous requests to the backend.
- **Bootstrap**: Framework for building responsive, mobile-first web pages.

## Backend Technologies
- **Python (Flask)**: Website framework.
- **Flask-WTF**: Used for handling forms and CSRF protection.
- **SQLAlchemy**: Database interaction.
- **Jinja2**: Templating engine in Flask for dynamically generating HTML.
- **PostgreSQL**: Database.

## Structure

```commandline
├── app/
│   ├── __init__.py              # Application initialization
│   ├── models.py                # Database models
│   ├── api/                     # PhoneGetter API
│   ├── errors/                  # Error handling
│   ├── modules/                 # Application modules (main, settings, register, etc.)
│   │   ├── main/                # Main module (e.g., homepage)
│   │   ├── settings/            # User settings (password change, etc.)
│   │   ├── register/            # Registration and login
│   │   ├── classes/             # Device and class management, teachers dashboard
│   │   ├── phone_history/       # Phone in device history
│   ├── static/                  # Static assets (CSS, images, JS)
│   ├── templates/               # HTML templates
│   ├── translations/            # Localization (e.g., Russian)
│   ├── utils/                   # Utility functions
```