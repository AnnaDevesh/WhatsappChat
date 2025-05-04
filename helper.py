from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji
from io import BytesIO
from fpdf import FPDF
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
extract = URLExtract()
def fetch_stats(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # fetching number of messages
    num_messages = df.shape[0]
    
    # fetch number of words
    words = []
    for message in df['message']:
        lst = message.split()
        words.extend(lst)
        
    # fetch no of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    
    # fetch no of links shared
    links = []
    for message in df['message']:
        urls = extract.find_urls(message)
        links.extend(urls)
    
    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100, 2).reset_index().rename(columns = {'user':'name', 'count':'percent'})
    return x, df

def create_wordcloud(selected_user, df):
        
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    
    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='black')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep = " "))
    return df_wc

def most_common_words(selected_user, df):
    
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))
    
    timeline['time'] = time
    
    return timeline

def daily_timeline(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    
    return daily_timeline

def week_activity_map(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        
    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


# hate speech
def analyze_sentiment(message):
    sentiment_score = analyzer.polarity_scores(message)
    if sentiment_score['compound'] >= 0.05:
        return 'Positive'
    elif sentiment_score['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'
    
def detect_hate_speech(selected_user, df):
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    df['sentiment'] = df['message'].apply(analyze_sentiment)
    
    sentiment_counts = df[df['sentiment'] != 'Neutral'].groupby(['user', 'sentiment']).size().unstack(fill_value=0)
    positive_counts = sentiment_counts.get('Positive', pd.Series(0, index=sentiment_counts.index))
    negative_counts = sentiment_counts.get('Negative', pd.Series(0, index=sentiment_counts.index))
    
    return positive_counts, negative_counts, sentiment_counts, df








































# Function to create a PDF from image paths
def create_pdf(image_paths):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add each image to the PDF
    for image_path in image_paths:
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, 'hi', ln=True, align="C")
        pdf.image(image_path, x=10, y=20, w=190)

    # Output PDF as a string and write to BytesIO
    pdf_buffer = BytesIO()
    pdf_data = pdf.output(dest='S').encode('latin1')  # Get the PDF as a string
    pdf_buffer.write(pdf_data)
    pdf_buffer.seek(0)  # Reset the buffer position for reading
    return pdf_buffer