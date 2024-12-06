FROM python
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY *.py /usr/local/app
COPY locale /usr/local/app/locale
RUN mkdir -p /usr/local/app/config
#EXPOSE 5000

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["python3", "/usr/local/app/sweet_home_controller.py"]
#CMD ["bash"]

