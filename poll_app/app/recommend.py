from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_recommended_polls(all_polls, voted_polls):
    all_poll_texts = [poll.title + " " + poll.description + " " + poll.creator_username + " " + poll.created_at.strftime('%B %d, %Y at %I:%M %p') for poll in all_polls]
    voted_poll_texts = [poll.title + " " + poll.description + " " + poll.creator_username + " " + poll.created_at.strftime('%B %d, %Y at %I:%M %p') for poll in voted_polls]


    vectorizer = TfidfVectorizer(stop_words='english') # Equivalent to CountVectorizer followed by TfidfTransformer. Will also remove english stopwords like 'and', 'the', 'a' etc from corpus since they are insignificant
    tfidf_matrix = vectorizer.fit_transform(all_poll_texts)

    # basically what CountVectorizer does is it computes frequency map of each word in a document
    # and then stacks those frequency maps on one another to form one count matrix
    # To use count vectorizer simply, we can do-
    '''
    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform(corpus)
    '''

    # The fit_transform function of CountVectorizer class takes in a corpus, which is a list of sentences (documents), eg. 
    ''' 
    documents = [
        "I love programming.",
        "Programming is fun and challenging.",
        "I love solving programming challenges."
    ] 
    '''
    # First the fit method acts, which computes frequency list of each word in each document of that corpus (i.e. build a vocabulary of unique words in corpus), like
    '''
    ['and' 'challenges' 'challenging' 'fun' 'i' 'is' 'love' 'programming' 'solving']
    '''
    # Then the transform method acts, which stacks those frequency maps it into a count matrix, which looks like-
    '''
    [[0 0 0 0 1 0 1 1 0]
    [1 0 1 1 0 1 0 1 0]
    [0 1 0 0 1 0 1 1 1]]
    '''

    # now on this matrix, the TfidfTransformer acts, which replaces each element in the count matrix with its Tfidf score
    # what TF-IDF means "Term Frequency - Inverse Document Frequency"
    # The basic idea about this method is that this assumes that the features which appear in more number of documents text provide us less information specific about that document.
    # For eg. consider these 3 sentences­-
    '''
    "This is a good movie"
    "This is a good movie but the actor is not smart"
    "This is not a good movie"
    '''
    # Now here, since the word "good" is present in all the 3 documents, it will be given lesser weight than the word "not", which is present only in the 3rd document.
    # Hence, the information decreases as the number of occurences increases across different types of documents.
    # The formula used for TF-IDF score is
    '''
    weight of term t in document d = TF(t,d) * IDF(t)
    where TF(t,d) = Term frequency of t = count of term t in document d / total words in document d
    and IDF(t) = Inverse document frequency of t = log (total no. of documents / number of documents in which term t appears)
    '''



    # Calculate cosine similarity between voted polls and all polls
    voted_indices = [all_polls.index(poll) for poll in voted_polls] # the index(x) method returns the index of position element x in the given list 
    voted_vectors = tfidf_matrix[voted_indices] # voted vectors will be a matrix with each row corresponding to a poll in which a given user voted, and each column represents the TF-IDF score score of each term in our vocabulary.
    similarities = cosine_similarity(voted_vectors, tfidf_matrix)
    # cosine similarity just returns how similar 2 vectors are by computing the dot product between them as A * B^T
    # the larger the dot product, means closer those two n dimensional vectors were in that n dimensional space
    # means the higher was the similarity between them
    # another thing which will affect the magnitude of cosine similarity was the TFIDF score of a term
    # The result is a 2D matrix (similarities), where each row corresponds to a voted poll, and each column corresponds to a similarity score with a poll in all_polls.



    # Recommend polls based on similarity scores
    recommended_indices = {}
    for row in similarities:
        similar_polls = row.argsort()[-5:] # argsort returns the indices of row in ascending order of similarity scores. eg. if similarity scores are [0.9, 0.2, 0.8, 0.1, 0.95], then it returns [3, 1, 2, 0, 4]
        for poll_idx in similar_polls:
            recommended_indices[poll_idx] = recommended_indices.get(poll_idx, 0) + 1

    sorted_recommended_indices = sorted(recommended_indices.items(), key=lambda item: item[1], reverse=True)
    recommended_polls = [all_polls[i] for i,j in sorted_recommended_indices if all_polls[i] not in voted_polls]
    return recommended_polls[:5] # top 5 polls recommended for this user to vote excluding his own polls
