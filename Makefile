setup:
	pip install -r requirements.txt

pipeline:
	python3 load_data.py
	python3 analysis.py

dashboard:
	streamlit run app.py

.PHONY: setup pipeline dashboard

