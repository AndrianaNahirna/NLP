import re
import json
import os

class RuleBasedExtractor:
    def __init__(self, resources_path='sentiment/resources'):
        with open(os.path.join(resources_path, 'months_ua.json'), 'r', encoding='utf-8') as f:
            self.months = json.load(f)
        with open(os.path.join(resources_path, 'currencies.json'), 'r', encoding='utf-8') as f:
            self.currencies = json.load(f)
        with open(os.path.join(resources_path, 'locations.json'), 'r', encoding='utf-8') as f:
            self.locations = json.load(f)

    def extract_dates(self, text):
        results = []
        for match in re.finditer(r'\b([0-3]?\d)\.([0-1]?\d)\.(20\d{2}|19\d{2}|\d{2})\b', text):
            d, m, y = match.groups()
            y = "20" + y if len(y) == 2 else y
            if 1 <= int(m) <= 12 and 1 <= int(d) <= 31:
                results.append({"field_type": "DATE", "value": f"{y}-{int(m):02d}-{int(d):02d}", 
                                "start_char": match.start(), "end_char": match.end(), "method": "regex_numeric_date"})
        
        month_keys = "|".join(self.months.keys())
        pattern2 = fr'\b([0-3]?\d)\s+({month_keys})\s+(20\d{{2}})\b'
        for match in re.finditer(pattern2, text, re.IGNORECASE):
            d, m_str, y = match.groups()
            m = self.months.get(m_str.lower())
            if m and 1 <= int(d) <= 31:
                results.append({"field_type": "DATE", "value": f"{y}-{m}-{int(d):02d}", 
                                "start_char": match.start(), "end_char": match.end(), "method": "regex_text_date"})
        return results

    def extract_amounts(self, text):
        results = []
        curr_keys = "|".join(re.escape(k) for k in self.currencies.keys())
        pattern = fr'\b(\d+([.,]\d{{1,2}})?)\s*({curr_keys})\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val_str = match.group(1).replace(',', '.')
            curr = self.currencies.get(match.group(3).lower(), "UNKNOWN")
            results.append({"field_type": "AMOUNT", "value": f"{float(val_str)} {curr}", 
                            "start_char": match.start(), "end_char": match.end(), "method": "regex_currency"})
        return results

    def extract_locations(self, text):
        results = []
        loc_keys = "|".join(self.locations.keys())
        pattern = fr'(?i)\b({loc_keys})\b'
        for match in re.finditer(pattern, text):
            val = self.locations.get(match.group(1).lower())
            results.append({"field_type": "LOCATION", "value": val, 
                            "start_char": match.start(), "end_char": match.end(), "method": "dict_location_ua"})
        return results

    def extract_all(self, text):
        return self.extract_dates(text) + self.extract_amounts(text) + self.extract_locations(text)