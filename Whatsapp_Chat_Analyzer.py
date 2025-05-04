import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

# Add Font Awesome to your Streamlit app
st.markdown(
    """
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <i class="fab fa-whatsapp" style="font-size: 24px; color: green; margin-right: 10px;"></i>
        <h1 style="display: inline; font-size: 20px;">Whatsapp Chat Analyzer</h1>
    </div>
    """,
    unsafe_allow_html=True
)

from matplotlib.font_manager import FontProperties

# styling
st.markdown("""
            <style>
           [data-testid="stAppViewContainer"] {
    background-color: #e3f2ff; /* Change this to your desired color */
}

[data-testid="stSidebar"] {
    background-color: #d6efff; /* Optional: Sidebar color */
}
            </style>
            """, 
unsafe_allow_html=True)
            

prop = FontProperties(fname='/System/Library/Fonts/Apple Color Emoji.ttc')
plt.rcParams['font.family'] = prop.get_family()

st.markdown(
    """
    <h1 style='text-align: center; color: black; font-family: 'Montserrat', sans-serif;'>Welcome to the Whatsapp Chat Analyzer</h1>
    """,
    unsafe_allow_html=True
)

# image
if "show_image" not in st.session_state:
    st.session_state.show_image = True

# Function to hide the image
def hide_image():
    st.session_state.show_image = False

if st.session_state.show_image:
    st.image('WhatsApp.svg.webp')

uploaded_file = st.sidebar.file_uploader('Choose a file')

if uploaded_file is not None:
    file_name = uploaded_file.name
    
    if  not file_name.endswith('.txt') or not file_name.startswith('WhatsApp Chat with'):
        st.sidebar.error("Please upload a valid WhatsApp chat file (in .txt format).")
        st.stop()
    
    lst = file_name.split("WhatsApp Chat with ")
    group_name = lst[1].split(".txt")
    
    selected_tab = option_menu(
        f'Drop down analysis for "{group_name[0]}"',
        ["Top Statistics", "Timeline", 'Activity Map', 'Most busy users', 'Word distribution', 'Emoji and hate speech'],
        icons=["bar-chart-line", "clock", "map", "people-fill", "file-text", "emoji-smile"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f5f5f5"},
            "icon": {"color": "blue", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#007bff", "color": "white"},
        }
    )
    
    bytes_data = uploaded_file.getvalue()
    
    # converting this stream file to string
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)
    
    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")
    
    
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    all_data = []
    
    if st.sidebar.button("Show Analysis"):    
        hide_image()
     
        # stats area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            
        # Display the statistics in a table format
        if selected_tab == 'Top Statistics':
            st.title("Top statistics")
            st.markdown(
                f"""
                <style>
                .stat-table {{
                    width: 100%;
                    border-collapse: collapse;
                    
                }}
                .stat-table td {{
                    padding: 15px;
                    text-align: center;
                    border: 1px solid #ddd;
                    font-size: 18px;
                    background-color: black;
                    color: white;
                }}
                .stat-table th {{
                    padding: 10px;
                    text-align: center;
                    border: 1px solid #ddd;
                    background-color: black;
                    font-size: 20px;
                    color: white;
                }}
                </style>
                <table class="stat-table">
                    <tr>
                        <th>Total Messages</th>
                        <th>Total Words</th>
                        <th>Media Shared</th>
                        <th>Links Shared</th>
                    </tr>
                    <tr>
                        <td>{num_messages}</td>
                        <td>{words}</td>
                        <td>{num_media_messages}</td>
                        <td>{num_links}</td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True
            )

        
        if selected_tab == 'Timeline':
            # Monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig,ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation = 'vertical')
            monthly_timeline_bar = 'bargraph.png'
            plt.savefig(monthly_timeline_bar)
            
            all_data.append(monthly_timeline_bar)
            
            st.pyplot(fig)
            
            # daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig,ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation = 'vertical')
            daily_timeline_bar = 'bargraph2.png'
            plt.savefig(daily_timeline_bar)
            
            all_data.append(daily_timeline)
            
            st.pyplot(fig)
        
        # activity map
        if selected_tab == 'Activity Map':
            st.title("Activity map")
            col1, col2 = st.columns(2)
            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                plt.xticks(rotation='vertical')
                busy_day_bar = 'bargraph3.png'
                plt.savefig(busy_day_bar)
                
                all_data.append(busy_day_bar)
                
                st.pyplot(fig)
                
            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                busy_month_bar = 'bargraph4.png'
                plt.savefig(busy_month_bar)
                
                all_data.append(busy_month_bar)
                
                st.pyplot(fig)
            
            # activity heat map
            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            heatmap_png = 'heatmap.png'
            plt.savefig(heatmap_png)
            
            all_data.append(heatmap_png)
            
            st.pyplot(fig)
            
        # finding the busiest user in the group
        if selected_tab == 'Most busy users':
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    ax.bar(x.index, x.values, color = 'red')
                    plt.xticks(rotation = 'vertical')
                    busy_user_bar = 'busy_bar.png'
                    plt.savefig(busy_user_bar)
                    
                    all_data.append(busy_user_bar)
                    
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)
                
        # wordcloud
        if selected_tab == 'Word distribution':
            st.title("Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            wc_png = 'word.png'
            plt.savefig(wc_png)
            
            all_data.append(wc_png)
            
            st.pyplot(fig)
            
            # most common words
            most_common_df = helper.most_common_words(selected_user, df)
            
            fig, ax = plt.subplots()
            
            ax.barh(most_common_df[0], most_common_df[1])
            
            st.title("Most common words")
            common_png = 'common.png'
            plt.savefig(common_png)
            
            all_data.append(common_png)
            
            st.pyplot(fig)
        
        # emoji analysis
        if selected_tab == 'Emoji and hate speech':
            emoji_df = helper.emoji_helper(selected_user, df)
            st.title("Emoji Analysis")
            
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct='%0.2f')
                    pie_chart = 'pie.png'
                    plt.savefig(pie_chart)
                    
                    all_data.append(pie_chart)
                    
                    st.pyplot(fig)
            else:
                st.write("No emojis in the given chat")
            
            # hate speech detection
            positive_counts, negative_counts, sentiment_counts, sent_df = helper.detect_hate_speech(selected_user, df)
            
            fig, ax = plt.subplots()
            
            bar_width = 0.4
            users = sentiment_counts.index
            x = range(len(users))

            # Plot positive sentiments
            ax.bar(x, positive_counts, width=bar_width, label='Positive', color='green')

            # Plot negative sentiments (shifted for double bar effect)
            ax.bar([i + bar_width for i in x], negative_counts, width=bar_width, label='Negative', color='red')

            # Add labels, title, and legend
            ax.set_xlabel('Users')
            ax.set_ylabel('Message Counts')
            ax.set_title('Sentiment Analysis by User')
            ax.set_xticks([i + bar_width / 2 for i in x])
            ax.set_xticklabels(users)
            ax.legend()
            plt.xticks(rotation = 'vertical')
            hate_bar = 'hate.png'
            plt.savefig(hate_bar)
            
            all_data.append(hate_bar)
            st.pyplot(fig)