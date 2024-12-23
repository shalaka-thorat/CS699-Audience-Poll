from app import db
from app.models import User, Poll, Option, Vote, UserPollReport
from sqlalchemy import func

def create_poll(title, description, user_id):
    poll = Poll(title=title, description=description, user_id=user_id)
    db.session.add(poll)
    db.session.commit()
    return poll
    
def create_options(options, poll_id):
    for text in options:
        option = Option(text=text, poll_id=poll_id)
        db.session.add(option)
    db.session.commit()

def fetch_unvoted_polls(user_id):
    polls =  fetch_polls()
    my_voted_polls = [poll for poll in polls if not check_history(user_id=user_id, poll_id=poll.id)]
    return my_voted_polls
    
def fetch_polls():
    return Poll.query.order_by(Poll.created_at.desc()).all()

def fetch_unreported_polls_by_user(user_id):    
    reported_polls = db.session.query(UserPollReport.poll_id).filter_by(user_id=user_id).subquery()
    unreported_polls = db.session.query(Poll).filter(Poll.id.notin_(db.session.query(reported_polls)))
    user_created_polls = Poll.query.filter_by(user_id=user_id)
    accessible_polls = unreported_polls.union(user_created_polls).all()
    return accessible_polls

def fetch_reported_polls():
    reported_poll_ids = db.session.query(UserPollReport.poll_id)
    reported_polls = Poll.query.filter(Poll.id.in_(reported_poll_ids)).all()
    return reported_polls


def get_poll(poll_id):
    return Poll.query.filter_by(id=poll_id).first()

def vote(poll_id, option_id, user_id):
    is_already_voted = check_history(user_id=user_id,poll_id=poll_id)
    if not is_already_voted:
        vote = Vote(user_id=user_id, poll_id=poll_id, option_id=option_id)
        db.session.add(vote)
        db.session.commit()
        # add_vote_history(user_id=user_id, poll_id=poll_id, vote_id=vote.id)
    
def get_vote_counts_for_poll(option_id):
    vote_count = (
        db.session.query(func.count(Vote.id))
        .filter(Vote.option_id==option_id)
        .scalar()
    )
    return vote_count

# def add_vote_history(user_id, poll_id, vote_id):
#     # history = UserVoteHistory(user_id=user_id, poll_id=poll_id, vote_id=vote_id)
#     db.session.add(history)
#     db.session.commit()
        
def check_history(user_id, poll_id):
    if Vote.query.filter_by(user_id=user_id, poll_id=poll_id).first():
        return True
    # if UserVoteHistory.query.filter_by(user_id=user_id, poll_id=poll_id).first():
        # return True
    return False

def check_owner(user_id, poll_id):
    if Poll.query.filter_by(user_id=user_id, id=poll_id).first():
        return True
    return False

def get_polls_voted_by_user(user_id):
    polls =  fetch_polls()
    my_voted_polls = [poll for poll in polls if check_history(user_id=user_id, poll_id=poll.id)]
    return my_voted_polls

def get_polls_created_by_user(user_id):
    return Poll.query.filter_by(user_id=user_id)

def delete_poll(user_id, poll_id):
    user = User.query.filter_by(id=user_id).first()
    poll = Poll.query.get(poll_id)

    if user is None or poll is None:
        return

    if user.is_admin or check_owner(user_id, poll_id):
        db.session.delete(poll)
        db.session.commit()

def get_poll_options(poll_id):
    return Option.query.filter_by(poll_id=poll_id).all()

def get_all_unique_genders():
    genders = db.session.query(User.gender).distinct().all()
    # for user in User.query.distinct(User.gender):
    #     genders.append(user.gender)
    return [gender[0] for gender in genders]

def vote_count_by_poll_and_gender(poll, gender):
    count = 0
    for vote in poll.votes:
        if User.query.get(vote.user_id).gender == gender:
            count += 1
    return count
        

def vote_count_by_option_and_gender(option, gender):
    count = 0
    for vote in option.votes:
        if User.query.get(vote.user_id).gender == gender:
            count += 1
    return count

def report_poll(user_id, poll_id):
    is_owner = user_id == Poll.query.get(poll_id).user_id
    entry = UserPollReport.query.filter_by(user_id=user_id, poll_id=poll_id).first()
    if is_owner or entry:
        return
    entry = UserPollReport(user_id=user_id, poll_id=poll_id)
    db.session.add(entry)
    db.session.commit()
    
def reject_flag(poll_id):
    UserPollReport.query.filter_by(poll_id=poll_id).delete()
    db.session.commit()
    pass
