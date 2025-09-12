import streamlit as st
import random
import re
import nltk
from nltk.tokenize import sent_tokenize
import io

# Download NLTK data
nltk.download('punkt_tab', quiet=True)

# Title
st.title("AI Text Humanizer Pro")

# Sidebar for options and settings
st.sidebar.header("Transformation Options")

# Checkboxes
use_contractions = st.sidebar.checkbox("Contractions", value=True)
use_fillers = st.sidebar.checkbox("Fillers", value=True)
use_colloquial = st.sidebar.checkbox("Colloquial", value=True)
use_typos = st.sidebar.checkbox("Typos", value=False)

# Tone selection
tone = st.sidebar.selectbox("Tone", ["casual", "friendly", "professional", "academic", "conversational"], index=0)

# Intensity slider
intensity = st.sidebar.slider("Intensity", 0, 100, 50)

# Custom replacements section
st.sidebar.header("Custom Word Replacements")
if 'custom_replacements' not in st.session_state:
    st.session_state.custom_replacements = {}

# Display current replacements
if st.session_state.custom_replacements:
    st.sidebar.write("Current Replacements:")
    for orig, repl in st.session_state.custom_replacements.items():
        st.sidebar.write(f"{orig} → {repl}")
        if st.sidebar.button(f"Remove {orig}", key=f"rem_{orig}"):
            del st.session_state.custom_replacements[orig]
            st.rerun()

# Add new replacement
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        original = st.text_input("Original:")
    with col2:
        replacement = st.text_input("Replacement:")
    if st.button("Add Replacement") and original and replacement:
        st.session_state.custom_replacements[original.strip()] = replacement.strip()
        st.rerun()

# Removal options
st.sidebar.header("Removal Options")
remove_emojis = st.sidebar.checkbox("Remove Emojis", value=True)
unwanted_input = st.sidebar.text_area(
    "Unwanted words (comma-separated):",
    "delve, testament, tapestry, realm, beacon, navigate, moreover, furthermore",
    height=60,
    key="unwanted"
)

# Default transformations
CONTRACTIONS = {
    "do not": "don't", "does not": "doesn't", "did not": "didn't",
    "cannot": "can't", "will not": "won't", "is not": "isn't",
    "are not": "aren't", "I am": "I'm", "I have": "I've",
    "we are": "we're", "you are": "you're", "it is": "it's",
    "they are": "they're", "that is": "that's", "there is": "there's",
    "what is": "what's", "where is": "where's", "who is": "who's",
    "how is": "how's", "why is": "why's", "let us": "let's"
}

FILLERS = ["you know", "like", "I mean", "to be honest", "actually", 
           "kind of", "sort of", "well", "basically", "literally"]

COLLOQUIAL = {
    "very": "super", "extremely": "super",
    "children": "kids", "purchase": "buy",
    "help": "give a hand", "important": "kind of a big deal",
    "automobile": "car", "residence": "place",
    "utilize": "use", "individual": "person",
    "commence": "start", "terminate": "end",
    "sufficient": "enough", "inquire": "ask"
}

TONE_TRANSFORMATIONS = {
    "friendly": {
        "hello": "hey there",
        "thank you": "thanks a bunch",
        "sorry": "my bad",
        "goodbye": "see ya"
    },
    "professional": {
        "like": "such as",
        "a lot": "considerably",
        "stuff": "materials",
        "thing": "item"
    },
    "academic": {
        "find out": "determine",
        "look at": "examine",
        "get": "obtain",
        "make sure": "ensure"
    }
}

def apply_contractions(s):
    for k, v in CONTRACTIONS.items():
        s = re.sub(r'\b' + re.escape(k) + r'\b', v, s, flags=re.IGNORECASE)
    return s

def insert_fillers(sent):
    if random.random() < (0.25 * intensity / 100):
        filler = random.choice(FILLERS)
        if random.random() < 0.5:
            return f"{filler}, {sent}"
        else:
            parts = sent.rsplit(',', 1)
            if len(parts) > 1:
                return f"{parts[0]}, {filler}, {parts[1]}"
            else:
                return f"{sent}, {filler}"
    return sent

def colloquialize(sent):
    all_replacements = {**COLLOQUIAL, **st.session_state.custom_replacements}
    for k, v in all_replacements.items():
        sent = re.sub(r'\b' + re.escape(k) + r'\b', v, sent, flags=re.IGNORECASE)
    return sent

def apply_tone_specific(sent, tone):
    if tone in TONE_TRANSFORMATIONS:
        for k, v in TONE_TRANSFORMATIONS[tone].items():
            sent = re.sub(r'\b' + re.escape(k) + r'\b', v, sent, flags=re.IGNORECASE)
    return sent

