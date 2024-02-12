import streamlit as st
from firebase_admin import firestore
import json


with open('quizzes.json', 'r') as file:
    json_data = json.load(file)

# for topic_data in json_data:
#     print(topic_data)

quizzes = json_data
#List of all topics
all_topics = [quiz['topic'] for quiz in quizzes]

def app():

    st.title("Quiz Page")

    if 'db' not in st.session_state:
        st.session_state.db = ''

    db = firestore.client()
    st.session_state.db = db

    ph = ''
    if st.session_state.username =='':
        ph = 'Login to be able to take a quiz'
        st.text(ph)
    else:
        ph = 'Take a quiz'
        st.text(ph)

        # Search bar for topic selection
        selected_topic = st.selectbox("Select a Quiz Topic", all_topics)

        # Get selected quiz
        selected_quiz = next((quiz for quiz in quizzes if quiz['topic'] == selected_topic), None)

        if selected_quiz:
            st.header(f"{selected_topic} Quiz")

            # Display questions and collect user answers
            user_answers = []
            for i, question in enumerate(selected_quiz['questions']):
                st.write(f"**Question {i + 1}:** {question['question']}")
            
                # Use st.radio for single answer choice
                user_answer = st.radio(f"Select an option for Question {i + 1}", question['options'])
                user_answers.append(user_answer)

            # Submit button to calculate and display result
            if st.button("Submit"):
                # Calculate and display result
                correct_answers = [q['correct_answer'] for q in selected_quiz['questions']]
                score = sum(user_answer == correct_answer for user_answer, correct_answer in zip(user_answers, correct_answers))
                # writing the taken quiz to the database
                info = db.collection('Quizzes').document(st.session_state.username).get()
                print(selected_quiz['topic'])
                print(info.to_dict())
                if info.exists:
                    info = info.to_dict()
                    if 'taken_quizzes' in info.keys():
                        pos = db.collection('Quizzes').document(st.session_state.username)
                        taken_quizzes = info['taken_quizzes']
                        quiz_scores = info['quiz_scores']
                        taken_quizzes.append(selected_quiz['topic'])
                        quiz_scores.append(score)
                        pos.set({'taken_quizzes': taken_quizzes, 'quiz_scores': quiz_scores, 'Username': st.session_state.username})
                    # pos.update({u'taken_quizzes': firestore.ArrayUnion([u'{}'.format(selected_quiz['topic'])]), u'quiz_scores': firestore.ArrayUnion([u'{}'.format(score)])})
                    else:
                        data = {"taken_quizzes":[selected_quiz['topic']], "quiz_scores":[score], "Username": st.session_state.username}
                        db.collection('Quizzes').document(st.session_state.username).set(data)
                else:
                    data = {"taken_quizzes":[selected_quiz['topic']], "quiz_scores":[score], "Username": st.session_state.username}
                    db.collection('Quizzes').document(st.session_state.username).set(data)


                st.write(f"Your Score: {score}/{len(selected_quiz['questions'])}")

                # Display correct answers
                st.write("Correct Answers:")
                for i, (user_answer, correct_answer) in enumerate(zip(user_answers, correct_answers)):
                    st.write(f"Question {i + 1}: {correct_answer} (Your answer: {user_answer})")
        else:
            st.warning("No quiz found for the selected topic. Please choose a valid topic.")



'''
 You are a helpful assistant programmed to generate questions based on your database. For "diagnose name" diagnose, you're tasked with designing 10 distinct questions. Each of these questions will be accompanied by 4 possible answers: one correct answer and three incorrect ones. 
    For clarity and ease of processing, structure your response in a way that emulates a Python list of lists. 

    Your output should be shaped as follows:

    1. An outer list that contains 10 inner lists.
    2. Each inner list represents a dictionary of question, options and correct_answer keys, and contains exactly 3 values  in this order:
    - The generated question.
    - Options list which contains all the possible answers
    - correct answer

    Your output should mirror this structure:
    [
        {"question": "Generated Question 1", "options": [ "Option 1.1",  "Option 1.2", "Option 1.3", "Option 1.4"], "correct_answer": "Correct option"},
       {"question":"Generated Question 2", "options": [ "Option 2.1",  "Option 2.2", "Option 2.3", "Option 2.4"], "correct_answer": "Correct option"},
        ...
    ]

    It is crucial that you adhere to this format as it's optimized for further Python processing.
'''