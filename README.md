Real State Chatbot Assistant

Project Overview
This project is a demonstration of a Generative AI-powered chatbot designed to act as an intelligent assistant for a business. The bot's primary function is to handle customer inquiries, specifically by answering frequently asked questions (FAQs), providing detailed information on available properties, and facilitating booking requests.

This application showcases a practical and responsible approach to integrating Large Language Models (LLMs) by combining their natural language understanding with a structured, reliable data source. The use of the Groq API highlights a focus on low-latency and high-speed inference in the application.

Key Features
Intelligent FAQ Handling: The chatbot can answer a wide range of general inquiries about the company, services, and policies using a pre-defined knowledge base, ensuring accurate and consistent responses.

Robust Data Retrieval with Fuzzy Matching (RAG): The bot efficiently retrieves and presents specific property information from a structured CSV file. A core technical feature is the fuzzy-matching algorithm, which intelligently handles misspellings and variations in user input (e.g., "Pincrest" vs. "Pinecrest"). This makes the system more robust and user-friendly, demonstrating a key principle of Retrieval-Augmented Generation (RAG) in a practical way.

User-Friendly UI: The web interface, built with Streamlit, provides an intuitive experience for both viewing property information and submitting booking requests. The addition of a property selection dropdown further enhances usability and minimizes input errors.

Booking Automation: The bot can collect a user's name, phone number, and preferred property to generate a new booking record, which is securely saved to a separate CSV file. This demonstrates an understanding of managing and persisting user-generated data.

Modular and Clean Code: The project is structured with a clear separation of concerns, with core logic and helper functions organized into separate files for improved readability and maintainability.

Technology Stack
Python 3.11+: The core programming language.

Streamlit: For creating the interactive web-based user interface.

Groq API: Used for natural language processing and generating conversational, polished responses with a focus on low latency.

Pandas: For efficient data manipulation and retrieval from CSV files.

fuzzywuzzy: A library specifically used for the fuzzy-matching feature, demonstrating attention to practical implementation details.

Getting Started
Follow these steps to set up and run the application.

Prerequisites
Python 3.11 or higher installed.

Installation
Clone the Repository:

git clone https://github.com/AdeebaBakhtiyar/RealState_chatbot
cd your-repo-name

Create a Virtual Environment:

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate      # On Windows

Install Dependencies:

pip install -r requirements.txt

Configuration
Obtain a Groq API Key: You'll need to get an API key from the GroqCloud website.

Set Your API Key: Create a new file named .env in the project's root directory and add your API key to it.

GROQ_API_KEY="YOUR_API_KEY_HERE"

Running the Application
Once everything is configured, you can launch the app.

streamlit run app.py

The application will open in your default web browser, and you can begin interacting with the chatbot.

File Structure
The project has the following file and folder structure:

.
├── .env                  # Your API key
├── app.py                # Main application logic
├── requirements.txt      # Project dependencies
├── bookings.csv          # Automatically generated booking records
├── properties.csv        # The structured property data source
├── README.md             # This file
└── helpers.py            # Helper functions for data processing and fuzzy matching

Future Improvements
Database Integration: Migrate the properties.csv and bookings.csv data to a more scalable solution like SQLite or Firestore for better performance and data integrity.

Advanced RAG: Implement a more advanced RAG pipeline to handle unstructured data, such as PDFs or web pages, for a broader knowledge base.

Interactive Booking UI: Enhance the booking feature to use an interactive form instead of a conversational flow for a more robust user experience.

Improved Error Handling: Add more comprehensive try...except blocks to handle unexpected API responses or user inputs gracefully.