def maybe_typo(word):
    if len(word) > 3 and random.random() < (0.03 * intensity / 100):
        i = random.randint(0, len(word)-2)
        l = list(word)
        l[i], l[i+1] = l[i+1], l[i]
        return ''.join(l)
    return word

def add_typos_to_sentence(sent):
    words = sent.split()
    words = [maybe_typo(w) for w in words]
    return ' '.join(words)


def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F",  # emoticons
        u"\U0001F300-\U0001F5FF",  # symbols & pictographs
        u"\U0001F680-\U0001F6FF",  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF",  # flags (iOS)
        u"\U00002702-\U000027B0",
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def humanize_text(text, use_contractions, use_fillers, use_colloquial, use_typos, tone, intensity, remove_emojis=False, unwanted_words=""):
    if not text.strip():
        return "", 0, 0, 0, 0, 0, 0
    
    stats = {
        'chars_before': len(text),
        'words_before': len(text.split()),
        'sentences': 0,
        'transformations': 0
    }
    
    text = text.strip()
    
    if remove_emojis:
        text = remove_emojis(text)
        stats['transformations'] += 1
    
    if unwanted_words:
        words_to_remove = [w.strip().lower() for w in unwanted_words.split(',') if w.strip()]
        removed_count = 0
        for word in words_to_remove:
            pattern = r'\b' + re.escape(word) + r'\b'
            old_len = len(text)
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            if len(text) < old_len:
                removed_count += 1
        if removed_count > 0:
            text = re.sub(r'\s+', ' ', text).strip()
            stats['transformations'] += 1
    
    sents = sent_tokenize(text)
    stats['sentences'] = len(sents)
    new_sents = []
    
    for s in sents:
        s = s.strip()
        
        if use_contractions:
            s = apply_contractions(s)
            stats['transformations'] += 1
        
        if use_colloquial:
            s = colloquialize(s)
            stats['transformations'] += 1
        
        s = apply_tone_specific(s, tone)
        
        if use_fillers:
            s = insert_fillers(s)
            stats['transformations'] += 1
        
        if tone == "friendly" and random.random() < 0.5 and not remove_emojis:
            s = s + " 🙂"
        elif tone == "professional":
            s = s.replace("like", "such as")
        
        if use_typos:
            s = add_typos_to_sentence(s)
            stats['transformations'] += 1
        
        new_sents.append(s)
    
    # Join short sentences occasionally
    out = []
    i = 0
    while i < len(new_sents):
        if i+1 < len(new_sents) and random.random() < 0.2:
            out.append(new_sents[i].rstrip('.') + ', ' + new_sents[i+1].lower())
            i += 2
        else:
            out.append(new_sents[i])
            i += 1
    
    result = ' '.join(out)
    stats['chars_after'] = len(result)
    stats['words_after'] = len(result.split())
    
    return result, stats['chars_before'], stats['chars_after'], stats['words_before'], stats['words_after'], stats['sentences'], stats['transformations']

# File upload
uploaded_file = st.file_uploader("Choose a text file", type=['txt'])

if uploaded_file is not None:
    input_text = io.StringIO(uploaded_file.getvalue().decode()).read()
else:
    input_text = st.text_area("Enter text to humanize:", height=200, key="input")

if st.button("Humanize Text"):
    if input_text.strip():
        result, chars_before, chars_after, words_before, words_after, sentences, transformations = humanize_text(
            input_text, use_contractions, use_fillers, use_colloquial, use_typos, tone, intensity, remove_emojis, unwanted_input
        )
        
        st.text_area("Humanized Text:", value=result, height=200, key="output")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Characters", f"{chars_before} → {chars_after}")
        col2.metric("Words", f"{words_before} → {words_after}")
        col3.metric("Sentences", sentences)
        col4.metric("Transformations", transformations)
        
        # Download button
        st.download_button(
            label="Download Humanized Text",
            data=result,
            file_name="humanized_text.txt",
            mime="text/plain"
        )
    else:
        st.warning("Please enter some text to humanize.")

# Help section
with st.expander("User Guide"):
    st.markdown("""
    1. Paste your AI-generated text into the input area or upload a file.
    2. Select transformation options in the sidebar.
    3. Choose a tone and adjust intensity.
    4. Add custom word replacements if needed.
    5. Click "Humanize Text" to transform.
    6. Download the result.
    
    Advanced: Custom replacements persist during the session.
    """)

# About
st.sidebar.markdown("---")
st.sidebar.markdown("**AI Text Humanizer Pro**  \nVersion 2.0  \n© 2023 Text Humanizer Team")
