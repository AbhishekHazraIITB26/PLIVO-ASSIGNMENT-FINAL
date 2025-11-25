import json
import random
import os

# --- Constants & Lists ---

# NEW: Updated First Names
FIRST_NAMES = [
    "arman", "zara", "vihaan", "kavya", "ishan", "sana", "reyansh", "diya", 
    "advait", "meher", "kabir", "aanya", "arush", "pari", "devansh", "khushi", 
    "samarth", "navya", "yuvraj", "ruhi", "dhairya", "avni", "hridaan", "prisha", 
    "vaibhav", "siya", "moksh", "anika", "shaurya", "myra", "darsh", "aadhya", "viraj"
]

# NEW: Updated Last Names
LAST_NAMES = [
    "malhotra", "saxena", "bhatia", "chopra", "deshmukh", "gowda", "nayak", 
    "das", "mukherjee", "shetty", "pawar", "jain", "kaur", "seth", "lal", 
    "biswas", "sinha", "bhatt", "pandey", "khanna", "mishra"
]

# NEW: Updated Cities (Tier 2/Tier 3 mix)
CITIES = [
    "bhopal", "patna", "vadodara", "ludhiana", "agra", "nashik", "faridabad", 
    "meerut", "rajkot", "varanasi", "srinagar", "aurangabad", "dhanbad", 
    "amritsar", "allahabad", "ranchi", "howrah", "jabalpur", "gwalior", "vijayawada"
]

# SHUFFLED: Locations
LOCATIONS = [
    "banjara hills", "powai", "whitefield", "hitech city", "electronic city", 
    "mall road", "outer ring road", "velachery", "bkc", "indiranagar", 
    "salt lake", "koramangala", "old airport road", "mg road"
]

# SHUFFLED: Domains
DOMAINS = ["protonmail", "outlook", "gmail", "rediffmail", "yahoo", "hotmail"]

# SHUFFLED: TLDs
TLDS = ["co", "org", "com", "in", "co.in"]

# SHUFFLED: Months
MONTHS = [
    "august", "december", "january", "july", "november", "september", 
    "february", "april", "october", "june", "march", "may"
]

DIGIT_MAP = {
    '0': ['zero', 'oh', '0'], '1': ['one', '1'], '2': ['two', '2'], '3': ['three', '3'], 
    '4': ['four', '4'], '5': ['five', '5'], '6': ['six', '6'], '7': ['seven', '7'], 
    '8': ['eight', '8'], '9': ['nine', '9']
}

# --- Helper Functions ---

def get_noisy_digit_string(number_str):
    """
    Converts '123' to 'one two 3' or 'double two'.
    mimics stress.jsonl heavy noise.
    """
    res = []
    i = 0
    while i < len(number_str):
        char = number_str[i]
        
        # Check for "double" opportunity (e.g., 88 -> double eight)
        if i < len(number_str) - 1 and number_str[i+1] == char and random.random() < 0.4:
            val = random.choice(DIGIT_MAP[char])
            # Only use "double" with words ("double eight", not "double 8")
            if val.isalpha(): 
                res.append(f"double {val}")
                i += 2
                continue

        if char in DIGIT_MAP:
            # 70% chance to spell it out (Stress set is very noisy)
            if random.random() < 0.7:
                res.append(random.choice(DIGIT_MAP[char]))
            else:
                res.append(char)
        else:
            res.append(char)
        i += 1
        
    return " ".join(res)

def generate_phone():
    # 10 digits
    digits = "".join([str(random.randint(0, 9)) for _ in range(10)])
    # Stress set has fully spelled out phones often
    return get_noisy_digit_string(digits)

def generate_card():
    # Stress set patterns:
    # 1. 6522-0922... (Dashed)
    # 2. three five seven... (Fully spelled)
    # 3. 5315-6485...
    digits = "".join([str(random.randint(0, 9)) for _ in range(16)])
    
    r = random.random()
    if r < 0.4:
        # Dashed format like "6522-0922 8152 0012"
        raw = f"{digits[:4]}-{digits[4:8]} {digits[8:12]} {digits[12:]}"
        # Often these remain numeric in stress set
        return raw
    elif r < 0.7:
        # Fully Spelled out
        return get_noisy_digit_string(digits)
    else:
        # Spaced
        raw = f"{digits[:4]} {digits[4:8]} {digits[8:12]} {digits[12:]}"
        return get_noisy_digit_string(raw)

