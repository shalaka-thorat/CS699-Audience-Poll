from poll_secrets import db_uri, db_secret_key, admins
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'index'


def add_dummy_users(user_count):
    from app import auth
    for i in range(user_count//2):
        auth.signup(email=f"fstudent{i}@example.com", password="123ABCabc#", age=24, gender="female")
        auth.signup(email=f"mstudent{i}@example.com", password="123ABCabc#", age=24, gender="male")

dummy_polls = {
    'Baseball Heroes': 'Celebrate the achievements and inspiring journeys of the greatest baseball legends to ever play the game.',
    'Microservices': 'Understand the architecture, scalability, and modularity of microservices for modern web applications.',
    'Boxing Champions': 'Explore the stories of the greatest boxing champions and their iconic fights that defined the sport.',
    'Musical Extravaganza': 'Experience unforgettable music-filled cinematic tales that will leave you inspired and entertained.',
    'Swimming Techniques': 'Master swimming styles like freestyle, butterfly, and backstroke to enhance your aquatic skills.',
    'War Epics': 'Dive into epic tales of bravery, heroism, and conflict set during iconic wars throughout history.',
    'Tennis Grand Slams': 'Learn about the four biggest tennis tournaments, their history, and the legends who triumphed there.',
    'Dynamic Programming': 'Solve complex problems efficiently using the principles and techniques of dynamic programming.',
    'Marathon Tips': 'Prepare for long-distance running success with proven techniques, endurance training, and motivation tips.',
    'Skating Stars': 'Relive the iconic moments of figure skating champions and their breathtaking performances on ice.',
    'Algorithms Basics': 'Master essential algorithms like sorting, searching, and recursion to strengthen your programming skills.',
    'Action Blockbusters': 'High-octane action movies packed with thrilling sequences and unforgettable stunts.',
    'Gymnastics Skills': 'Learn to master flips, balances, and routines with professional gymnastics techniques and tips.',
    'Golf Legends': 'Discover the inspiring stories of the greatest golfers who have graced the greens and won major championships.',
    'Code Optimization': 'Learn how to improve code performance and efficiency with techniques like profiling, caching, and refactoring.',
    'Python Basics': 'Learn Python fundamentals for programming, from variables to control flow, and become confident in coding.',
    'Time Travel Stories': 'Explore fascinating movies and tales that delve into the thrilling concept of time travel.',
    'Clean Code': 'Master the art of writing clean, maintainable, and readable code with structured techniques and best practices.',
    'Sports Movies': 'Watch inspirational movies about athletes overcoming obstacles and achieving greatness in their sports.',
    'Badminton Masters': 'Discover techniques to improve your badminton gameplay, from smashing to strategic court positioning.',
    'Comedy Gold': 'Laugh out loud with timeless comedies that never fail to bring smiles and endless humor.',
    'Olympic History': 'Dive into the rich history of the Olympics and uncover the milestones that shaped the games.',
    'Graph Algorithms': 'Study graph traversal techniques like BFS, DFS, and Dijkstra’s algorithm to solve graph-based problems.',
    'Concurrency': 'Learn threading, multiprocessing, and parallel programming to make your applications more efficient.',
    'Cloud Computing': 'Master the basics of cloud computing with AWS, Azure, GCP, and learn about serverless architecture.',
    'Superhero Epics': 'Watch thrilling superhero adventures with larger-than-life characters and action-packed sequences.',
    'Documentary Gems': 'Learn and explore the world through insightful and educational documentary films.',
    'Debugging Tips': 'Improve debugging skills with systematic techniques for identifying and resolving code issues efficiently.',
    'Space Adventures': 'Dive into movies set in the vastness of space, exploring unknown planets and galaxies.',
    'Fantasy Worlds': 'Immerse yourself in magical realms filled with enchanting stories, mythical creatures, and epic adventures.',
    'Backend APIs': 'Learn how to design and implement RESTful APIs for backend web services and applications.',
    'Web Frameworks': 'Discover the power of Python frameworks like Flask, Django, and FastAPI to build web applications.',
    'Version Control': 'Master Git for tracking changes, collaborating on projects, and managing your codebase effectively.',
    'Unit Testing': 'Learn the importance of unit tests in applications and improve the quality of your code.',
    'Volleyball Basics': 'Master serving, spiking, and teamwork strategies to excel in volleyball.',
    'Surfing Legends': 'Celebrate the stories and achievements of legendary surfers who dominated the waves.',
    'AI Basics': 'Explore artificial intelligence concepts and learn how AI is transforming the world around us.',
    'Hockey Strategies': 'Understand advanced tactics and strategies used in modern hockey to outplay opponents.',
    'Wrestling Superstars': 'Discover the incredible stories of iconic wrestlers and their most memorable matches.',
    'Indie Treasures': 'Unearth hidden gems in indie films and celebrate the creativity of independent filmmakers.',
    'Oscar Winners': 'A look at award-winning movies that captivated audiences and critics alike with brilliant storytelling.',
    'Database Basics': 'Understand relational databases, SQL queries, and how to effectively design database schemas.',
    'Frontend Design': 'Build visually appealing and user-friendly web designs with HTML, CSS, and modern JavaScript.',
    'Cricket Records': 'Explore amazing cricketing achievements and world records that continue to inspire fans.',
    'Romantic Classics': 'Relive timeless tales of love, relationships, and enduring romance in classic films.',
    'Football Skills': 'Improve your dribbling, passing, and scoring with tips from the best football players in the world.',
    'Horror Movie Classics': 'Frightening tales in the horror genre that will keep you on the edge of your seat.',
    'Basketball Legends': 'Discover the inspiring stories of the greatest basketball players of all time.',
    'Sci-Fi Masterpieces': 'Explore iconic science fiction movies that delve into futuristic and imaginative worlds.',
    'Cult Classics': 'Films with a loyal and passionate following that have stood the test of time.',
    'Drama Hits': 'Emotional and captivating stories that touch the heart and leave a lasting impact.',
    'Formula 1 Greats': 'Relive the greatest moments and stories of legendary Formula 1 drivers.',
    'Animated Wonders': 'Celebrate the magic of animated movies loved by all generations.',
    'ML Libraries': 'Explore powerful machine learning libraries like TensorFlow, PyTorch, and Scikit-Learn.',
    'Mystery Thrillers': 'Dive into gripping mysteries and suspenseful stories that keep you guessing till the end.',
    'Object-Oriented Concepts': 'Master OOP concepts like inheritance, polymorphism, and encapsulation for efficient coding.',
    'Soccer Tactics': 'Understand modern soccer formations, tactics, and strategies to dominate the field.',
    'Cycling Techniques': 'Improve your speed, endurance, and efficiency with advanced cycling techniques.',
    'Data Structures': 'Master essential data structures like arrays, trees, heaps, and hash tables to enhance programming skills.',
    'Historical Dramas': 'Stories based on pivotal historical events that shaped the world as we know it.',
    'Python Libraries': 'Dive deep into Python libraries like NumPy, Pandas, and Matplotlib to enhance your data analysis projects.',
    'Programming Paradigms': 'Learn about functional, procedural, and object-oriented programming approaches.',
    'Code Refactoring': 'Refactor your code for improved readability, maintainability, and performance.',
    'Frontend Frameworks': 'Explore JavaScript frameworks like React, Angular, and Vue for modern web development.'
}

def add_dummy_poll(creator_email, title, description):
    from app import models
    user_id = models.User.query.filter_by(email=creator_email).first().id
    existing_poll = db.session.query(models.Poll).filter_by(title=title, user_id=user_id).first()
    if not existing_poll:
        poll = models.Poll(title=title, description=description, user_id=user_id)
        db.session.add(poll)
        db.session.commit()
        options=["a", "b"]
        for text in options:
            option = models.Option(text=text, poll_id=poll.id)
            db.session.add(option)
        db.session.commit()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SECRET_KEY'] = db_secret_key

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import models
        db.create_all()
        from app import auth
        auth.add_admins(admins)

        # adding dummy data
        add_dummy_users(20)
        
        dummy_polls_list = list(dummy_polls.items())
        for i in range (len(dummy_polls)//2):
            add_dummy_poll("mstudent1@example.com", dummy_polls_list[i][0], dummy_polls_list[i][1])
        
        for i in range (len(dummy_polls)//2, len(dummy_polls)//2 + len(dummy_polls)//4):
            add_dummy_poll("fstudent1@example.com", dummy_polls_list[i][0], dummy_polls_list[i][1])

        for i in range (len(dummy_polls)//2 + len(dummy_polls)//4, len(dummy_polls)):
            add_dummy_poll("mstudent2@example.com", dummy_polls_list[i][0], dummy_polls_list[i][1])

        # voter_id = models.User.query.filter_by(email="mstudent0@example.com").first().id
        # from app import poll_service
        # poll_service.vote(15, 1, voter_id)
        # poll_service.vote(16, 1, voter_id)
        # poll_service.vote(18, 1, voter_id)

    return app