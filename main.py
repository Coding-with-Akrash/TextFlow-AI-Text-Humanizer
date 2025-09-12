import streamlit as st
import random
import re
import io

# Title with styling
st.title("🧠 AI Text Humanizer Pro")
st.markdown("### Transform AI-generated text into natural, human-like content")

# Sidebar for options and settings
st.sidebar.header("🎛️ Transformation Options")

# Checkboxes with emojis
use_contractions = st.sidebar.checkbox("🤝 Contractions", value=True)
use_fillers = st.sidebar.checkbox("🗣️ Fillers & Pauses", value=True)
use_colloquial = st.sidebar.checkbox("💬 Colloquial Language", value=True)
use_typos = st.sidebar.checkbox("⌨️ Typos & Imperfections", value=False)
use_emojis = st.sidebar.checkbox("😊 Emojis & Expressions", value=True)
use_sentence_variety = st.sidebar.checkbox("📝 Sentence Variety", value=True)

# Tone selection
tone = st.sidebar.selectbox("🎭 Tone Style", 
                           ["casual", "friendly", "professional", "academic", "conversational", "enthusiastic"], 
                           index=1)

# Intensity slider with description
intensity = st.sidebar.slider("🔥 Transformation Intensity", 0, 100, 70)
st.sidebar.caption(f"Intensity: {intensity}% - Higher = more dramatic changes")

# Custom replacements section
st.sidebar.header("🔧 Custom Word Replacements")
if 'custom_replacements' not in st.session_state:
    st.session_state.custom_replacements = {}

# Display current replacements
if st.session_state.custom_replacements:
    st.sidebar.write("**Current Replacements:**")
    for orig, repl in st.session_state.custom_replacements.items():
        st.sidebar.write(f"`{orig}` → `{repl}`")
        if st.sidebar.button(f"❌ Remove {orig}", key=f"rem_{orig}"):
            del st.session_state.custom_replacements[orig]
            st.rerun()

# Add new replacement
with st.sidebar:
    st.write("**Add New Replacement:**")
    col1, col2 = st.columns(2)
    with col1:
        original = st.text_input("Original word:", key="orig_input")
    with col2:
        replacement = st.text_input("Replacement:", key="repl_input")
    if st.button("➕ Add Replacement") and original and replacement:
        st.session_state.custom_replacements[original.strip().lower()] = replacement.strip()
        st.rerun()

# Enhanced transformations
CONTRACTIONS = {
    "do not": "don't", "does not": "doesn't", "did not": "didn't", "have not": "haven't",
    "cannot": "can't", "will not": "won't", "is not": "isn't", "are not": "aren't",
    "was not": "wasn't", "were not": "weren't", "has not": "hasn't", "had not": "hadn't",
    "would not": "wouldn't", "could not": "couldn't", "should not": "shouldn't",
    "I am": "I'm", "I have": "I've", "I will": "I'll", "I would": "I'd",
    "you are": "you're", "you have": "you've", "you will": "you'll", "you would": "you'd",
    "we are": "we're", "we have": "we've", "we will": "we'll", "we would": "we'd",
    "they are": "they're", "they have": "they've", "they will": "they'll", "they would": "they'd",
    "that is": "that's", "there is": "there's", "what is": "what's", "where is": "where's",
    "who is": "who's", "how is": "how's", "why is": "why's", "when is": "when's",
    "it is": "it's", "it has": "it's", "let us": "let's", "going to": "gonna",
    "want to": "wanna", "got to": "gotta", "kind of": "kinda", "sort of": "sorta"
}

FILLERS = [
    "you know", "like", "I mean", "to be honest", "actually", "basically",
    "literally", "seriously", "honestly", "well", "so", "um", "uh", "ah",
    "right", "okay", "anyway", "sort of", "kind of", "I guess", "I suppose"
]

PAUSES = [", you know,", ", like,", ", I mean,", ", actually,", ", basically,", ", well,"]

