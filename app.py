import streamlit as st
import ollama

def generate_plan(agent_name, user_input):
    prompt = f"Create a daily schedule plan based on the user's input. {agent_name} needs to work with the other agents like (work, food, rest, workout) to create a well balanced daily plan. User input:{user_input}"
    response= ollama.chat(model="llama3.1:8b", messages =[{"role":"user","content":prompt}])
    return response.get('message', {}).get('content', 'no text found in response')


def create_daily_plan(sleep_hours, working_hours):
    available_hours = 24 - sleep_hours - working_hours

    # Generate Different Plan

    sleep_plan = generate_plan("Sleep Agent",f"User needs {sleep_hours} hours of sleep.")
    work_plan = generate_plan("Work Agent",f"User works {working_hours} hours a day.")
    food_plan = generate_plan("Food Agent",f"Plan meals with {available_hours} hours left.")
    workout_plan = generate_plan("Workout Agent",f"User can workout for {available_hours} hours.")
    rest_plan = generate_plan("Rest Agent",f"Plan relaxation time within {available_hours} hours.")

    # Combine all the plans

    daily_plan=f"""
    Your Daily Plan :
    1. {sleep_plan}
    2. {work_plan}
    3. {food_plan}
    4. {workout_plan}
    5. {rest_plan}
    """
    return daily_plan


def main():
    
    st.title("Daily Planer AI App")

    sleep_hours = st.slider("How many hours do you sleep each day?",0,24,8)
    working_hours = st.slider("How many hours do you work each day?",0,24,8)

    if st.button("Generate Daily Plan"):
        daily_plan=create_daily_plan(sleep_hours,working_hours)
        st.subheader("Your Suggested Daily Plan:")
        st.write(daily_plan)

if __name__ == "__main__":
    main()
