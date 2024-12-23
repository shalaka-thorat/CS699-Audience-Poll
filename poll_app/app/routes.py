import re
import qrcode
from io import BytesIO
import base64
from flask_login import login_required, current_user
from flask import request, redirect, url_for, render_template, flash
from app import create_app, login_manager
from app import auth
from app import poll_service as ps
from app import analysis
from app import recommend


app = create_app()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return auth.load_user(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(f"login called with method {request.method}")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # print(f"email is {email}")
        # print(f"password is {password}")
        if (auth.login(email, password)):
            return redirect(url_for("home"))
        else:
            flash('Invalid Email/Password. Please Try Again')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    auth.logout()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        age = request.form['age']

        if (auth.signup(email, password, gender=gender, age=age)):
            if (auth.login(email, password)):
                return redirect(url_for("home"))
            return redirect(url_for("login"))
    return render_template("signup.html")


# initially just show all polls to a user, unless he has voted in atleast more than 1 poll
# after that, using the voted polls of this user, recommend him 10 new polls
@app.route('/home')
@login_required
def home():
    all_polls=ps.fetch_polls()
    # unvoted_polls = ps.fetch_unvoted_polls(user_id=current_user.id)
    # print(len(unvoted_polls))

    voted_polls = ps.get_polls_voted_by_user(user_id=current_user.id)

    recommended_polls = None
    if (len(voted_polls) != 0):
        recommended_polls = recommend.get_recommended_polls(all_polls, voted_polls)

    polls = ps.fetch_unreported_polls_by_user(user_id=current_user.id)

    if 'q' in request.args:
        query = request.args.get('q').lower()
        polls = [p for p in polls if re.search(query, p.title.lower()) or re.search(query, p.creator_username.lower()) or re.search(query, p.created_at.strftime('%B %d, %Y at %I:%M %p').lower())]
    
    return render_template("custom_polls.html", user=current_user, polls=polls, page="home", recommended_polls=recommended_polls)


@app.route('/create_poll', methods=['GET', 'POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        poll = ps.create_poll(title=title, description=description, user_id=current_user.id)
        options = [value for key, value in request.form.items() if key.startswith('option')]
        ps.create_options(options=options, poll_id=poll.id)
        return redirect(url_for('my_polls'))
    return render_template('create_poll.html')

@app.route('/poll/<poll_id>')
def poll(poll_id):
    if current_user.is_authenticated and ps.check_history(poll_id=poll_id, user_id=current_user.id):
        return redirect(url_for('results', poll_id=poll_id))
    poll = ps.get_poll(poll_id=poll_id)
    return render_template("poll.html", poll=poll)

@app.route("/results/<poll_id>", methods=['GET', 'POST'])
@login_required
def results(poll_id):
    if request.method == 'POST':
        selected_option_id=request.form['selected_option']
        ps.vote(user_id=current_user.id, poll_id=poll_id, option_id=selected_option_id)
    return render_template("poll_results.html", poll=ps.get_poll(poll_id=poll_id))

@app.route("/home/my_votes")
@login_required
def my_votes():
    polls = ps.get_polls_voted_by_user(user_id=current_user.id)
    if 'q' in request.args:
        query = request.args.get('q').lower()
        polls = [p for p in polls if re.search(query, p.title.lower()) or re.search(query, p.creator_username.lower()) or re.search(query, p.created_at.strftime('%B %d, %Y at %I:%M %p').lower())]
    
    return render_template("custom_polls.html", user=current_user, polls=polls, page="history")
    
@app.route("/home/my_polls")
@login_required
def my_polls():
    polls = ps.get_polls_created_by_user(user_id=current_user.id)
    if 'q' in request.args:
        query = request.args.get('q').lower()
        polls = [p for p in polls if re.search(query, p.title.lower()) or re.search(query, p.creator_username.lower()) or re.search(query, p.created_at.strftime('%B %d, %Y at %I:%M %p').lower())]
    
    return render_template("my_polls.html", user=current_user, polls=polls, page="poll")

@app.route("/home/my_polls/delete/<poll_id>")
@login_required
def delete_poll(poll_id):
    ps.delete_poll(user_id=current_user.id, poll_id=poll_id)
    if current_user.is_admin:
        return redirect(url_for('admin_polls'))
    return redirect(url_for('my_polls'))

@app.route("/delete_account")
@login_required
def delete_account():
    auth.delete_user(user_id=current_user.id)
    return redirect(url_for('index'))

@app.route("/share/<poll_id>")
@login_required
def share_poll(poll_id):
    url = request.url
    qr = qrcode.make(url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_img_bytes= base64.b64encode(buffered.getvalue()).decode()
    return render_template('share_poll.html', user=current_user, url=url, qr_img_bytes=qr_img_bytes)

@app.route('/admin')
@auth.admin_required
def admin_users():
    users = auth.get_all_users()
    if 'q' in request.args:
        query = request.args.get('q').lower()
        users = [u for u in users if re.search(query, u.email.lower())]
    return render_template("admin_users.html", user=current_user, users=users, page="users")

@app.route('/admin/delete/<user_id>')
@auth.admin_required
def admin_delete(user_id):
    auth.delete_user(user_id=user_id, initiator='admin')
    return redirect(url_for('admin_users'))

@app.route('/admin/polls')
@auth.admin_required
def admin_polls():
    polls = ps.fetch_polls()
    if 'q' in request.args:
        query = request.args.get('q').lower()
        polls = [p for p in polls if re.search(query, p.title.lower()) or re.search(query, p.creator_username.lower()) or re.search(query, p.created_at.strftime('%B %d, %Y at %I:%M %p').lower())]
    return render_template("admin_polls.html", user=current_user, polls=polls, page="polls")

@app.route("/analyse/<poll_id>")
@auth.login_required
def analyse(poll_id):
    poll = ps.get_poll(poll_id=poll_id)
    if poll and current_user.id == poll.user_id:
        options = ps.get_poll_options(poll_id=poll_id)
        votes_img= analysis.create_poll_vote_dist_plot(options=options)
        option_gender_dist_plot = analysis.create_stacked_vote_dist_plot_by_gender(options=options)
        poll_gender_dist_plot = analysis.create_votes_gender_distribution_for_poll(poll=poll)
        gender_option_dist_plot = analysis.all_gender_option_distribution_plots(poll=poll)
        return render_template('analysis.html', votes_img=votes_img, option_gender_dist_plot=option_gender_dist_plot, poll_gender_dist_plot=poll_gender_dist_plot, gender_option_dist_plot=gender_option_dist_plot)
    return redirect(url_for('my_polls'))

@app.route("/flag/<poll_id>")
@auth.login_required
def report(poll_id):
    ps.report_poll(user_id=current_user.id, poll_id=poll_id)
    return redirect(url_for('home'))

@app.route("/flag/reported_polls/")
@auth.admin_required
def admin_reported_polls():
    polls = ps.fetch_reported_polls()
    return render_template('admin_reported_polls.html', user=current_user, polls=polls, page="reports")

@app.route("/reject/<poll_id>")
@auth.admin_required
def reject_flag(poll_id):
    ps.reject_flag(poll_id=poll_id)
    return redirect(url_for('admin_polls'))