COLLOQUIAL = {
    "very": "super", "extremely": "incredibly", "quite": "pretty",
    "children": "kids", "purchase": "buy", "acquire": "get",
    "assist": "help", "aid": "help", "support": "back up",
    "important": "big deal", "crucial": "key", "essential": "must-have",
    "automobile": "car", "vehicle": "ride", "residence": "place",
    "domicile": "home", "utilize": "use", "employ": "use",
    "individual": "person", "person": "guy/gal", "commence": "start",
    "initiate": "kick off", "terminate": "end", "conclude": "wrap up",
    "sufficient": "enough", "adequate": "plenty", "inquire": "ask",
    "question": "ask about", "request": "ask for", "require": "need",
    "necessitate": "call for", "demonstrate": "show", "illustrate": "show",
    "approximately": "about", "circa": "around", "multiple": "several",
    "numerous": "a bunch of", "difficult": "tough", "challenging": "hard",
    "complicated": "tricky", "expensive": "pricey", "costly": "spendy",
    "beautiful": "gorgeous", "attractive": "good-looking", "intelligent": "smart",
    "brilliant": "sharp", "excellent": "awesome", "outstanding": "amazing"
}

EMOJIS_BY_TONE = {
    "casual": ["😊", "👍", "😎", "🤔", "😅", "👌", "🙂", "😁"],
    "friendly": ["😊", "❤️", "👍", "🙏", "😍", "🤗", "🌟", "🎉"],
    "professional": ["✅", "📊", "📈", "💼", "🎯", "⚡", "🔍", "📋"],
    "academic": ["📚", "🔬", "📖", "🎓", "✏️", "📝", "🔍", "💡"],
    "conversational": ["💬", "🗣️", "👥", "🎭", "😊", "🤝", "👋", "🙂"],
    "enthusiastic": ["🔥", "🚀", "💥", "🎊", "⭐", "😍", "🤩", "🌟"]
}

TONE_TRANSFORMATIONS = {
    "casual": {
        "hello": "hey", "hi": "hey", "thank you": "thanks", "thanks": "thx",
        "goodbye": "bye", "please": "pls", "because": "'cause", "about": "'bout",
        "going to": "gonna", "want to": "wanna", "got to": "gotta"
    },
    "friendly": {
        "hello": "hey there", "hi": "hello friend", "thank you": "thanks a bunch",
        "sorry": "my bad", "goodbye": "see ya later", "please": "if you don't mind",
        "great": "awesome", "excellent": "fantastic", "good": "wonderful"
    },
    "professional": {
        "like": "such as", "a lot": "significantly", "lots of": "numerous",
        "stuff": "materials", "thing": "element", "get": "obtain",
        "make sure": "ensure", "help": "assist", "use": "utilize"
    },
    "academic": {
        "find out": "determine", "look at": "examine", "get": "acquire",
        "make sure": "verify", "think": "postulate", "show": "demonstrate",
        "big": "substantial", "small": "minimal", "change": "modify"
    },
    "conversational": {
        "however": "but", "therefore": "so", "furthermore": "also",
        "moreover": "plus", "thus": "so", "consequently": "as a result",
        "nevertheless": "still", "although": "though"
    },
    "enthusiastic": {
        "good": "AMAZING", "great": "FANTASTIC", "excellent": "PHENOMENAL",
        "interesting": "FASCINATING", "important": "CRUCIAL", "exciting": "THRILLING",
        "beautiful": "STUNNING", "fun": "BLAST"
    }
}

def apply_contractions(text):
    """Apply contractions with high visibility"""
    for formal, casual in CONTRACTIONS.items():
        text = re.sub(r'\b' + re.escape(formal) + r'\b', casual, text, flags=re.IGNORECASE)
    return text

def insert_fillers_and_pauses(text):
    """Insert fillers and pauses for natural speech patterns"""
    sentences = text.split('. ')
    transformed_sentences = []
    
    for sentence in sentences:
        if sentence and random.random() < (0.4 * intensity / 100):
            # Add filler at beginning
            if random.random() < 0.3:
                sentence = random.choice(FILLERS).title() + ", " + sentence.lower()
            
            # Add pause in middle
            words = sentence.split()
            if len(words) > 4 and random.random() < 0.4:
                pause_pos = random.randint(2, len(words) - 2)
                words.insert(pause_pos, random.choice(PAUSES))
                sentence = ' '.join(words)
            
            # Add filler at end
            if random.random() < 0.2:
                sentence = sentence + " " + random.choice(FILLERS) + "."
        
        transformed_sentences.append(sentence)
    
    return '. '.join(transformed_sentences)

