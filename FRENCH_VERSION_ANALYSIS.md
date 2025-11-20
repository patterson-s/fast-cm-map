# French Version Implementation Analysis
## FAST Conflict Forecasts - Internationalization Strategy

---

## Executive Summary

This document provides a comprehensive analysis of how to create a French version of the FAST Conflict Forecasts application. The application is a Plotly Dash web app that visualizes conflict forecasting data. Creating a French version requires translating both UI elements (in Python code) and dynamic content (in JSON data), totaling approximately **200+ distinct text elements** across multiple layers.

---

## 1. Application Architecture Overview

### 1.1 Technology Stack
- **Framework**: Plotly Dash (Python web framework)
- **Data**: 4.1MB JSON file with 201 country forecasts
- **Visualization**: Plotly choropleth maps and charts
- **Deployment**: Gunicorn on Render platform
- **State Management**: URL-based routing (RESTful)

### 1.2 Data Flow Architecture

```
User Browser
    ↓
app.py (Entry point, port 8050)
    ↓
callbacks.py (URL routing)
    ↓
    ├─→ "/" → layout.py::create_landing_page()
    │           ↓
    │       Main map with controls
    │
    └─→ "/country/{CODE}/{month}-{year}" → layout.py::create_detail_page()
                ↓
        ┌───────┴────────┬──────────────┬─────────────┐
        ↓                ↓              ↓             ↓
    Summary Text   temporal_viz    covariate_viz   symlog_viz
    (from JSON)    (time series)   (risk factors)  (scatter plot)
```

### 1.3 Key Files
- **app.py** (31 lines) - Entry point
- **layout.py** (400 lines) - UI layout, page generation
- **callbacks.py** (113 lines) - Routing and interactivity
- **data_loader.py** (105 lines) - Data access layer
- **temporal_viz.py** (100 lines) - Historical trends chart
- **covariate_viz.py** (65 lines) - Risk factors chart
- **symlog_viz.py** (92 lines) - Regional comparison chart
- **data/forecast_data.json** (4.1MB) - All forecast data

---

## 2. Text Content Inventory

### 2.1 Static UI Text (in Python Code)

All UI text is hardcoded in Python files and needs translation:

#### **layout.py** (Primary UI strings)

**Landing Page:**
- Main heading: `"FAST Conflict Forecasts"`
- Subtitle: `"Click on a country to view detailed forecasts"`
- Link: `"Feature Requests"`
- Control labels:
  - `"Forecast period:"`
  - `"Fatality scale:"`
  - `"Absolute"`
  - `"Log"`
- Map legend:
  - `"Predicted fatalities"`
  - `"log(1 + predicted fatalities)"`
- Hover template: `"Predicted fatalities: %{customdata:.1f}"`
- Dropdown placeholder: `"Select forecast period"`

**Detail Page:**
- Navigation: `"← Back to map"`
- Section headings:
  - `"Summary"`
  - `"Historical conflict trends"`
  - `"Structural risk factors"`
  - `"Comparable cases"`
- Error messages:
  - `"Data not available"`
  - `"No forecast data is available for the selected country and date."`

**Month Names:**
```python
get_month_name(month) -> {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
```

#### **temporal_viz.py** (Chart labels)
- Legend labels:
  - `"Historical (all months)"`
  - `"6-Month Rolling Average"`
  - `"Forecast"`
  - `f"Target ({get_month_name(target_month)})"`
- Chart titles:
  - `f"{country_name} - Complete Monthly Fatalities"`
- Axis labels:
  - `"Fatalities"`

#### **covariate_viz.py** (Risk factor labels)
- Covariate labels:
  ```python
  {
      'infant_mortality': 'Infant Mortality Rate',
      'military_power': 'Military Executive Power'
  }
  ```
- Chart title: `f"{country_name} - Structural Risk Factors"`
- Axis labels:
  - `"Percentile"`
- Hover template: `"Percentile: %{x:.0f}%"`
- Error message: `"No covariate data available"`

#### **symlog_viz.py** (Regional comparison labels)
- Risk categories (as legend labels):
  - `"Near-certain no conflict"` → Color: light blue
  - `"Improbable conflict"` → Color: yellow
  - `"Probable conflict"` → Color: orange
  - `"Near-certain conflict"` → Color: red
