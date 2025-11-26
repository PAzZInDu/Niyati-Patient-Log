import streamlit as st


# Custom CSS for the news cards
st.markdown("""
<style>
    .news-container {
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        gap: 20px;
        padding: 20px 0;
        scrollbar-width: thin;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
    }
    .news-card {
        flex: 0 0 auto;
        width: 300px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        cursor: pointer;
        display: inline-block;
        vertical-align: top;
    }
    .news-card:hover {
        transform: translateY(-5px);
    }
    .news-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .news-content {
        padding: 15px;
    }
    .news-title {
        font-weight: bold;
        margin-bottom: 8px;
    }
    .news-desc {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


# Sample news data 
news_data = [
    {
        "title": "Concussion in Football",
        "description": "When it comes to concussion, don’t take chances",
        "image_url": "https://cdn.englandfootball.com/-/media/EnglandFootball/Hero/Desktop/learn/Brain-Health/20220812-concussion---hero.jpg?h=700&iar=0&w=1440&rev=3fa6bdd9610a4629ad063507804a1aa4&hash=25E5CEC7EB01A128C018492822EFE1DF",
        "link": "https://www.englandfootball.com/concussion"
    },
    {
        "title": "Football Concussions",
        "description": "Prevention, Diagnosis, and Recovery",
        "image_url": "https://www.cognitivefxusa.com/hubfs/football-concussion-prevention-and-recovery.jpg",
        "link": "https://www.cognitivefxusa.com/blog/football-concussion-prevention-and-recovery"
    }
]



def main():
    # Page header
    st.title("🌐 Community Page 🌟")
    
    # Community Info section
    st.header("Community Info")
    st.info("""
      
    Stay updated with the latest **news**, **events**, and **announcements**. Scroll through the news cards below and click on any that **catch your eye** 👀 to learn more.
    """)

    st.toast("Welcome to **our vibrant community!** ", icon="🎉", duration = 5)

    # News cards section
    st.subheader("Latest News & Updates")
    
    # Create a horizontal scrollable container for news cards
    news_cards_html = "<div class='news-container'>"
    
    for news in news_data:
        # Create HTML for each news card
        news_cards_html += f"""
<a href="{news['link']}" style="text-decoration: none; color: inherit;">
    <div class="news-card">
        <img src="{news['image_url']}" class="news-image" alt="{news['title']}">
        <div class="news-content">
            <div class="news-title">{news['title']}</div>
            <div class="news-desc">{news['description']}</div>
        </div>
    </div>
</a>
        """
    
    news_cards_html += "</div>"
    st.markdown(news_cards_html, unsafe_allow_html=True)
    
    # Add some spacing at the bottom
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.divider()

    # FAQ's
    st.title("FAQs")

    # FAQ 1
    with st.expander("1. How does the app detect whether I have a concussion?"):
        st.markdown("""
    ### 🧠 How the Detection Works
    The app uses an **LLM** trained on medical and sports-related data such as:

    - **Symptoms you report**
    - **Injury**


    After you upload the required inputs, the model analyzes the patterns and predicts whether the signs indicate a:

    - ✅ **Possible concussion**, or  
    - ❌ **No concussion detected**

    > ⚠️ **Important:** This app is meant to assist coaches, parents, and trainers with quick assessments.  
    > It does **not** replace professional medical diagnosis.
    """
                    )

    
    # FAQ 2
    with st.expander("2. What should I do if the app predicts a concussion?"):
        st.markdown("""
    ### 🚨 If the App Predicts a Concussion
    If the result indicates a **Concussion**, you should:

    1. **Immediately stop all physical activity**  
    2. **Do not continue playing, training, or practicing**
    3. **Seek medical attention** from a doctor or certified athletic trainer

    > 🛑 Ignoring concussion symptoms can worsen the injury.

    This app provides **quick screening only** — it cannot:
    - Measure severity  
    - Identify internal injuries  
    - Provide treatment  
    """
                    )


if __name__ == "__main__":
    main()