def colloquialize(text):
    """Make text more colloquial and casual"""
    all_replacements = {**COLLOQUIAL, **st.session_state.custom_replacements}
    for formal, casual in all_replacements.items():
        text = re.sub(r'\b' + re.escape(formal) + r'\b', casual, text, flags=re.IGNORECASE)
    return text

def apply_tone_specific(text, tone):
    """Apply tone-specific transformations"""
    if tone in TONE_TRANSFORMATIONS:
        for formal, casual in TONE_TRANSFORMATIONS[tone].items():
            text = re.sub(r'\b' + re.escape(formal) + r'\b', casual, text, flags=re.IGNORECASE)
    return text

def add_typos(text):
    """Add realistic typos and imperfections"""
    if intensity < 20:
        return text
    
    words = text.split()
    for i in range(len(words)):
        if random.random() < (0.08 * intensity / 100) and len(words[i]) > 3:
            word = words[i]
            # Different types of typos
            typo_type = random.choice(['swap', 'double', 'omit', 'wrong_char', 'caps'])
            
            if typo_type == 'swap' and len(word) > 3:
                pos = random.randint(0, len(word)-2)
                words[i] = word[:pos] + word[pos+1] + word[pos] + word[pos+2:]
            
            elif typo_type == 'double' and len(word) > 2:
                pos = random.randint(1, len(word)-1)
                words[i] = word[:pos] + word[pos] + word[pos:]
            
            elif typo_type == 'omit' and len(word) > 3:
                pos = random.randint(1, len(word)-2)
                words[i] = word[:pos] + word[pos+1:]
            
            elif typo_type == 'wrong_char' and len(word) > 2:
                pos = random.randint(1, len(word)-1)
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                words[i] = word[:pos] + wrong_char + word[pos+1:]
            
            elif typo_type == 'caps':
                words[i] = word.upper() if word.islower() else word.lower()
    
    return ' '.join(words)

def add_emojis(text, tone):
    """Add emojis based on tone and content"""
    if not use_emojis:
        return text
    
    emoji_chance = 0.3 * intensity / 100
    sentences = text.split('. ')
    
    for i in range(len(sentences)):
        if random.random() < emoji_chance and sentences[i].strip():
            emoji = random.choice(EMOJIS_BY_TONE.get(tone, ["😊"]))
            sentences[i] = sentences[i] + " " + emoji
    
    return '. '.join(sentences)

def vary_sentence_structure(text):
    """Add variety to sentence structure"""
    if not use_sentence_variety:
        return text
    
    sentences = text.split('. ')
    varied_sentences = []
    
    for sentence in sentences:
        if sentence.strip():
            # Sometimes start with conjunction for casual flow
            if random.random() < 0.2 and tone in ["casual", "friendly", "conversational"]:
                conjunctions = ["And", "But", "So", "Well", "Anyway", "Actually"]
                sentence = random.choice(conjunctions) + " " + sentence.lower()
            
            # Add rhetorical questions
            if random.random() < 0.15 and "?" not in sentence:
                question_words = ["Right?", "You know?", "See?", "Get it?"]
                sentence = sentence + " " + random.choice(question_words)
            
            varied_sentences.append(sentence)
    
    return '. '.join(varied_sentences)

def humanize_text(text, use_contractions, use_fillers, use_colloquial, use_typos, tone, intensity):
    """Main humanization function with visible transformations"""
    if not text.strip():
        return "", 0, 0, 0, 0, 0, 0
    
    original_text = text
    transformations = 0
    
    # Apply transformations in sequence
    if use_contractions:
        new_text = apply_contractions(text)
        if new_text != text:
            transformations += 1
        text = new_text
    
    if use_colloquial:
        new_text = colloquialize(text)
        if new_text != text:
            transformations += 1
        text = new_text
    
    text = apply_tone_specific(text, tone)
    
    if use_fillers:
        new_text = insert_fillers_and_pauses(text)
        if new_text != text:
            transformations += 1
        text = new_text
    
    if use_typos:
        new_text = add_typos(text)
        if new_text != text:
            transformations += 1
        text = new_text
    
    if use_emojis:
        new_text = add_emojis(text, tone)
        if new_text != text:
            transformations += 1
        text = new_text
    
    if use_sentence_variety:
        new_text = vary_sentence_structure(text)
        if new_text != text:
            transformations += 1
        text = new_text
    
    # Count statistics
    chars_before = len(original_text)
    chars_after = len(text)
    words_before = len(original_text.split())
    words_after = len(text.split())
    sentences_before = len(original_text.split('. '))
    sentences_after = len(text.split('. '))
    
    return text, chars_before, chars_after, words_before, words_after, sentences_before, transformations