- Chart title: `f"Regional Conflict Forecast Distribution - {get_month_name(month)} {year}"`
- Axis labels:
  - `"Probability of ≥25 Fatalities"`
  - `"Predicted Fatalities"`
- Legend label: `f"{country_name} (target)"`
- Hover template: `"Probability: %{x:.3f}<br>Predicted: %{y:.1f}"`

#### **app.py** (Meta information)
- App title: `"FAST Conflict Forecasts"` (appears in browser tab)

**Total Static UI Strings: ~60 unique text elements**

---

### 2.2 Dynamic Content (in JSON Data)

#### **forecast_data.json Structure**

Each of the 201 forecasts contains:

```json
{
  "country_code": "SOM",
  "country_name": "Somalia",  // ← Needs translation
  "month": 12,
  "year": 2025,
  "bluf": "In December 2025, Somalia has...",  // ← Needs translation (200-400 chars)
  "forecast": {
    "risk_category": "Near-certain conflict",  // ← Needs translation
    "intensity_category": "101-1,000"  // ← Needs translation
  },
  "regional_context": [
    {
      "country_name": "Sudan"  // ← Needs translation
    }
  ],
  "cohort": [
    {
      "country_name": "Syria"  // ← Needs translation
    }
  ]
}
```

#### **Text Fields Requiring Translation:**

1. **Country Names** (~67 unique countries, appears 3 times per forecast)
   - `forecast.country_name`
   - `forecast.regional_context[].country_name`
   - `forecast.cohort[].country_name`
   - **Volume**: ~67 unique names × 3 occurrences = ~201 instances

