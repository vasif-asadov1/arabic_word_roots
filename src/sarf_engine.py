class SarfEngine:
    def __init__(self):
        # --- GEÇMİŞ ZAMAN (MADI) EKLERİ ---
        self.past_suffixes = {
            "O [E] (Hüve)": "َ", "O İkisi [E] (Hüma)": "َا", "Onlar [E] (Hüm)": "ُوا",
            "O [K] (Hiye)": "َتْ", "O İkisi [K] (Hüma)": "َتَا", "Onlar [K] (Hünne)": "ْنَ",
            "Sen [E] (Ente)": "ْتَ", "Siz İkiniz [E/K] (Entüma)": "ْتُمَا", "Siz [E] (Entüm)": "ْتُمْ",
            "Sen [K] (Enti)": "ْتِ", "Siz [K] (Entünne)": "ْتُنَّ",
            "Ben (Ene)": "ْتُ", "Biz (Nahnü)": "ْنَا"
        }

        # --- ŞİMDİKİ ZAMAN (MUDARI) EKLERİ (Önek, Sonek) ---
        self.present_affixes = {
            "O [E] (Hüve)": ("يَ", "ُ"),
            "O İkisi [E] (Hüma)": ("يَ", "َانِ"),
            "Onlar [E] (Hüm)": ("يَ", "ُونَ"),
            
            "O [K] (Hiye)": ("تَ", "ُ"),
            "O İkisi [K] (Hüma)": ("تَ", "َانِ"),
            "Onlar [K] (Hünne)": ("يَ", "ْنَ"),
            
            "Sen [E] (Ente)": ("تَ", "ُ"),
            "Siz İkiniz [E/K] (Entüma)": ("تَ", "َانِ"),
            "Siz [E] (Entüm)": ("تَ", "ُونَ"),
            
            "Sen [K] (Enti)": ("تَ", "ِينَ"),
            "Siz [K] (Entünne)": ("تَ", "ْنَ"),
            
            "Ben (Ene)": ("أَ", "ُ"),
            "Biz (Nahnü)": ("نَ", "ُ")
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
    
    print(f"--- Şimdiki Zaman Testi: {test_root} ---")
    for zamir in engine.present_affixes.keys():
        result = engine.conjugate_present_tense(test_root, zamir)
        print(f"{zamir.ljust(30)} : {result}")