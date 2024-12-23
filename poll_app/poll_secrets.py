# dont forget to finally delete this database and start a new one when rolling app to production
# otherwise many dummy users and admin users (dangerous) have been created
admins = {
    "admin@gmail.com": "12345"
}

db_uri = "sqlite:///poll_app.db"
db_secret_key = 'your_secret_key'