def generate_email(name):
    clean_name = name.replace(" ", ".").lower()
    domain = random.choice(DOMAINS)
    tld = random.choice(TLDS)
    
    # Stress set feature: spaced out domains like "h o t m a i l" or "p r o t o n..."
    if random.random() < 0.4:
        domain = " ".join(list(domain))
    
    at_char = random.choice([" at ", "@"])
    dot_char = random.choice([" dot ", "."])
    
    return f"{clean_name}{at_char}{domain}{dot_char}{tld}"

def generate_date():
    day = random.randint(1, 30)
    year = random.randint(2023, 2026)
    month = random.choice(MONTHS)
    
    # "15 of may 2026", "23rd april 2026", "14th november"
    r = random.random()
    if r < 0.4:
        return f"{day} of {month} {year}"
    elif r < 0.7:
        suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
        return f"{day}{suffix} {month} {year}"
    else:
        return f"{day:02d}/{random.randint(1,12):02d}/{year}"

def generate_example(id_num):
    # Templates mimicking stress.jsonl specifically
    templates = [
        "hinglish_intro",  # "haan so my naam is..."
        "stress_pii",      # "uh actually my old card..."
        "negative_order",  # "regarding order id..."
        "standard_intro"   # "this is X from Y..."
    ]
    
    # Weights to favor stress patterns heavily for training
    template = random.choices(templates, weights=[0.3, 0.4, 0.15, 0.15])[0]
    
    text_parts = []
    entities = []
    
    def add_text(s):
        text_parts.append(s)
    def add_entity(content, label):
        start = len("".join(text_parts))
        text_parts.append(content)
        end = len("".join(text_parts))
        entities.append({"start": start, "end": end, "label": label})

    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    city = random.choice(CITIES)
    
    if template == "hinglish_intro":
        # pattern: "haan so my naam is X and main rehte in Y we will meet on Z"
        add_text("haan so my naam is ")
        add_entity(name, "PERSON_NAME")
        add_text(" and main rehte in ")
        add_entity(city, "CITY")
        add_text(" we will meet on ")
        add_entity(generate_date(), "DATE")
        
    elif template == "stress_pii":
        # pattern: "uh actually my old card number maybe is X i am not sure and my new phone is Y also send email to Z please"
        add_text("uh actually my old card number maybe is ")
        add_entity(generate_card(), "CREDIT_CARD")
        add_text(" i am not sure and my new phone is ")
        add_entity(generate_phone(), "PHONE")
        add_text(" also send email to ")
        add_entity(generate_email(name), "EMAIL")
        add_text(" please")
        
    elif template == "negative_order":
        # pattern: "this is regarding order id X and i checked it two three times already"
        order_id = "".join([str(random.randint(0,9)) for _ in range(6)])
        add_text(f"this is regarding order id {order_id} and i checked it two three times already")
        
    elif template == "standard_intro":
        add_text("this is ")
        add_entity(name, "PERSON_NAME")
        add_text(f" from {city} my phone is ")
        add_entity(generate_phone(), "PHONE")
        add_text(" please call me tomorrow")

    return {
        "id": f"utt_{id_num:04d}",
        "text": "".join(text_parts),
        "entities": entities
    }

def main():
    # Increase training size slightly to ensure patterns are learned
    if not os.path.exists("data"):
        os.makedirs("data")

    with open("data/train.jsonl", "w", encoding="utf-8") as f:
        for i in range(1500):
            f.write(json.dumps(generate_example(i)) + "\n")
            
    with open("data/dev.jsonl", "w", encoding="utf-8") as f:
        for i in range(200):
            f.write(json.dumps(generate_example(i)) + "\n")

    print("Generated data/train.jsonl (1500 lines) and data/dev.jsonl (200 lines)")

if __name__ == "__main__":
    main()