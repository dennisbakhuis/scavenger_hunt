poetry run \
    streamlit run src/streamlit_app.py \
    --server.port=8501 \
    --server.enableXsrfProtection=false \
    --server.enableCORS=false & \
poetry run \
    streamlit run src/admin_streamlit_app.py \
    --server.port=8502 \
    --server.enableXsrfProtection=false \
    --server.enableCORS=false && \
wait
