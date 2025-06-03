

"""
Disaster Response Dashboard - Main Application
Refactored version with modular architecture
"""

# Utilities
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import altair as alt

# Import utility modules
from Utils.external_clients import initialize_external_connections
from Utils.kafka_consumers import initialize_kafka_system
from Utils.update_stream import update_all_data_batch
from Utils.ui_components import (
    render_satellite_tab,
    render_iot_tab, 
    render_social_tab,
    render_sidebar_status
)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'social_messages' not in st.session_state:
        st.session_state.social_messages = []
    if 'iot_data' not in st.session_state:
        st.session_state.iot_data = []
    if 'sat_data' not in st.session_state:
        st.session_state.sat_data = []
    if 'consumer_started' not in st.session_state:
        st.session_state.consumer_started = False
    if 'queues' not in st.session_state:
        st.session_state.queues = None
    if 'external_clients' not in st.session_state:
        st.session_state.external_clients = None


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="DRCS Disaster Response Coordination System",
        layout="wide"
    )
    
    # Dashboard Theme
    alt.theme.enable("dark")
    
    #######################
    # CSS styling
    st.markdown("""
    <style>

    [data-testid="block-container"] {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 0rem;
        margin-bottom: -7rem;
    }

    [data-testid="stVerticalBlock"] {
        padding-left: 0rem;
        padding-right: 0rem;
    }

    [data-testid="stMetric"] {
        background-color: #393939;
        text-align: center;
        padding: 15px 0;
    }

    [data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
    align-items: center;
    }

    [data-testid="stMetricDeltaIcon-Up"] {
        position: relative;
        left: 38%;
        -webkit-transform: translateX(-50%);
        -ms-transform: translateX(-50%);
        transform: translateX(-50%);
    }

    [data-testid="stMetricDeltaIcon-Down"] {
        position: relative;
        left: 38%;
        -webkit-transform: translateX(-50%);
        -ms-transform: translateX(-50%);
        transform: translateX(-50%);
    }

    </style>
    """, unsafe_allow_html=True)
    #######################


def setup_external_connections():
    """Initialize connections to external services (MinIO, Redis)"""
    if not st.session_state.external_clients:
        try:
            clients = initialize_external_connections()
            st.session_state.external_clients = clients
        except Exception as e:
            st.error(f"Failed to initialize external connections: {e}")
            st.stop()


def setup_kafka_system():
    """Initialize Kafka consumers and processing queues"""
    if st.session_state.queues is None:
        try:
            queues = initialize_kafka_system()
            st.session_state.queues = queues
            st.session_state.consumer_started = True
        except Exception as e:
            st.error(f"Failed to initialize Kafka system: {e}")
            st.stop()


def update_data_streams():
    """Update data from all Kafka streams"""
    if st.session_state.queues:
        social_queue, iot_queue, sat_queue = st.session_state.queues
        return update_all_data_batch(social_queue, iot_queue, sat_queue, st.session_state)
    return 0, 0, 0


def render_main_header():
    """Render the main dashboard header"""
    st.title(f"Disaster Response Dashboard")


def render_main_tabs():
    """Render the main dashboard tabs"""
    tab1, tab2, tab3 = st.tabs([
        "🛰️ Satellite Environmental Data",
        "🔧 IoT Environmental Sensors", 
        "📱 Social Media Alerts"
    ])
    
    with tab1:
        if st.session_state.sat_data:
            render_satellite_tab(
                st.session_state.sat_data[-1],
                st.session_state.external_clients.get_minio().get_client(),
                img_bucket="satellite-imgs"
            )
        else:
            st.info("🔄 Waiting for satellite data...")
            st.write("The system is ready to receive and display real-time satellite environmental data.")
    
    with tab2:
        if st.session_state.iot_data:
            render_iot_tab(
                st.session_state.iot_data[-1], 
                st.session_state.external_clients.get_redis().get_client()
            )
        else:
            st.info("🔄 Waiting for IoT data...")
            st.write("The system is ready to receive and display real-time IoT environmental data.")
    
    with tab3:
        if st.session_state.social_messages:
            render_social_tab(
                st.session_state.social_messages
            )
        else:
            st.info("Waiting for social media messages...")


def render_sidebar(processing_stats):
    """Render sidebar with system status"""
    social_count, iot_count, sat_count = processing_stats
    render_sidebar_status(
        st.session_state.social_messages,
        st.session_state.iot_data,
        st.session_state.sat_data,
        social_count, 
        iot_count, 
        sat_count
    )


def main():
    """Main application function"""
    # Setup
    setup_page_config()
    initialize_session_state()
    setup_external_connections()
    setup_kafka_system()
    
    # Update data streams
    processing_stats = update_data_streams()
    
    # Render UI
    render_main_header()
    render_main_tabs()
    render_sidebar(processing_stats)
    
    # Auto-refresh
    st_autorefresh(
        interval=15000, 
        limit=None, 
        key="global-autorefresh"
    )


if __name__ == "__main__":
    main()

