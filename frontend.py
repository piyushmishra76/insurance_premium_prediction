import os
import streamlit as st
import requests
import time
API_BASE_URL = os.getenv(
    "API_URL",
    "https://insurance-premium-api-7ks7.onrender.com"
).rstrip("/")

API_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

def wake_backend():
    """
    This function checks if the backend API is ready to accept requests. It performs a health check and manages the state of the API readiness in the Streamlit session state.
    It avoids repeated checks if the API was recently confirmed to be ready, and it handles connection
    I have created this function with the help of ChatGPT. Because the backend is hosted on Render, it may take some time to wake up if it has been idle. This function ensures that the user is informed about the status of the backend and avoids unnecessary repeated checks."""
    now = time.time()

    last_check = st.session_state.get(
        "_api_last_checked", 0
    )
    was_ready = st.session_state.get(
        "_api_ready", False
    )

    # Reuse a recent successful health check
    if was_ready and now - last_check < 60:
        return True

    # Avoid repeatedly retrying immediately after failure
    if last_check and now - last_check < 15:
        st.warning(
            "The prediction API is still starting. "
            "Please refresh this page in a few seconds."
        )
        return False

    ready = False

    with st.spinner(
        "Connecting to the prediction API. "
        "The first visit may take about a minute..."
    ):
        for attempt in range(8):
            try:
                response = requests.get(
                    HEALTH_URL,
                    timeout=10
                )

                if response.ok:
                    data = response.json()

                    if (
                        isinstance(data, dict)
                        and data.get("status") == "Ok"
                        and data.get("model_loaded") is True
                    ):
                        ready = True
                        break

            except (requests.RequestException, ValueError):
                pass

            if attempt < 7:
                time.sleep(5)

    st.session_state["_api_last_checked"] = time.time()
    st.session_state["_api_ready"] = ready

    if ready:
        st.caption("Prediction API is ready.")
    else:
        st.warning(
            "The backend is not ready yet. "
            "Please refresh the page and try again."
        )

    return ready


st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")
api_ready = wake_backend()#check if the backend is ready to accept requests
# Input fields
age = st.number_input("Age", min_value=1, max_value=119, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Are you a smoker?", options=[True, False])
city = st.text_input("City", value="Mumbai")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
)

if st.button(
    "Predict Premium Category",
    disabled=not api_ready
):
    
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(
            API_URL,
            json=input_data,
            timeout=30
        )

        result = response.json()

        if response.ok:
            st.success(
                "Predicted Insurance Premium Category: "
                f"**{result['predicted_category']}**"
            )

            st.write("🔍 Confidence:", result["confidence"])
            st.write("📊 Class Probabilities:")
            st.json(result["probabilities"])

        else:
            st.error(f"API Error: {response.status_code}")
            st.json(result)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Check its URL and status.")

    except requests.exceptions.Timeout:
        st.error("The API request timed out. Please try again.")

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