# Main content area
st.header("📝 Input Text")
uploaded_file = st.file_uploader("Choose a text file", type=['txt'], help="Upload a .txt file or type directly below")

if uploaded_file is not None:
    input_text = io.StringIO(uploaded_file.getvalue().decode()).read()
else:
    input_text = st.text_area("Enter AI-generated text to humanize:", 
                             height=150, 
                             placeholder="Paste your formal or AI-generated text here...",
                             help="The more formal the input, the more dramatic the transformation!")

# Humanize button with styling
if st.button("🚀 Humanize Text", type="primary", use_container_width=True):
    if input_text.strip():
        with st.spinner("Transforming text... This might take a moment"):
            result, chars_before, chars_after, words_before, words_after, sentences, transformations = humanize_text(
                input_text, use_contractions, use_fillers, use_colloquial, use_typos, tone, intensity
            )
        
        st.header("🎉 Humanized Output")
        
        # Create two columns for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Original Text")
            st.text_area("", value=input_text, height=200, key="original_output", label_visibility="collapsed")
        
        with col2:
            st.subheader("✨ Humanized Text")
            st.text_area("", value=result, height=200, key="humanized_output", label_visibility="collapsed")
        
        # Statistics with emojis
        st.header("📊 Transformation Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("📝 Characters", f"{chars_before} → {chars_after}", f"{chars_after - chars_before:+d}")
        col2.metric("📋 Words", f"{words_before} → {words_after}", f"{words_after - words_before:+d}")
        col3.metric("🔤 Sentences", sentences)
        col4.metric("🔄 Transformations", transformations)
        
        # Download button
        st.download_button(
            label="📥 Download Humanized Text",
            data=result,
            file_name="humanized_text.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Show transformation highlights
        st.header("🌟 Transformation Highlights")
        st.info("""
        **Visible changes applied:**
        - 🤝 Contractions added for casual flow
        - 🗣️ Natural fillers and pauses inserted
        - 💬 Formal language made conversational
        - 🎭 Tone-specific vocabulary applied
        - 😊 Emojis added for emotional expression
        - 📝 Sentence structure varied for natural rhythm
        """)
        
    else:
        st.warning("⚠️ Please enter some text to humanize.")

# Help section with expander
with st.expander("📖 User Guide & Tips"):
    st.markdown("""
    ## 🎯 How to Get Perfect Visible Changes
    
    **1. Start with formal AI text** - The more formal the input, the more dramatic the transformation!
    
    **2. Adjust Intensity** - Higher intensity (70-100) = more visible changes
    
    **3. Combine multiple options** - Use Contractions + Fillers + Colloquial for maximum effect
    
    **4. Choose the right tone**:
    - 🎭 **Casual**: Very informal, like texting a friend
    - 😊 **Friendly**: Warm and approachable with emojis
    - 💼 **Professional**: Polished but natural business language
    - 📚 **Academic**: Scholarly but readable
    - 💬 **Conversational**: Natural speaking patterns
    - 🔥 **Enthusiastic**: Excited and energetic
    
    **5. Add custom replacements** for domain-specific terms
    
    **Example transformation**:
    - **Input**: "The utilization of this methodology will facilitate the optimization process."
    - **Output**: "So, using this method will basically help optimize things, you know? 👍"
    """)

# About section
st.sidebar.markdown("---")
st.sidebar.markdown("""
**🧠 AI Text Humanizer Pro**  
*Version 3.0*  
**© 2025 Text Humanizer by Akrash Noor**

Transform robotic AI text into natural, human-sounding content with visible, dramatic changes!
""")

# Add some styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton>button {
        background-color: #2196F3;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
