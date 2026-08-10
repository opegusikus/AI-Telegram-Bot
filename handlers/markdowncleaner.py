#This part fixes Markdowns that DeepSeek sends in messages
#because they are not compatible with telebot.

from markdown_text_clean import clean_text

def clean_markdown_response(text):
    cleaned_text = clean_text(text)
    return cleaned_text