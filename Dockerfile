FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
python main.py &\n\
streamlit run app.py' > start.sh

RUN chmod +x start.sh

CMD ["/bin/bash", "start.sh"]