2. **BLUF Summaries** (201 unique texts)
   - `forecast.bluf`
   - **Characteristics**:
     - Length: 200-400 characters
     - Format: Structured paragraph with specific data points
     - Content: Country-specific analysis with embedded statistics
   - **Example**:
     ```
     "In December 2025, Somalia has a 100% probability of experiencing
     at least 25 battle deaths, with a forecast of 154.6 battle deaths
     on average. This puts Somalia in the category of Near-certain
     conflict, comparable to countries like Syria and Sudan..."
     ```
   - **Translation Challenge**: Must preserve:
     - Numbers/statistics (don't translate)
     - Country names (translate consistently)
     - Risk category phrases (translate consistently)
     - Natural paragraph flow in French

3. **Risk Categories** (4 unique values, appears 201 times)
   - `forecast.forecast.risk_category`
   - Values:
     - `"Near-certain no conflict"` → "Aucun conflit quasi-certain"
     - `"Improbable conflict"` → "Conflit improbable"
     - `"Probable conflict"` → "Conflit probable"
     - `"Near-certain conflict"` → "Conflit quasi-certain"

4. **Intensity Categories** (5 unique values, appears 201 times)
   - `forecast.forecast.intensity_category`
   - Values:
     - `"0"` → "0" (no translation needed)
     - `"1-25"` → "1-25" (no translation needed)
     - `"26-100"` → "26-100" (no translation needed)
     - `"101-1,000"` → "101-1 000" (French number formatting)
     - `"1,001+"` → "1 001+" (French number formatting)

**Total Dynamic Content:**
- 201 BLUF summaries (major translation effort)
- ~67 unique country names (repeated ~603 times across all forecasts)
- 4 risk categories (repeated 201 times)
- 5 intensity categories (repeated 201 times)

---

## 3. Translation Strategy & Implementation Plan

### 3.1 Two-Track Approach

The French version requires translating content in **two separate locations**:

#### **Track 1: Static UI Translations (Code)**
- Location: Python files (`.py`)
- Method: Create translated versions or use i18n system
- Volume: ~60 text strings
- Complexity: Low to Medium

#### **Track 2: Dynamic Content Translations (Data)**
- Location: JSON data file
- Method: Create translated JSON or hybrid system
- Volume: 201 BLUFs + 800+ data labels
- Complexity: High (especially BLUF summaries)

---

### 3.2 Recommended Architecture: Dual Data Files

**Option A: Separate French Data File** (Recommended)

```
data/
  ├── forecast_data.json          # Original English
  └── forecast_data_fr.json       # French version
```

**Pros:**
- Clean separation of concerns
- No performance overhead
- Easy to maintain and update
- Supports URL-based language switching
- Can deploy monolingual versions

**Cons:**
- Data duplication
- Need to keep both files in sync
- Larger repository size

**Implementation:**
1. Create translation pipeline for JSON data
2. Modify `data_loader.py` to accept language parameter
3. Load appropriate file based on language selection
4. Update UI strings in Python code

---

### 3.3 Detailed Implementation Steps

#### **Phase 1: Data Translation Pipeline**

```
English JSON → Translation API → French JSON
```

**Step 1.1: Extract Translatable Content**
```python
# Script: extract_translatable_content.py
# Output: translations_needed.json

{
  "country_names": {
    "Somalia": null,
    "Yemen": null,
    ...
  },
  "risk_categories": {
    "Near-certain conflict": null,
    "Probable conflict": null,
    ...
  },
  "bluf_texts": [
    {
      "key": "SOM_12_2025",
      "text": "In December 2025, Somalia has...",
      "translation": null
    },
    ...
  ]
}
```

**Step 1.2: Translate via Cohere API**
```python
# Script: translate_content.py
# Input: translations_needed.json
# Output: translations_completed.json

for item in translatable_content:
    # Black box: Cohere Translate API call
    translation = cohere_translate(
        text=item['text'],
        source_lang='en',
        target_lang='fr'
    )
    item['translation'] = translation
```

**Special Handling for BLUF Texts:**
- Pre-process: Mark country names, numbers, dates as "do not translate"
- Post-process: Ensure consistent terminology across all 201 summaries
- Quality check: Verify French grammar and flow

**Step 1.3: Generate French JSON**
```python
# Script: generate_french_json.py
# Input: forecast_data.json + translations_completed.json
# Output: forecast_data_fr.json

# Replace all translatable fields with French versions
# Preserve all numeric data, dates, and structure
```

#### **Phase 2: Code Modifications**

**Step 2.1: Create Translation Dictionary for UI**
```python
# File: translations.py

UI_STRINGS = {
    'en': {
        'app_title': 'FAST Conflict Forecasts',
        'click_country': 'Click on a country to view detailed forecasts',
        'forecast_period': 'Forecast period:',
        'fatality_scale': 'Fatality scale:',
        'absolute': 'Absolute',
        'log': 'Log',
        'back_to_map': '← Back to map',
        'summary': 'Summary',
        'historical_trends': 'Historical conflict trends',
        'risk_factors': 'Structural risk factors',
        'comparable_cases': 'Comparable cases',
        'predicted_fatalities': 'Predicted fatalities',
        'log_predicted': 'log(1 + predicted fatalities)',
        'fatalities': 'Fatalities',
        'percentile': 'Percentile',
        'probability_label': 'Probability of ≥25 Fatalities',
        'months': {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
    },
    'fr': {
        'app_title': 'Prévisions de conflits FAST',
        'click_country': 'Cliquez sur un pays pour voir les prévisions détaillées',
        'forecast_period': 'Période de prévision :',
        'fatality_scale': 'Échelle de fatalités :',
        'absolute': 'Absolue',
        'log': 'Logarithmique',
        'back_to_map': '← Retour à la carte',
        'summary': 'Résumé',
        'historical_trends': 'Tendances historiques des conflits',
        'risk_factors': 'Facteurs de risque structurels',
        'comparable_cases': 'Cas comparables',
        'predicted_fatalities': 'Fatalités prévues',
        'log_predicted': 'log(1 + fatalités prévues)',
        'fatalities': 'Fatalités',
        'percentile': 'Centile',
        'probability_label': 'Probabilité de ≥25 fatalités',
        'months': {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
    }
}

def get_text(key, lang='en'):
    """Get translated text for given key and language."""
    return UI_STRINGS[lang].get(key, UI_STRINGS['en'][key])

def get_month_name(month, lang='en'):
    """Get month name in specified language."""
    return UI_STRINGS[lang]['months'].get(month, str(month))
```

**Step 2.2: Modify data_loader.py**
```python
# File: data_loader.py

class ForecastDataLoader:
    def __init__(self, language='en'):
        self.language = language

        # Load appropriate data file
        if language == 'fr':
            data_path = 'data/forecast_data_fr.json'
        else:
            data_path = 'data/forecast_data.json'

        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # ... rest of initialization

# Modify singleton
_loader_instances = {}

def get_loader(language='en'):
    """Get or create data loader for specified language."""
    if language not in _loader_instances:
        _loader_instances[language] = ForecastDataLoader(language)
    return _loader_instances[language]
```

**Step 2.3: Update layout.py**
```python
# File: layout.py

# Add language parameter to all functions
def create_landing_page(language='en'):
    loader = get_loader(language)
    # ... existing code ...

    return html.Div([
        html.H1(
            get_text('app_title', language),
            style={"textAlign": "center", "marginTop": "20px"},
        ),
        html.P(
            get_text('click_country', language),
            style={"textAlign": "center", "color": "#666"},
        ),
        # ... update all text strings with get_text() calls
    ])

def create_detail_page(country_code, month, year, language='en'):
    loader = get_loader(language)
    # ... update all text strings with get_text() calls
```

**Step 2.4: Update visualization files**
```python
# Files: temporal_viz.py, covariate_viz.py, symlog_viz.py

# Add language parameter to all chart creation functions
def create_temporal_chart(forecast, language='en'):
    # ... existing code ...

    fig.add_trace(go.Scatter(
        # ...
        name=get_text('historical_all_months', language),
        # ...
    ))

    fig.update_layout(
        # ...
        yaxis_title=get_text('fatalities', language),
        # ...
    )
```

**Step 2.5: Add Language Selector to UI**
```python
# File: layout.py (in create_landing_page)

html.Div([
    dcc.RadioItems(
        id='language-selector',
        options=[
            {'label': 'English', 'value': 'en'},
            {'label': 'Français', 'value': 'fr'}
        ],
        value='en',
        inline=True,
        labelStyle={'marginRight': '15px'}
    )
], style={'textAlign': 'center', 'marginTop': '10px'})
```

**Step 2.6: Update callbacks.py**
```python
# File: callbacks.py

# Add language detection to URL routing
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('language-selector', 'value')
)
def display_page(pathname, language='en'):
    if pathname == '/':
        return create_landing_page(language)
    elif pathname.startswith('/country/'):
        # Parse URL
        parts = pathname.split('/')
        country_code = parts[2]
        month_year = parts[3].split('-')
        month = int(month_year[0])
        year = int(month_year[1])
        return create_detail_page(country_code, month, year, language)
```

---

### 3.4 Alternative Architecture: URL-Based Language Selection

Instead of UI selector, use URL routing:
- English: `https://app.com/` or `https://app.com/en/`
- French: `https://app.com/fr/`

**Pros:**
- Shareable French links
- SEO-friendly
- Can deploy separate domains (e.g., `app.fr`)
- No UI clutter

**Implementation:**
```python
# callbacks.py
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # Extract language from URL
    if pathname.startswith('/fr'):
        language = 'fr'
        pathname = pathname[3:]  # Remove /fr prefix
    else:
        language = 'en'

    # Route to appropriate page with language
    # ...
```

---

## 4. Translation Workflow with Cohere API

### 4.1 Translation Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Content Extraction                                 │
│  Script: extract_translatable_content.py                    │
│  Input:  data/forecast_data.json + *.py files              │
│  Output: translation_input.json                             │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Translation                                        │
│  Script: translate_with_cohere.py                          │
│  Input:  translation_input.json                             │
│  API:    Cohere Translate (BLACK BOX)                       │
│  Output: translation_output.json                            │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Quality Validation                                 │
│  Script: validate_translations.py                           │
│  Checks: Terminology consistency, number preservation       │
│  Output: validated_translations.json                        │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Content Assembly                                   │
│  Script: generate_french_files.py                          │
│  Input:  validated_translations.json                        │
│  Output: data/forecast_data_fr.json + translations.py      │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Cohere API Integration Points

**API Call Structure (Black Box):**
```python
def translate_batch(texts, source_lang='en', target_lang='fr'):
    """
    Black box translation function using Cohere API.

    Args:
        texts: List of strings to translate
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        List of translated strings
    """
    # Black box implementation
    # Handles: API authentication, rate limiting, error handling
    translations = cohere_translate_api(texts, source_lang, target_lang)
    return translations
```

**Translation Requirements:**
1. **Country Names**: Simple noun translation
   - Input: "Somalia", "Yemen", "Democratic Republic of the Congo"
   - Expected: "Somalie", "Yémen", "République démocratique du Congo"

2. **Risk Categories**: Fixed terminology (create glossary)
   - Must be consistent across all 201 forecasts
   - Use same French term every time

3. **BLUF Paragraphs**: Context-aware translation
   - Preserve: Numbers, percentages, statistics
   - Translate: All narrative text
   - Maintain: Formal analytical tone
   - Example preservation:
     - "154.6 battle deaths" → "154,6 morts au combat"
     - "100% probability" → "100 % de probabilité"
     - "December 2025" → "décembre 2025"

**Batching Strategy:**
- Process BLUFs in batches of 10-20 to maintain consistency
- Process all country names in single batch
- Process risk categories as glossary terms first

---

## 5. Technical Considerations

### 5.1 Character Encoding
- Ensure UTF-8 encoding throughout: `'encoding': 'utf-8'`
- French special characters: é, è, ê, ë, à, â, ù, û, ç, î, ï, ô
- Test with country names containing accents (e.g., "Côte d'Ivoire")

### 5.2 Number Formatting
French uses different number formatting:
- Decimal separator: comma (,) instead of period (.)
- Thousands separator: space instead of comma
- Examples:
  - English: `1,234.56` → French: `1 234,56`
  - English: `100%` → French: `100 %` (space before %)

**Implementation:**
```python
import locale

def format_number_french(number, decimals=1):
    """Format number for French locale."""
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    return locale.format_string(f'%.{decimals}f', number, grouping=True)
```

### 5.3 Date Formatting
- Month names already handled in translation dictionary
- Keep year numbers as-is
- Format: "décembre 2025" (lowercase month in French)

### 5.4 Performance Impact
- **Current**: Single JSON file (~4.1MB) loaded once
- **With French**: Two JSON files (~8.2MB total)
- **Memory**: ~8MB additional RAM (negligible)
- **Load time**: Same (only one file loaded per session)
- **No performance degradation expected**

### 5.5 Maintenance Considerations
- When English data updates, need to:
  1. Re-extract new/changed content
  2. Translate new content only
  3. Merge into French JSON
  4. Validate consistency
- Consider versioning both data files together
- Automated tests to ensure both files have same structure

---

## 6. Testing Strategy

### 6.1 Unit Tests
```python
# test_translations.py

def test_all_ui_strings_translated():
    """Verify all English UI strings have French translations."""
    for key in UI_STRINGS['en'].keys():
        assert key in UI_STRINGS['fr'], f"Missing French translation for: {key}"

def test_month_names():
    """Verify all 12 months translated."""
    assert len(UI_STRINGS['fr']['months']) == 12

def test_data_file_parity():
    """Verify English and French data files have same structure."""
    with open('data/forecast_data.json') as f:
        en_data = json.load(f)
    with open('data/forecast_data_fr.json') as f:
        fr_data = json.load(f)

    assert len(en_data['forecasts']) == len(fr_data['forecasts'])
    assert en_data['metadata']['total_forecasts'] == fr_data['metadata']['total_forecasts']
```

### 6.2 Visual Testing
- Manual review of each page type in French
- Verify text doesn't overflow containers
- Check that French text fits in buttons/labels
- Verify charts render correctly with French labels

### 6.3 Translation Quality Checks
```python
# validate_translations.py

def check_numbers_preserved(original, translated):
    """Ensure all numbers appear in translation."""
    import re
    original_numbers = re.findall(r'\d+\.?\d*', original)
    translated_numbers = re.findall(r'\d+[,.]?\d*', translated)
    assert len(original_numbers) == len(translated_numbers)

def check_risk_category_consistency(french_data):
    """Ensure risk categories use consistent French terms."""
    categories = set()
    for forecast in french_data['forecasts']:
        categories.add(forecast['forecast']['risk_category'])

    assert categories == {
        "Aucun conflit quasi-certain",
        "Conflit improbable",
        "Conflit probable",
        "Conflit quasi-certain"
    }
```

---

## 7. Deployment Options

### Option A: Single Bilingual App
- Deploy one app with language selector
- URL structure: `app.com/?lang=fr`
- Users can switch languages dynamically
- **Pros**: Single deployment, easy updates
- **Cons**: Loads both data files (minimal impact)

### Option B: Separate Deployments
- Deploy two separate instances:
  - `app.com` (English only)
  - `app-fr.com` or `fr.app.com` (French only)
- Each loads only its language data
- **Pros**: Cleaner separation, can customize per region
- **Cons**: Double deployment, more maintenance

### Option C: URL Routing (Recommended)
- Single app, URL-based language selection:
  - `app.com/` or `app.com/en/` → English
  - `app.com/fr/` → French
- Language persists across navigation
- **Pros**: SEO-friendly, shareable links, single deployment
- **Cons**: Slightly more complex routing logic

---

## 8. Estimated Effort

### Translation Volume
| Category | Count | Avg Length | Total Words |
|----------|-------|------------|-------------|
| UI Strings | 60 | 3 words | ~180 words |
| Country Names | 67 | 2 words | ~134 words |
| Risk Categories | 4 | 3 words | ~12 words |
| BLUF Summaries | 201 | 50 words | ~10,050 words |
| Chart Labels | 20 | 3 words | ~60 words |
| **TOTAL** | **352** | - | **~10,436 words** |

### Development Time Estimates
| Phase | Task | Estimated Time |
|-------|------|----------------|
| 1 | Extract translatable content | 4 hours |
| 2 | Set up Cohere API integration | 2 hours |
| 3 | Translate content (API + validation) | 8 hours |
| 4 | Create translations.py | 2 hours |
| 5 | Modify data_loader.py | 2 hours |
| 6 | Update layout.py | 4 hours |
| 7 | Update visualization files | 4 hours |
| 8 | Update callbacks.py | 3 hours |
| 9 | Add language selector | 2 hours |
| 10 | Testing & QA | 8 hours |
| 11 | Documentation | 2 hours |
| **TOTAL** | | **~41 hours** |

*Note: Assumes Cohere API works as expected (black box). Additional time may be needed for API troubleshooting.*

---

## 9. File Structure After Implementation

```
fast-cm-map/
├── app.py                          # Entry point (minimal changes)
├── callbacks.py                    # Updated with language routing
├── layout.py                       # Updated with get_text() calls
├── data_loader.py                  # Updated with language parameter
├── temporal_viz.py                 # Updated with language parameter
├── covariate_viz.py                # Updated with language parameter
├── symlog_viz.py                   # Updated with language parameter
├── translations.py                 # NEW: UI string translations
│
├── data/
│   ├── forecast_data.json          # Original English data
│   └── forecast_data_fr.json       # NEW: French translated data
│
├── scripts/                        # NEW: Translation pipeline
│   ├── extract_translatable_content.py
│   ├── translate_with_cohere.py
│   ├── validate_translations.py
│   └── generate_french_files.py
│
├── tests/                          # NEW: Translation tests
│   ├── test_translations.py
│   └── test_data_parity.py
│
└── docs/
    └── FRENCH_VERSION_ANALYSIS.md  # This document
```

---

## 10. Key Decisions Required

Before implementation, decide on:

1. **Language Selection Method**
   - [ ] UI toggle (radio buttons)
   - [ ] URL routing (`/fr/` prefix)
   - [ ] Subdomain (`fr.app.com`)
   - [ ] Query parameter (`?lang=fr`)

2. **Default Language**
   - [ ] English
   - [ ] French
   - [ ] Browser detection

3. **Data File Strategy**
   - [ ] Separate files (recommended)
   - [ ] Combined file with language keys
   - [ ] Database with language tables

4. **Translation Validation**
   - [ ] Manual review of all BLUFs
   - [ ] Sample review (e.g., 10%)
   - [ ] Automated validation only

5. **Deployment Approach**
   - [ ] Single bilingual app
   - [ ] Separate deployments
   - [ ] URL routing

6. **Number Formatting**
   - [ ] Full French localization (1 234,56)
   - [ ] Keep English format for consistency
   - [ ] Hybrid (translate text, keep number format)

---

## 11. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cohere API translation quality issues | High | Medium | Manual review sample, create glossary for consistency |
| French text longer than English, breaks layout | Medium | High | Test with longest translations, adjust CSS if needed |
| Inconsistent terminology across 201 BLUFs | High | Medium | Use glossary, validate all risk categories match |
| Performance degradation with 2 data files | Low | Low | Only load one file per session, monitor metrics |
| Maintenance burden keeping files in sync | Medium | High | Automate translation pipeline, version files together |
| Character encoding issues | Medium | Low | UTF-8 everywhere, test with special characters early |
| Missing translations cause app crashes | High | Low | Fallback to English, comprehensive unit tests |

---

## 12. Success Criteria

The French version will be considered complete when:

- [x] All 60 UI strings translated and displayed correctly
- [x] All 201 BLUF summaries translated with consistent terminology
- [x] All 67 country names translated across all contexts
- [x] All 4 risk categories use consistent French terms
- [x] Charts and visualizations display French labels correctly
- [x] Month names appear in French throughout the app
- [x] Language selection mechanism works smoothly
- [x] French text fits properly in all UI containers
- [x] Numbers and statistics preserved accurately in translations
- [x] No encoding issues with French special characters
- [x] All tests pass for both English and French versions
- [x] Documentation updated with French version usage

---

## 13. Next Steps

1. **Decision Phase** (1 day)
   - Review this analysis
   - Make key decisions (Section 10)
   - Approve approach

2. **Setup Phase** (1 day)
   - Set up Cohere API access
   - Create translation scripts repository
   - Set up testing framework

3. **Translation Phase** (3-5 days)
   - Extract content
   - Translate via API
   - Validate translations
   - Generate French data file

4. **Development Phase** (3-5 days)
   - Implement code changes
   - Add language selector
   - Update all visualization files

5. **Testing Phase** (2-3 days)
   - Unit tests
   - Visual testing
   - Quality assurance

6. **Deployment Phase** (1 day)
   - Deploy French version
   - Monitor for issues
   - Gather user feedback

**Total Timeline: 2-3 weeks**

---

## Appendix A: Sample Translation Mapping

### UI Strings (Complete List)

```python
TRANSLATION_MAP = {
    # Main heading
    "FAST Conflict Forecasts": "Prévisions de conflits FAST",

    # Landing page
    "Click on a country to view detailed forecasts":
        "Cliquez sur un pays pour voir les prévisions détaillées",
    "Feature Requests": "Demandes de fonctionnalités",
    "Forecast period:": "Période de prévision :",
    "Fatality scale:": "Échelle de fatalités :",
    "Absolute": "Absolue",
    "Log": "Logarithmique",
    "Select forecast period": "Sélectionner la période de prévision",

    # Map
    "Predicted fatalities": "Fatalités prévues",
    "log(1 + predicted fatalities)": "log(1 + fatalités prévues)",

    # Detail page
    "← Back to map": "← Retour à la carte",
    "Summary": "Résumé",
    "Historical conflict trends": "Tendances historiques des conflits",
    "Structural risk factors": "Facteurs de risque structurels",
    "Comparable cases": "Cas comparables",
    "Data not available": "Données non disponibles",
    "No forecast data is available for the selected country and date.":
        "Aucune donnée de prévision n'est disponible pour le pays et la date sélectionnés.",

    # Chart labels
    "Fatalities": "Fatalités",
    "Percentile": "Centile",
    "Probability of ≥25 Fatalities": "Probabilité de ≥25 fatalités",
    "Historical (all months)": "Historique (tous les mois)",
    "6-Month Rolling Average": "Moyenne mobile sur 6 mois",
    "Forecast": "Prévision",
    "Complete Monthly Fatalities": "Fatalités mensuelles complètes",
    "Regional Conflict Forecast Distribution":
        "Distribution régionale des prévisions de conflits",

    # Risk factors
    "Infant Mortality Rate": "Taux de mortalité infantile",
    "Military Executive Power": "Pouvoir exécutif militaire",
    "No covariate data available": "Aucune donnée de covariable disponible",

    # Months
    "January": "janvier", "February": "février", "March": "mars",
    "April": "avril", "May": "mai", "June": "juin",
    "July": "juillet", "August": "août", "September": "septembre",
    "October": "octobre", "November": "novembre", "December": "décembre",

    # Risk categories (must be consistent)
    "Near-certain no conflict": "Aucun conflit quasi-certain",
    "Improbable conflict": "Conflit improbable",
    "Probable conflict": "Conflit probable",
    "Near-certain conflict": "Conflit quasi-certain",
}
```

### Sample Country Names

```python
COUNTRY_NAMES_FR = {
    "Somalia": "Somalie",
    "Yemen": "Yémen",
    "Syria": "Syrie",
    "Sudan": "Soudan",
    "Nigeria": "Nigeria",
    "Congo": "Congo",
    "Democratic Republic of the Congo": "République démocratique du Congo",
    "Ethiopia": "Éthiopie",
    "Mali": "Mali",
    "Burkina Faso": "Burkina Faso",
    "Niger": "Niger",
    "Chad": "Tchad",
    "Cameroon": "Cameroun",
    "Central African Republic": "République centrafricaine",
    "South Sudan": "Soudan du Sud",
    "Mozambique": "Mozambique",
    "Afghanistan": "Afghanistan",
    "Pakistan": "Pakistan",
    "India": "Inde",
    "Myanmar": "Myanmar",
    "Philippines": "Philippines",
    "Iraq": "Irak",
    "Turkey": "Turquie",
    "Israel": "Israël",
    "Palestine": "Palestine",
    "Lebanon": "Liban",
    "Egypt": "Égypte",
    "Libya": "Libye",
    "Tunisia": "Tunisie",
    "Algeria": "Algérie",
    "Morocco": "Maroc",
    "Mauritania": "Mauritanie",
    "Senegal": "Sénégal",
    "Guinea": "Guinée",
    "Ivory Coast": "Côte d'Ivoire",
    "Ghana": "Ghana",
    "Togo": "Togo",
    "Benin": "Bénin",
    "Kenya": "Kenya",
    "Uganda": "Ouganda",
    "Tanzania": "Tanzanie",
    "Rwanda": "Rwanda",
    "Burundi": "Burundi",
    "Angola": "Angola",
    "Zambia": "Zambie",
    "Zimbabwe": "Zimbabwe",
    "South Africa": "Afrique du Sud",
    "Mexico": "Mexique",
    "Colombia": "Colombie",
    "Venezuela": "Venezuela",
    "Brazil": "Brésil",
    "Peru": "Pérou",
    "Ecuador": "Équateur",
    "Bolivia": "Bolivie",
    "Paraguay": "Paraguay",
    "Uruguay": "Uruguay",
    "Argentina": "Argentine",
    "Chile": "Chili",
    # ... (all 67 countries)
}
```

---

## Conclusion

Creating a French version of the FAST Conflict Forecasts application is a **moderately complex** but **highly structured** task. The main challenges are:

1. **Volume**: ~10,400 words to translate, primarily in 201 BLUF summaries
2. **Consistency**: Must maintain consistent terminology across all forecasts
3. **Technical Integration**: Requires modifications across 7 Python files
4. **Data Management**: Need to maintain two large JSON files in sync

The recommended approach is:
- **Dual data files** (separate English and French JSON)
- **URL-based language routing** (`/fr/` prefix)
- **Translation dictionary** for UI strings in Python
- **Cohere API** for bulk translation with validation

With proper planning and the translation pipeline described above, this can be accomplished in **2-3 weeks** of focused development time.

The architecture is designed to be:
- ✅ Maintainable (clear separation of translations)
- ✅ Scalable (easy to add more languages)
- ✅ Performant (no overhead, single file loaded)
- ✅ Testable (comprehensive validation)

**Key Success Factor**: High-quality, consistent translation of the 201 BLUF summaries, which requires careful prompt engineering for the Cohere API and thorough validation.
