from django.shortcuts import render, redirect
from .forms import EventForm
from .models import Event, WikipediaChange
from django.db.models import Count
import aiohttp
import asyncio
from asgiref.sync import sync_to_async
from datetime import timedelta
import plotly.graph_objs as go
from plotly.offline import plot
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def analyze_similarity_with_bert(event_description, article_text):
    """
    Analyze the contextual similarity between an event description and a Wikipedia article using BERT.
    
    Parameters:
    event_description (str): The description of the event.
    article_text (str): The full text of the Wikipedia article.

    Returns:
    float: Cosine similarity score between the event description and the article.
    """
    # Tokenize and encode the inputs
    inputs_event = tokenizer(event_description, return_tensors='pt', truncation=True, padding=True)
    inputs_article = tokenizer(article_text, return_tensors='pt', truncation=True, padding=True)

    # Get embeddings for event description and article
    with torch.no_grad():
        event_embedding = model(**inputs_event).last_hidden_state.mean(dim=1)
        article_embedding = model(**inputs_article).last_hidden_state.mean(dim=1)

    # Calculate cosine similarity
    similarity = cosine_similarity(event_embedding.numpy(), article_embedding.numpy())
    
    return similarity[0][0]

# Fetch full Wikipedia article text (Placeholder function, replace with actual implementation)
def fetch_full_article_text(article_title):
    # Placeholder: Replace this with the actual code to fetch the full article text
    return "This is a sample text of a Wikipedia article for demonstration purposes."

# This function fetches real Wikipedia article changes using the Wikipedia API
async def fetch_article_changes(article_title, event_description, event_date):
    # Calculate the end date (3 months after the event date)
    end_date = event_date + timedelta(days=90)

    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": article_title,
        "rvlimit": "max",
        "rvprop": "timestamp|user|comment|content",
        "rvslots": "main",
        "rvstart": event_date.strftime('%Y-%m-%dT%H:%M:%SZ'),  # Start date (event date)
        "rvend": end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),      # End date (3 months after event date)
        "continue": ""
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            pages = data.get('query', {}).get('pages', {})

            changes = []
            for page_id, page_info in pages.items():
                revisions = page_info.get('revisions', [])
                for rev in revisions:
                    content = rev.get('slots', {}).get('main', {}).get('*', '')
                    if event_description.lower() in content.lower():
                        changes.append({
                            'page_title': page_info.get('title'),
                            'timestamp': rev.get('timestamp'),
                            'user': rev.get('user'),
                            'comment': rev.get('comment'),
                            'matched_content': content,
                        })
            return changes

# Synchronous view to handle event creation and fetching Wikipedia changes
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()

            # Fetch Wikipedia changes after the event is created
            articles = asyncio.run(sync_to_async(list)(event.articles.all()))
            changes_found = False

            for article in articles:
                # Fetch the full text of the Wikipedia article
                article_text = fetch_full_article_text(article.title)

                # Analyze similarity using BERT
                similarity_score = analyze_similarity_with_bert(event.event_description, article_text)

                # If similarity score is above a threshold, consider it a match
                if similarity_score > 0.8:  # Threshold can be adjusted
                    changes = asyncio.run(fetch_article_changes(article.title, event.event_description, event.event_date))
                    changes_found = True
                    for change in changes:
                        if change['matched_content']:  # Only save if matched content is found
                            asyncio.run(sync_to_async(WikipediaChange.objects.create)(
                                event=event,
                                page_title=change['page_title'],
                                timestamp=change['timestamp'],
                                user=change['user'],
                                comment=change['comment'],
                                matched_content=f"{change['matched_content']} (Similarity Score: {similarity_score:.2f})"
                            ))

            if not changes_found:
                asyncio.run(sync_to_async(WikipediaChange.objects.create)(
                    event=event,
                    page_title="No Change Found",
                    timestamp=None,
                    user="",
                    comment="No contextually similar changes found.",
                    matched_content=""
                ))

            return redirect('all_events_and_changes')  # Redirect to view all events and changes
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

# Synchronous view to display all events and their associated Wikipedia changes
def all_events_and_changes(request):
    # Fetch all events and their change status
    events = Event.objects.all()
    events_with_changes = []
    event_status = []
    change_details = []

    for event in events:
        changes = asyncio.run(sync_to_async(list)(event.changes.all()))
        events_with_changes.append({
            'event': event,
            'changes': changes
        })
        # Determine if a change was found and get the date and URL
        if changes and any(change.page_title != "No Change Found" for change in changes):
            event_status.append('green')  # Change found, bar will be green
            # Get the date and URL of the first change found
            change_date = changes[0].timestamp.strftime('%Y-%m-%d') if changes[0].timestamp else "No Date"
            change_url = f"https://en.wikipedia.org/wiki/{changes[0].page_title.replace(' ', '_')}"
            change_details.append(f"Date: {change_date}<br>URL: {change_url}")
        else:
            event_status.append('white')  # No change found, bar will be empty (white)
            change_details.append('No Change Found')

    # Prepare data for Plotly
    x_labels = [f"{item['event'].event_name} ({item['event'].event_date.strftime('%Y-%m-%d')})" for item in events_with_changes]
    colors = event_status

    # Create a bar chart
    bar_chart = go.Bar(
        x=x_labels,  # Use the concatenated event name and date as x-axis labels
        y=[1] * len(x_labels),  # Set all y values to 1 since we're just showing status
        name='Wikipedia Change Status',
        marker_color=colors,
        text=change_details,  # Add the change dates and URLs to the hover text
        hoverinfo='text+x',  # Show event name, date, and change details on hover
    )

    layout = go.Layout(
        title='Wikipedia Change Status per Event',
        xaxis=dict(title='Event and Date'),
        yaxis=dict(title='Change Found', tickvals=[0, 1], ticktext=['No Change', 'Change Found']),
        showlegend=False
    )

    fig = go.Figure(data=[bar_chart], layout=layout)
    plot_div = plot(fig, output_type='div')

    return render(request, 'events/event_changes.html', {
        'events_with_changes': events_with_changes,
        'plot_div': plot_div
    })

