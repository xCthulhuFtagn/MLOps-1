FROM python:3.13-bullseye
# Install necessary build tools and compilers
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

ADD ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Initialize a Git repository and configure Git
RUN git init . && \
    git config --global user.email "you@example.com" && \
    git config --global user.name "Your Name"

# Set up a fake remote repository
RUN mkdir /app/fake-remote && \
    cd /app/fake-remote && \
    git init --bare

# Add the fake remote repository to the local Git repository
RUN git remote add origin /app/fake-remote

# Create an initial commit
RUN echo "# Initial commit" > README.md && \
    git add README.md && \
    git commit -m "Initial commit" && \
    git push --set-upstream origin master

EXPOSE 8000

ENTRYPOINT [ "sh","run-rest.sh" ]