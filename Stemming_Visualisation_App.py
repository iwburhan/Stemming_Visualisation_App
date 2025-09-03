import streamlit as st
from nltk.tokenize import word_tokenize
import nltk
import re

nltk.download('punkt')

st.set_page_config(page_title="Porter Stemmer - All Rules", layout="centered")
st.title("Porter Stemmer")
st.subheader("Visualize Step-by-Step Stemming Rules")
st.markdown("""
Enter word or text and see **every rule check and transformation** applied by the Porter Stemmer.
Even rules that do not change the word are shown, with clear action descriptions.
""")

# ---------------------
# Helper functions
# ---------------------
def measure(word):
    vc_sequence = re.sub(r'[^aeiou]+', 'C', word)
    vc_sequence = re.sub(r'[aeiouy]+', 'V', vc_sequence)
    return vc_sequence.count('VC')

def contains_vowel(word):
    return bool(re.search(r'[aeiou]', word))

def ends_with_double_consonant(word):
    return len(word) >= 2 and word[-1] == word[-2] and word[-1] not in 'aeiou'

def ends_cvc(word):
    if len(word) < 3:
        return False
    c, v, c2 = word[-3], word[-2], word[-1]
    return c not in 'aeiou' and v in 'aeiou' and c2 not in 'aeiouwxy'

# ---------------------
# Step functions (all rules with action description)
# ---------------------
def step1a(word):
    rules = []
    if word.endswith('sses'):
        new_word = word[:-2]
        rules.append(("Step1a: 'sses' → 'ss'", new_word))
    elif word.endswith('ies'):
        new_word = word[:-2]
        rules.append(("Step1a: 'ies' → 'i'", new_word))
    elif word.endswith('ss'):
        new_word = word
        rules.append(("Step1a: 'ss' → 'ss' (no change)", new_word))
    elif word.endswith('s'):
        new_word = word[:-1]
        rules.append(("Step1a: removed 's'", new_word))
    else:
        new_word = word
        rules.append(("Step1a: no rule applied", new_word))
    return new_word, rules

def step1b(word):
    rules = []
    new_word = word
    if word.endswith('eed'):
        stem = word[:-3]
        if measure(stem) > 0:
            new_word = stem + 'ee'
            rules.append(("Step1b: changed 'eed' → 'ee'", new_word))
        else:
            rules.append(("Step1b: 'eed' but m=0, no change", new_word))
    elif word.endswith('ed'):
        stem = word[:-2]
        if contains_vowel(stem):
            new_word = stem
            rules.append(("Step1b: removed 'ed'", new_word))
        else:
            rules.append(("Step1b: 'ed' but no vowel in stem, no change", new_word))
    elif word.endswith('ing'):
        stem = word[:-3]
        if contains_vowel(stem):
            new_word = stem
            rules.append(("Step1b: removed 'ing'", new_word))
        else:
            rules.append(("Step1b: 'ing' but no vowel in stem, no change", new_word))
    else:
        rules.append(("Step1b: no rule applied", new_word))
    return new_word, rules

def step1b_helper(word):
    rules = []
    new_word = word
    if word.endswith(('at','bl','iz')):
        new_word += 'e'
        rules.append(("Step1b helper: added 'e' for 'at','bl','iz'", new_word))
    elif ends_with_double_consonant(word) and not word.endswith(('l','s','z')):
        new_word = word[:-1]
        rules.append(("Step1b helper: removed last consonant because double", new_word))
    else:
        rules.append(("Step1b helper: no rule applied", new_word))
    return new_word, rules

def step1c(word):
    rules = []
    new_word = word
    if word.endswith('y'):
        stem = word[:-1]
        if contains_vowel(stem):
            new_word = stem + 'i'
            rules.append(("Step1c: changed 'y' → 'i'", new_word))
        else:
            rules.append(("Step1c: 'y' but stem has no vowel, no change", new_word))
    else:
        rules.append(("Step1c: no rule applied", new_word))
    return new_word, rules

def step2(word):
    rules = []
    new_word = word
    suffixes = {
        "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
        "izer": "ize", "abli": "able", "alli": "al", "entli": "ent",
        "eli": "e", "ousli": "ous", "ization": "ize", "ation": "ate",
        "ator": "ate", "alism": "al", "iveness": "ive", "fulness": "ful",
        "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble"
    }
    applied = False
    for suf, rep in suffixes.items():
        if word.endswith(suf):
            stem = word[:-len(suf)]
            if measure(stem) > 0:
                new_word = stem + rep
                rules.append((f"Step2: '{suf}' → '{rep}'", new_word))
            else:
                rules.append((f"Step2: '{suf}' but m<=0, no change", new_word))
            applied = True
            break
    if not applied:
        rules.append(("Step2: no rule applied", new_word))
    return new_word, rules

