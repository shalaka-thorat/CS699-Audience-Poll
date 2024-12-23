from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd
from app import poll_service as ps

import matplotlib
matplotlib.use('Agg')

def create_poll_vote_dist_plot(options):
    data = []
    for option in options:
        row = {'Option':option.text, 'Votes':ps.get_vote_counts_for_poll(option_id=option.id)}
        data.append(row)
    df = pd.DataFrame(data)
    plt.bar(df['Option'], df['Votes'], label=df['Option'], width=0.5, color='#5CD1D5')
    plt.xlabel("Options")
    plt.ylabel("Votes")
    plt.title("Option Vote Distribution")
    buff = BytesIO()
    plt.savefig(buff, format="png")
    plt.close()
    plot_img = base64.b64encode(buff.getvalue()).decode()
    return plot_img

def create_stacked_vote_dist_plot_by_gender(options):
    genders = ps.get_all_unique_genders()
    data = {'Option': []}
    for gender in genders:
        data[gender] = [] 

    for option in options:
        data['Option'].append(option.text)
        for gender in genders:
            votes = ps.vote_count_by_option_and_gender(option=option, gender=gender)
            data[gender].append(votes)
            
    df = pd.DataFrame(data)
    options = df['Option']
    genders = df.columns[1:]

    cumulative = pd.DataFrame(0, index=df.index, columns=genders)
    for i, gender in enumerate(genders):
        if i > 0:
            cumulative[gender] = cumulative[genders[i-1]] + df[genders[i-1]]

    gcolors = {'male':'#9BE5FF', 'female':'#FFD1DC', 'other':'#77DD77'}
    for gender in genders:
        plt.bar(options, df[gender], label=gender, bottom=cumulative[gender], width=0.5, color=gcolors[gender])

    plt.xlabel('Options')
    plt.ylabel('Votes')
    plt.title('Votes by Gender per Option')
    plt.legend(loc='upper right')
    buff = BytesIO()
    plt.savefig(buff, format="png")
    plt.close()
    plot_img = base64.b64encode(buff.getvalue()).decode()
    return plot_img

def all_gender_option_distribution_plots(poll):
    plots = []
    for gender in ps.get_all_unique_genders():
        plots.append(create_option_distribution_for_gender(poll=poll, gender=gender))
    return plots

def create_option_distribution_for_gender(poll, gender):
    data = []
    for option in poll.options:
        votes = ps.vote_count_by_option_and_gender(option=option, gender=gender)
        row = {'Option': option.text, 'Votes':votes}
        data.append(row)
    df = pd.DataFrame(data)
    plt.bar(df['Option'], df['Votes'], label=df['Option'], width=0.5, color=['#9EEFE1', '#A2FFCE', '#A2FFA8'])
    plt.xlabel("Options")
    plt.ylabel("Votes")
    plt.title(f"Votes per Option by Gender: {gender}")
    buff = BytesIO()
    plt.savefig(buff, format="png")
    plt.close()
    plot_img = base64.b64encode(buff.getvalue()).decode()
    return plot_img

def create_votes_gender_distribution_for_poll(poll):
    data = []
    for gender in ps.get_all_unique_genders():
        votes = ps.vote_count_by_poll_and_gender(poll=poll, gender=gender)
        row = {'Gender':gender, 'Votes':votes}
        data.append(row)
    df = pd.DataFrame(data)
    plt.bar(df['Gender'], df['Votes'], label=df['Gender'], width=0.5, color=['#C291DB', '#C2ADFC', '#FFABFA'])
    plt.xlabel("Gender")
    plt.ylabel("Votes")
    plt.title("Votes by Gender")
    buff = BytesIO()
    plt.savefig(buff, format="png")
    plt.close()
    plot_img = base64.b64encode(buff.getvalue()).decode()
    return plot_img