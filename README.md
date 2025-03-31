# Paulbot

Paulbot is a chatbot that answers your questions related to Paul Allen.

This guide will walk you through setting up and running this project.

## Prerequisites

- Git
- Miniconda or Anaconda

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/igorpetrovicbe/paulbot.git
```

### 2. Add Configuration File

Place the `config.py` file in the repository root folder. This file contains necessary configurations for the application to run properly.

### 3. Set Up Python Environment

#### Install Miniconda

If you don't have Miniconda installed, download and install it from [Miniconda's official website](https://docs.anaconda.com/miniconda/).

#### Create and Activate Environment

```bash
# Create a new conda environment with Python 3.13
conda create -n yourenv python=3.13

# Activate the environment
conda activate yourenv
```

### 4. Install Dependencies

To set up the required dependencies for this project, run the following commands:

```bash
# Install Semantic Router with quiet mode and upgrade option
pip install -qU semantic-router

# Install all other required packages
pip install chainlit llama-index llama-index-vector-stores-pinecone pinecone llama-index-llms-openai voyageai
```

### 5. Run the Application

Navigate to your repository directory (if not already there) and start the application:

```bash
# Navigate to the repository directory
cd path/to/repository

# Run the application with hot-reloading enabled
chainlit run main.py -w
```

## Accessing the Application

Once started, the application will be available at:
- http://localhost:8000

## Troubleshooting

If you encounter any issues:
- Ensure all dependencies are correctly installed
- Check that the `config.py` file is properly configured
- Verify that you're using Python 3.13 in your active environment