def step3(word):
    rules = []
    new_word = word
    suffixes = {"icate": "ic", "ative": "", "alize": "al", "iciti": "ic",
                "ical": "ic", "ful": "", "ness": ""}
    applied = False
    for suf, rep in suffixes.items():
        if word.endswith(suf):
            stem = word[:-len(suf)]
            if measure(stem) > 0:
                new_word = stem + rep
                action = "removed" if rep == "" else f"replaced with '{rep}'"
                rules.append((f"Step3: '{suf}' → {rep if rep else ''} ({action})", new_word))
            else:
                rules.append((f"Step3: '{suf}' but m<=0, no change", new_word))
            applied = True
            break
    if not applied:
        rules.append(("Step3: no rule applied", new_word))
    return new_word, rules

def step4(word):
    rules = []
    new_word = word
    suffixes = ["al","ance","ence","er","ic","able","ible","ant","ement","ment","ent",
                "ion","ou","ism","ate","iti","ous","ive","ize"]
    applied = False
    for suf in suffixes:
        if word.endswith(suf):
            stem = word[:-len(suf)]
            if measure(stem) > 1:
                if suf == "ion" and stem.endswith(('s','t')):
                    new_word = stem
                    rules.append((f"Step4: removed 'ion'", new_word))
                elif suf != "ion":
                    new_word = stem
                    rules.append((f"Step4: removed '{suf}'", new_word))
            else:
                rules.append((f"Step4: '{suf}' but m<=1, no change", new_word))
            applied = True
            break
    if not applied:
        rules.append(("Step4: no rule applied", new_word))
    return new_word, rules

def step5a(word):
    rules = []
    new_word = word
    if word.endswith('e'):
        stem = word[:-1]
        m = measure(stem)
        if m > 1 or (m == 1 and not ends_cvc(stem)):
            new_word = stem
            rules.append(("Step5a: removed 'e'", new_word))
        else:
            rules.append(("Step5a: 'e' but not removed", new_word))
    else:
        rules.append(("Step5a: no rule applied", new_word))
    return new_word, rules

def step5b(word):
    rules = []
    new_word = word
    if measure(word) > 1 and ends_with_double_consonant(word) and word.endswith('l'):
        new_word = word[:-1]
        rules.append(("Step5b: removed last 'l' because double", new_word))
    else:
        rules.append(("Step5b: no rule applied", new_word))
    return new_word, rules

# ---------------------
# Full verbose stemmer
# ---------------------
def porter_stem_verbose(word):
    transformations = [(word, "Original", word)]
    for step_func in [step1a, step1b, step1b_helper, step1c, step2, step3, step4, step5a, step5b]:
        new_word, rules = step_func(word)
        for rule_desc, after_word in rules:
            transformations.append((word, after_word, rule_desc))
        # FIX: Update `word` only once per step, after collecting rules
        word = new_word
    transformations.append((word, word, "Final Stem"))
    return word, transformations

# ---------------------
# Streamlit UI
# ---------------------
# ---------------------
# Streamlit UI (color-coded)
# ---------------------
user_text = st.text_area("Enter word/words/text to stem:")

if st.button("Stem Text (All Rules)"):
    if not user_text.strip():
        st.warning("Please enter some text.")
    else:
        words = [w for w in word_tokenize(user_text) if re.search('[a-zA-Z]', w)]
        st.subheader("Tokenized Words")
        st.write(words)

        for word in words:
            final_stem, transformations = porter_stem_verbose(word.lower())

            # 1. Show word and final stem first
            st.markdown(
                f"""
                <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 0.5em;">
                    Word: <span style="color:#1f2937;">{word}</span><br>
                    Final Stem: <span style="color:green;">{final_stem}</span>
                </div>
                <hr>
                """,
                unsafe_allow_html=True
)


            # 2. Step-by-step flow
            st.markdown("### Step-by-step Flow (All Rules Shown)")
            for before, after, rule in transformations[1:-1]:  # exclude Original & Final Stem labels
                if before != after:
                    st.markdown(
                        f"<span style='color:green; font-weight:bold;'>{before} → {after}</span> "
                        f"<span style='color:#008000;'>{rule}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<span style='color:gray;'>{after} ({rule})</span>",
                        unsafe_allow_html=True
                    )

            # 3. Final stem (highlighted)
            st.markdown(f"**Final Stem:** <span style='color:green; font-weight:bold;'>{final_stem}</span>", unsafe_allow_html=True)
            st.markdown("---")
