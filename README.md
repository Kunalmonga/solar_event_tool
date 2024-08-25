# Event Change Tracker

This project tracks changes in Wikipedia articles related to specific events in the solar industry. The goal is to determine if an event in the solar industry triggers edits to relevant Wikipedia pages.

## Project Overview

The application allows users to create events related to developments in solar technology and fetches Wikipedia revisions for related articles within a three-month window following the event date. BERT (Bidirectional Encoder Representations from Transformers) is used to compare the content of these revisions with the event description by generating contextual embeddings and calculating cosine similarity. If a revision is deemed contextually relevant based on a similarity threshold, the change is recorded and visualized in a bar chart, where green bars indicate a match and empty bars indicate no relevant changes.

## Note on Visualization

For the data visualization component of this project, I have used Plotly, a Python-based library known for its ease of use and ability to create interactive charts and graphs. Plotly provides robust and flexible tools that allowed for the quick generation of the required visualizations, such as the bar charts used to display the contextual relevance of Wikipedia changes to the solar industry events.

## Note on Sample Response

I have attached a sample output screenshot for reference purposes in sampleoutput.png, demonstrating how the visualization looks in the application.

## Project Structure

- **`views.py`**: Handles the logic for event creation, fetching Wikipedia changes, and rendering the results.
- **`models.py`**: Defines the database models for events and Wikipedia changes.
- **`forms.py`**: Contains the forms used for event creation.
- **`templates/`**: Stores the HTML templates used to render the frontend pages.
- **`static/`**: Contains static assets such as CSS and JavaScript files.
- **`urls.py`**: Manages the URL routing for the Django application.
- **`settings.py`**: Contains the Django project's configuration settings.
- **`requirements.txt`**: Lists the Python dependencies required to run the project.

## BERT Integration for Contextual Similarity

### What is BERT?

BERT (Bidirectional Encoder Representations from Transformers) is a powerful language model developed by Google that excels at understanding the context of words in a text. BERT is used in this project to enhance the accuracy of detecting relevant changes in Wikipedia articles by comparing the content of revisions with event descriptions.

### How BERT Is Used in This Project

1. **Generating Contextual Embeddings**:

   - BERT is employed to generate embeddings (dense vector representations) for both event descriptions and Wikipedia article content. These embeddings capture the semantic meaning and context of the text.

2. **Comparing Event Descriptions with Wikipedia Articles**:

   - After generating embeddings for the event description and the Wikipedia article, the project computes the cosine similarity between these embeddings. A high similarity score indicates that the Wikipedia article content is contextually similar to the event description.

3. **Integration in Django Workflow**:
   - The function `analyze_similarity_with_bert` in `views.py` handles the BERT-based similarity analysis. This function is called during the event creation process to evaluate whether revisions in Wikipedia articles are contextually similar to the event being tracked.

### Installation Requirements for BERT

To use BERT in this project, the following Python packages must be installed:

```bash
pip install transformers torch scikit-learn
```

## Database

### Why PostgreSQL?

PostgreSQL is used as the database for this project due to its robustness, scalability, and support for complex queries. PostgreSQL's JSON support is particularly useful for handling the structured data returned by the Wikipedia API. Additionally, PostgreSQL's performance and reliability make it an excellent choice for applications that require consistent and accurate data handling.

### Database Models

1. **Event**:

   - Represents an event related to solar technology.
   - Fields: `event_date`, `event_name`, `event_description`, `tags`, `additional_info_link`.

2. **WikipediaArticle**:

   - Represents a Wikipedia article related to an event.
   - Fields: `event` (ForeignKey to Event), `title`, `url`.

3. **WikipediaChange**:
   - Records changes found in Wikipedia articles that match an event's description.
   - Fields: `event` (ForeignKey to Event), `page_title`, `timestamp`, `user`, `comment`, `matched_content`.

### Importing Sample Data

To set up the sample data for this project, follow these steps to import the provided PostgreSQL dump file (dbexport.pgsql):

1. **Create a New Database**:

```bash
createdb solar_event_db
```

2. **Import the Dump File present in root location**:

```bash
pg_restore -U your_db_user -d solar_event_db -v dbexport.pgsql
```

## Logic and Functionality

### Event Creation

When an event is created, the user inputs details such as the event name, date, description, and associated Wikipedia articles. The `create_event` view handles the creation of the event and triggers the process of fetching Wikipedia revisions.

### Fetching Data from Wikipedia

The `fetch_article_changes` function is responsible for querying Wikipedia's API to retrieve revisions for a specific article within a 3-month period following the event date. The function uses the following logic:

1. **API Request**: The function sends a request to the Wikipedia API with parameters specifying the article title, start date (event date), and end date (3 months after the event date).
2. **Revision Parsing**: The function parses the response to extract revisions, including the timestamp, user, comment, and content.
3. **Content Matching**: The function checks if any of the revisions' content matches the event description. If a match is found, the revision is recorded in the `WikipediaChange` model.

### Visualization

The results are visualized using Plotly, a powerful graphing library. A bar chart is generated to display the change status for each event:

- **Green Bars**: Indicate that a change was found for the event.
- **Empty Bars**: Indicate that no change was found.
- **Hover Information**: When hovering over a bar, users can see the date and URL of the Wikipedia change.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/solar_event_tool.git
   cd solar_event_tool
   ```

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL**:

   - Ensure PostgreSQL is installed and running on your system.
   - Create a new PostgreSQL database and update the `DATABASES` setting in `settings.py` with your database credentials.

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'solar_event_db',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:

   - Open your web browser and navigate to `http://127.0.0.1:8000`.

## Usage

1. **Create an Event**:

   - Navigate to `http://127.0.0.1:8000/create/`.
   - Fill in the event details, including the event date, name, description, and associated Wikipedia articles.
   - Submit the form to create the event and trigger the Wikipedia change detection.

2. **View Results**:
   - Navigate to `http://127.0.0.1:8000/all/` to view the results.
   - The page displays a list of events, along with a bar chart indicating whether a change was found for each event.
   - Hover over the bars to see the date and URL of the Wikipedia change.

## Rate Limiting and Best Practices

The Wikipedia API has rate limits to prevent abuse. Ensure your application respects these limits by:

- Implementing proper request handling, including exponential backoff in case of rate limit errors.
- Setting a custom `User-Agent` header in your requests that includes your application's name and a way to contact you.
