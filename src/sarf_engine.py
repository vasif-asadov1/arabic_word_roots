class SarfEngine:
    def __init__(self):
        # --- PAST TENSE SUFFIXES ---
        self.past_suffixes = {
            "He (Huwa)": "َ", "They Two [M] (Huma)": "َا", "They [M] (Hum)": "ُوا",
            "She (Hiya)": "َتْ", "They Two [F] (Huma)": "َتَا", "They [F] (Hunna)": "ْنَ",
            "You [M] (Anta)": "ْتَ", "You Two [M/F] (Antuma)": "ْتُمَا", "You All [M] (Antum)": "ْتُمْ",
            "You [F] (Anti)": "ْتِ", "You All [F] (Antunna)": "ْتُنَّ",
            "I (Ana)": "ْتُ", "We (Nahnu)": "ْنَا"
        }

        # --- PRESENT TENSE AFFIXES (Prefix, Suffix) ---
        self.present_affixes = {
            "He (Huwa)": ("يَ", "ُ"),
            "They Two [M] (Huma)": ("يَ", "َانِ"),
            "They [M] (Hum)": ("يَ", "ُونَ"),
            
            "She (Hiya)": ("تَ", "ُ"),
            "They Two [F] (Huma)": ("تَ", "َانِ"),
            "They [F] (Hunna)": ("يَ", "ْنَ"),
            
            "You [M] (Anta)": ("تَ", "ُ"),
            "You Two [M/F] (Antuma)": ("تَ", "َانِ"),
            "You All [M] (Antum)": ("تَ", "ُونَ"),
            
            "You [F] (Anti)": ("تَ", "ِينَ"),
            "You All [F] (Antunna)": ("تَ", "ْنَ"),
            
            "I (Ana)": ("أَ", "ُ"),
            "We (Nahnu)": ("نَ", "ُ")
        }

    def conjugate_past_tense(self, root_string, zamir):
        letters = root_string.split(" ")
        if len(letters) != 3: return "Error"
        L1, L2, L3 = letters[0], letters[1], letters[2]
        suffix = self.past_suffixes.get(zamir, "")
        return f"{L1}َ{L2}َ{L3}{suffix}"

    def conjugate_present_tense(self, root_string, zamir):
        letters = root_string.split(" ")
        if len(letters) != 3: return "Error"
        L1, L2, L3 = letters[0], letters[1], letters[2]
        
        prefix, suffix = self.present_affixes.get(zamir, ("", ""))
        
        # Math: Prefix + L1(Sukun) + L2(Damma) + L3 + Suffix
        return f"{prefix}{L1}ْ{L2}ُ{L3}{suffix}"

    def conjugate_future_tense(self, root_string, zamir):
        # The Future is just the Present tense with "سَـ" (Sa-) attached!
        present_word = self.conjugate_present_tense(root_string, zamir)
        if present_word == "Error": return "Error"
        return f"سَ{present_word}"

if __name__ == "__main__":
    engine = SarfEngine()
    test_root = "ك ت ب"
    
    print(f"--- Testing Present Tense for root: {test_root} ---")
    for zamir in engine.present_affixes.keys():
        result = engine.conjugate_present_tense(test_root, zamir)
        print(f"{zamir.ljust(25)} : {result}")
        
    print(f"\n--- Testing Future Tense for root: {test_root} ---")
    for zamir in engine.present_affixes.keys():
        result = engine.conjugate_future_tense(test_root, zamir)
        print(f"{zamir.ljust(25)} : {result}")