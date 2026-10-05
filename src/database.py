from models import Session, Prompt, Feedback


sessions = []
prompts = []
feedbacks = []


# =====================
# SESSION
# =====================


def create_session(session):

    sessions.append(session)

    return session



def get_sessions():

    return sessions



def delete_session(uid):

    global sessions

    sessions = [
        session
        for session in sessions
        if session.uid != uid
    ]



def update_session(uid, locale):

    for session in sessions:

        if session.uid == uid:

            session.locale = locale

            return session

    return None



# =====================
# PROMPT
# =====================


def create_prompt(prompt):

    prompts.append(prompt)

    return prompt



def get_prompts():

    return prompts



def delete_prompt(uid):

    global prompts

    prompts = [
        prompt
        for prompt in prompts
        if prompt.uid != uid
    ]



def update_prompt(uid, parameter):

    for prompt in prompts:

        if prompt.uid == uid:

            prompt.parameter = parameter

            return prompt

    return None



# =====================
# FEEDBACK
# =====================


def create_feedback(feedback):

    feedbacks.append(feedback)

    return feedback



def get_feedbacks():

    return feedbacks



def delete_feedback(uid):

    global feedbacks

    feedbacks = [
        feedback
        for feedback in feedbacks
        if feedback.uid != uid
    ]



def update_feedback(uid, status):

    for feedback in feedbacks:

        if feedback.uid == uid:

            feedback.status = status

            return feedback

    return None



def get_recent_feedbacks():

    result = []


    for session in sessions:

        for prompt in prompts:

            if prompt.session == session.uid:


                for feedback in feedbacks:


                    if feedback.prompt == prompt.uid:


                        result.append(
                            (
                                feedback.error,
                                prompt.parameter,
                                session.locale
                            )
                        )


    return result